import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.model.encoder.encoder_costvolume import EncoderCostVolume
from src.model.types import Gaussians

from omegaconf import DictConfig
import hydra
from jaxtyping import install_import_hook
from dataclasses import fields
import torch

with install_import_hook(
    ("src",),
    ("beartype", "beartype"),
):
    from src.config import load_typed_root_config
    from src.dataset.data_module import DataModule
    from src.global_cfg import set_cfg

def reduce_gaussians(field, skip_factor):
    return field[:, ::skip_factor, ...]

## Used to load configuration file upon calling the function
@hydra.main(
    version_base=None,
    config_path="../config",
    config_name="main",
)
def visualize(cfg_dict: DictConfig):

    gaussian_proportion = 0.05

    cfg = load_typed_root_config(cfg_dict)
    set_cfg(cfg_dict)

    cost_volume_config = cfg.model.encoder

    # Configure hyperparameters depending on the ablation that is selected
    
    # Settings for epipolar transformer
    if (not cost_volume_config.use_epipolar_trans):
        cost_volume_config.multiview_trans_attn_split = 5

    # Settings for cost volume only
    if (not cost_volume_config.wo_cost_volume):
        cost_volume_config.d_feature = 128

    # Settings for cost volume and cost volume refinement
    if (not cost_volume_config.wo_cost_volume_refine) and (not cost_volume_config.wo_cost_volume):
        cost_volume_config.costvolume_unet_feat_dim = 64
        # Image sizes should be divisible by ALL unet attention resolutions
        cost_volume_config.costvolume_unet_attn_res = [40]

        # Length of channel multiplier determines the number of downsampling levels
        cost_volume_config.costvolume_unet_channel_mult = [1, 2, 5]

    # Settings for depth refinement
    if (not cost_volume_config.wo_depth_refine):
        cost_volume_config.depth_unet_feat_dim = 64
        # Image sizes should be divisible by ALL unet attention resolutions
        cost_volume_config.depth_unet_attn_res = [40]

        # Length of channel multiplier determines the number of downsampling levels
        cost_volume_config.depth_unet_channel_mult = [1, 2, 5]

    encoder_cost_vol = EncoderCostVolume(cfg.model.encoder)

    data_module = DataModule(cfg.dataset, cfg.data_loader)
    test_dl = data_module.test_dataloader(cfg.dataset)

    gaussianList = []

    for img in test_dl:
        gaussians = encoder_cost_vol.forward(img['context'], 1)

        # Reduce the number of gaussians to be shown depending on defined percentage
        for field in fields(gaussians):
            value = getattr(gaussians, field.name)

            all_gaussians = value.shape[1]
            final_no_gaussians = gaussian_proportion * all_gaussians
            skip_factor = int(all_gaussians // final_no_gaussians)

            new_val = value[:, ::skip_factor, ...]

            setattr(new_val, field.name, value)

        gaussianList.append(gaussians)

    print("YAY YOU DID IT")

if __name__ == "__main__":

    visualize()