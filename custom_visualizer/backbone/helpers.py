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
from pathlib import Path

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

def get_number_scenes():
    init_configs()

    global global_cfg

    dataset = get_dataset(global_cfg.dataset, "test", StepTracker())
    return len(dataset)

def get_ablation_path(override_obj: OptionChanger):
    global global_cfg

    if not os.path.exists("checkpoints/ablations"): # if ablations are not downloaded, load the main model
        print("Ablation folder not found; defaulting to original model.")
        return "checkpoints/re10k.ckpt"

    if override_obj.wo_depth_refine and (not override_obj.wo_cost_volume_refine) and (not override_obj.wo_backbone_cross_attn) and override_obj.use_epipolar_trans and (not override_obj.wo_cost_volume):
        return "checkpoints/ablations/re10k_worefine.ckpt"
    elif override_obj.wo_depth_refine and override_obj.wo_cost_volume_refine and (not override_obj.wo_backbone_cross_attn) and override_obj.use_epipolar_trans and (not override_obj.wo_cost_volume):
        return "checkpoints/ablations/re10k_worefine_wounet.ckpt" 
    elif override_obj.wo_depth_refine and override_obj.wo_cost_volume and (not override_obj.wo_backbone_cross_attn) and override_obj.use_epipolar_trans:
        return "checkpoints/ablations/re10k_worefine_wocv.ckpt"
    elif override_obj.wo_depth_refine and (not override_obj.wo_cost_volume_refine) and override_obj.wo_backbone_cross_attn and override_obj.use_epipolar_trans and (not override_obj.wo_cost_volume):
        return "checkpoints/ablations/re10k_worefine_wobbcrossattn_best.ckpt"
    elif override_obj.wo_depth_refine and (not override_obj.wo_cost_volume_refine) and (not override_obj.wo_backbone_cross_attn) and (not override_obj.use_epipolar_trans) and (not override_obj.wo_cost_volume):
        return "checkpoints/ablations/re10k_worefine_wepitrans.ckpt"
    else:
        return "checkpoints/re10k.ckpt"

def change_config(override_obj : OptionChanger):
    # Change configuration of MVSplat
    global global_cfg
    encoder = global_cfg.model.encoder

    encoder.wo_backbone_cross_attn = override_obj.wo_backbone_cross_attn
    encoder.wo_cost_volume_refine = override_obj.wo_cost_volume_refine
    encoder.wo_depth_refine = override_obj.wo_depth_refine
    encoder.use_epipolar_trans = override_obj.use_epipolar_trans
    encoder.wo_cost_volume = override_obj.wo_cost_volume

    global_cfg.sample_idx = override_obj.sample_idx

    global_cfg.model.encoder = encoder

    global_cfg.info_request = override_obj.info_request

    global_cfg.sample_idx = override_obj.sample_idx

    global_cfg.checkpointing.load = get_ablation_path(override_obj)

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

    opacities = getattr(gaussian, "opacities").squeeze(0).detach().cpu().numpy()
    no_to_select = int(len(opacities) * gaussian_proportion)

    indices = opacities.argsort()[-no_to_select:][::-1]

    return gaussian, indices

def serializable_gaussians(gaussian: Gaussians, indices: List[int]):

    batch = []

    gauss_list = []

    print(f'We have: {len(indices)} Gaussians')

    avg_pos = getattr(gaussian, "means").squeeze(0).detach().cpu().numpy()
    avg_pos = np.mean(avg_pos[indices], axis=0).tolist()

    for idx in indices:
        gaussian_dict = {}

        gaussian_dict['position'] = getattr(gaussian, "means").squeeze(0)[idx, :].detach().cpu().numpy().tolist()
        gaussian_dict['opacity'] = getattr(gaussian, "opacities").squeeze(0)[idx].detach().cpu().numpy().tolist()
        gaussian_dict['scales'] = getattr(gaussian, "scales").squeeze(0)[idx, :].detach().cpu().numpy().tolist()

        rotations = getattr(gaussian, "rotations").squeeze(0)[idx, :]

        # Transform coordinates from xyzw to wxyz
        rotations = torch.Tensor((rotations[3], rotations[0], rotations[1], rotations[2]))
        rotations = rotations.detach().cpu().numpy()
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

def load_all_images():
    init_configs()

    print("Obtaining input images...")

    all_images_list = []

    dataset = get_dataset(global_cfg.dataset, "test", StepTracker())

    count = 0
    print(f'DATASET HAS SIZE: {len(dataset)}')

    for img in dataset:
        img_list = []
        target_img = img['target']['image']
        for img in target_img:
            img_list.append(F.to_pil_image(img))
        all_images_list.append(img_list)
        count += 1

    print("All input images obtained")

    return all_images_list

def get_video(data_dict):
    print("Obtaining video...")

    new_options = OptionChanger(data_dict)

    init_configs()
    change_config(new_options)

    train()

    global global_cfg

    path_to_vid = global_cfg.output_video

    return str(os.path.abspath(path_to_vid))

# if __name__ == "__main__":

    # get_data({'cv_refinement': True, 'depth_refinement': True, 'cross_attention': True, 'epipolar_transformer': True})