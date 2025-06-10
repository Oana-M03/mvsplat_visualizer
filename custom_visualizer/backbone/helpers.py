import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from scipy.spatial.transform import Rotation

from jaxtyping import install_import_hook
from dataclasses import fields
from hydra import compose, initialize
from hydra.utils import call
import hydra
from omegaconf import DictConfig
from typing import List
import json
import torch
import pickle

from custom_visualizer.backbone.OptionChanger import OptionChanger

from src.config import load_typed_root_config
from src.dataset.data_module import DataModule
from src.global_cfg import set_cfg
from src.model.encoder import EncoderCostVolume
from src.model.encoder.common.gaussian_adapter import Gaussians
from src.main import train

global_cfg = None
encoder_cfg = None
options = OptionChanger()
model = None

def change_config(override_obj : OptionChanger):
    # Change configuration of encoder model of MVSplat
    override_dict = override_obj.get_config_override()

    override_list = [f"++{k}={v}" for k, v in override_dict.items()]

    with initialize(version_base=None, config_path='../../config/model/encoder'):
        cfg = compose(config_name="costvolume", overrides=override_list)

        return cfg

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

        gauss_list.append(gaussian_dict)

        # Make batches of 100 Gaussians for more manageable data streaming
        if len(gauss_list) % 100 == 0:
            batch.append(gauss_list)
            gauss_list = []
    
    if gauss_list:
        batch.append(gauss_list)

    print(f'Gaussians obtained')

    return batch

def get_data():

    new_options = OptionChanger()

    init_configs()

    print("Obtaining Gaussians...")
    all_gaussians, indices = obtain_gaussians(new_options.proportion_to_keep)
    print("Obtained Gaussians. Converting to UI-compatible format...")
    print("NOTE: this might take a while. Please wait for process to finish.")

    return serializable_gaussians(all_gaussians, indices)


if __name__ == "__main__":

    get_data()