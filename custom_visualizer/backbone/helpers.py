import sys
import os

from src.misc.step_tracker import StepTracker

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from scipy.spatial.transform import Rotation

import hydra
from omegaconf import DictConfig
from typing import List
import json
import torch
import pickle
import numpy as np
import torchvision.transforms.functional as F

from custom_visualizer.backbone.OptionChanger import OptionChanger

from src.config import load_typed_root_config
from src.dataset.data_module import DataModule
from src.global_cfg import set_cfg
from src.model.encoder import EncoderCostVolume
from src.model.encoder.common.gaussian_adapter import Gaussians
from src.main import train
from src.dataset.data_module import get_dataset

global_cfg = None
model = None

def change_config(override_obj : OptionChanger):
    # Change configuration of encoder model of MVSplat
    global global_cfg
    encoder = global_cfg.model.encoder

    encoder.wo_backbone_cross_attn = override_obj.wo_backbone_cross_attn
    encoder.wo_cost_volume_refine = override_obj.wo_cost_volume_refine
    encoder.wo_depth_refine = override_obj.wo_depth_refine
    encoder.use_epipolar_trans = override_obj.use_epipolar_trans

    # encoder.d_feature = override_obj.d_feature
    # encoder.costvolume_unet_feat_dim = override_obj.costvolume_unet_feat_dim

    global_cfg.model.encoder = encoder

    global_cfg.info_request = override_obj.info_request
    set_cfg(global_cfg)

## Used to load main configuration file upon calling the function
@hydra.main(
    version_base=None,
    config_path="../../config",
    config_name="main",
)
def init_configs(cfg_dict: DictConfig):

    global global_cfg
    global_cfg = load_typed_root_config(cfg_dict)
    set_cfg(global_cfg)

def obtain_gaussians(gaussian_proportion=0.05):

    train()

    # get gaussians from pickle file
    with open('custom_visualizer/UI/public/gaussians.pkl', 'rb') as f:
        gaussian = pickle.load(f)

    print(f'Keeping only the top {gaussian_proportion * 100}% of the Gaussians in terms of opacity')

    opacities = getattr(gaussian, "opacities").squeeze(0).detach().numpy()
    no_to_select = int(len(opacities) * gaussian_proportion)

    indices = opacities.argsort()[-no_to_select:][::-1]

    return gaussian, indices

def serializable_gaussians(gaussian: Gaussians, indices: List[int]):

    batch = []

    gauss_list = []

    print(f'We have: {len(indices)} Gaussians')

    avg_pos = getattr(gaussian, "means").squeeze(0).detach().numpy()
    avg_pos = np.mean(avg_pos[indices], axis=0).tolist()

    for idx in indices:
        gaussian_dict = {}

        gaussian_dict['position'] = getattr(gaussian, "means").squeeze(0)[idx, :].detach().numpy().tolist()
        gaussian_dict['opacity'] = getattr(gaussian, "opacities").squeeze(0)[idx].detach().numpy().tolist()
        gaussian_dict['scales'] = getattr(gaussian, "scales").squeeze(0)[idx, :].detach().numpy().tolist()

        rotations = getattr(gaussian, "rotations").squeeze(0)[idx, :]

        # Transform coordinates from xyzw to wxyz
        rotations = torch.Tensor((rotations[3], rotations[0], rotations[1], rotations[2]))
        rotations = rotations.detach().numpy()
        euler_angles = Rotation.from_quat(rotations).as_euler('XYZ')
        gaussian_dict['rotation'] = euler_angles.tolist()

        gaussian_dict['avg_pos'] = avg_pos

        gauss_list.append(gaussian_dict)

        # Make batches of 100 Gaussians for more manageable data streaming
        if len(gauss_list) % 100 == 0:
            batch.append(gauss_list)
            gauss_list = []
    
    if gauss_list:
        batch.append(gauss_list)

    print(f'Gaussians obtained')

    return batch

def get_data(data_dict):

    new_options = OptionChanger(data_dict)

    init_configs()
    change_config(new_options)

    print("Obtaining Gaussians...")
    all_gaussians, indices = obtain_gaussians(new_options.proportion_to_keep)
    print("Obtained Gaussians. Converting to UI-compatible format...")
    print("NOTE: this might take a while. Please wait for process to finish.")

    return serializable_gaussians(all_gaussians, indices)

def get_images():
    init_configs()

    print("Obtaining input images...")

    global global_cfg
    dataset = get_dataset(global_cfg.dataset, "test", StepTracker())
    img = next(iter(dataset))
    target_img = img['target']['image']

    img_list = []

    for img in target_img:
        img_list.append(F.to_pil_image(img))
    
    print("Input images obtained")

    return img_list

def get_video(data_dict):
    print("Obtaining video...")

    new_options = OptionChanger(data_dict)

    init_configs()
    change_config(new_options)

    train()

    global global_cfg

    return global_cfg.output_video

if __name__ == "__main__":

    # get_data({'cv_refinement': True, 'depth_refinement': True, 'cross_attention': True, 'epipolar_transformer': True})
    get_images()