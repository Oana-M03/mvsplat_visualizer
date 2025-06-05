import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.model.encoder.encoder_costvolume import EncoderCostVolume

from jaxtyping import install_import_hook
from dataclasses import fields
from hydra import compose, initialize
import hydra
from omegaconf import DictConfig
from torch import Tensor

from OptionChanger import OptionChanger

with install_import_hook(
    ("src",),
    ("beartype", "beartype"),
):
    from src.config import load_typed_root_config
    from src.dataset.data_module import DataModule
    from src.global_cfg import set_cfg

global_cfg = None
encoder_cfg = None
data_module = None
test_dl = None

def change_config(override_obj : OptionChanger):
    # Change configuration of encoder model of MVSplat
    override_dict = override_obj.get_config_override()

    override_list = [f"++{k}={v}" for k, v in override_dict.items()]
    
    with initialize(version_base=None, config_path="../config/model/encoder"):
        cfg = compose(config_name="costvolume", overrides=override_list)

        global encoder_cfg
        encoder_cfg = cfg

        return cfg

## Used to load main configuration file upon calling the function
@hydra.main(
    version_base=None,
    config_path="../config",
    config_name="main",
)
def init_configs(cfg_dict: DictConfig):

    global global_cfg
    global_cfg = load_typed_root_config(cfg_dict)
    set_cfg(global_cfg)

    global data_module
    data_module = DataModule(global_cfg.dataset, global_cfg.data_loader)

    global test_dl
    test_dl = data_module.test_dataloader(global_cfg.dataset)
    

def obtain_gaussians(optionChanger: OptionChanger):

    gaussian_proportion = 0.05

    cfg = change_config(optionChanger)
    encoder_cost_vol = EncoderCostVolume(cfg)

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

    init_configs()

    optionChanger = OptionChanger()
    obtain_gaussians(optionChanger)