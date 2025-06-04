import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.model.encoder.encoder_costvolume import EncoderCostVolumeCfg, OpacityMappingCfg, EncoderCostVolume
from src.model.encoder.common.gaussian_adapter import GaussianAdapterCfg

from torch.utils.data import DataLoader
from omegaconf import DictConfig
import hydra
from jaxtyping import install_import_hook

with install_import_hook(
    ("src",),
    ("beartype", "beartype"),
):
    from src.config import load_typed_root_config
    from src.dataset.data_module import DataModule
    from src.global_cfg import set_cfg
    from src.loss import get_losses
    from src.misc.LocalLogger import LocalLogger
    from src.misc.step_tracker import StepTracker
    from src.misc.wandb_tools import update_checkpoint_path
    from src.model.decoder import get_decoder
    from src.model.encoder import get_encoder
    from src.model.model_wrapper import ModelWrapper

## Used to load configuration file upon calling the function
@hydra.main(
    version_base=None,
    config_path="../config",
    config_name="main",
)
def visualize(cfg_dict: DictConfig):

    cfg = load_typed_root_config(cfg_dict)
    set_cfg(cfg_dict)

    name = "costvolume"
    d_feature = 128
    num_depth_candidates = 32
    num_surfaces = 1
    visualizer = None
    gaussian_adapter = GaussianAdapterCfg(gaussian_scale_min=4, gaussian_scale_max=10, sh_degree=3)
    opacity_mapping = OpacityMappingCfg(initial=0.2, final=0.5, warm_up=2)
    gaussians_per_pixel = 1
    unimatch_weights_path = None
    downscale_factor = 0.1
    shim_patch_size = 0.3
    multiview_trans_attn_split = 8
    costvolume_unet_feat_dim = 3
    costvolume_unet_channel_mult = [0.5, 0.5, 0.5]
    costvolume_unet_attn_res = [1, 1, 1]
    depth_unet_channel_mult = [1, 1, 1]
    depth_unet_feat_dim = 32
    depth_unet_attn_res = [100, 100, 100]
    wo_depth_refine = True
    wo_cost_volume = False
    wo_backbone_cross_attn = True
    wo_cost_volume_refine = True
    use_epipolar_trans = True

    encoder_cost_volume_cfg = EncoderCostVolumeCfg(
        name=name,
        d_feature = d_feature,
        num_depth_candidates=num_depth_candidates,
        num_surfaces=num_surfaces,
        visualizer=visualizer,
        gaussian_adapter=gaussian_adapter,
        opacity_mapping=opacity_mapping,
        gaussians_per_pixel=gaussians_per_pixel,
        unimatch_weights_path=unimatch_weights_path,
        downscale_factor=downscale_factor,
        shim_patch_size=shim_patch_size,
        multiview_trans_attn_split=multiview_trans_attn_split,
        costvolume_unet_feat_dim=costvolume_unet_feat_dim,
        costvolume_unet_channel_mult=costvolume_unet_channel_mult,
        costvolume_unet_attn_res=costvolume_unet_attn_res,
        depth_unet_channel_mult=depth_unet_channel_mult,
        depth_unet_feat_dim=depth_unet_feat_dim,
        depth_unet_attn_res=depth_unet_attn_res,
        wo_depth_refine=wo_depth_refine,
        wo_cost_volume=wo_cost_volume,
        wo_backbone_cross_attn=wo_backbone_cross_attn,
        wo_cost_volume_refine=wo_cost_volume_refine,
        use_epipolar_trans=use_epipolar_trans
    )

    cost_volume_config = cfg.model.encoder

    # A bit hacky but it works
    if cost_volume_config.wo_depth_refine and cost_volume_config.wo_backbone_cross_attn and cost_volume_config.wo_cost_volume_refine and (not cost_volume_config.wo_cost_volume) and (not cost_volume_config.use_epipolar_trans):
        cost_volume_config.costvolume_unet_feat_dim = 69
        cost_volume_config.d_feature = 128
        cost_volume_config.depth_unet_feat_dim = 64
        cost_volume_config.multiview_trans_attn_split = 5

    if cost_volume_config.wo_depth_refine and cost_volume_config.wo_backbone_cross_attn and (not cost_volume_config.wo_cost_volume_refine) and (not cost_volume_config.wo_cost_volume) and (not cost_volume_config.use_epipolar_trans):
        cost_volume_config.costvolume_unet_feat_dim = 64
        # Image sizes should be divisible by ALL unet attention resolutions
        cost_volume_config.costvolume_unet_attn_res = [15]

        # Length of channel multiplier determines the number of downsampling levels
        cost_volume_config.costvolume_unet_channel_mult = [1, 2]


    encoder_cost_vol = EncoderCostVolume(cfg.model.encoder)

    data_module = DataModule(cfg.dataset, cfg.data_loader)
    test_dl = data_module.test_dataloader(cfg.dataset)

    for img in test_dl:
        gaussians = encoder_cost_vol.forward(img['context'], 1)

    print("YAY YOU DID IT")

if __name__ == "__main__":

    visualize()