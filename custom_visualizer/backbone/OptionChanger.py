class OptionChanger(object):

    def __init__(self, option_dict):
        # Initial settings belong to the base model

        self.info_request = option_dict['vis_choice']

        self.wo_depth_refine = not option_dict['depth_refinement']
        self.wo_cost_volume = not option_dict['cost_volume']
        self.wo_backbone_cross_attn = not option_dict['cross_attention']
        self.wo_cost_volume_refine = not option_dict['cv_refinement']
        self.use_epipolar_trans = not option_dict['epipolar_transformer']

        # self.multiview_trans_attn_split = 5

        # self.d_feature = 128

        # self.costvolume_unet_feat_dim = 64
        # self.costvolume_unet_attn_res = [40]
        # self.costvolume_unet_channel_mult = [1, 2, 5]

        # self.depth_unet_feat_dim = 64
        # self.depth_unet_attn_res = [40]
        # self.depth_unet_channel_mult = [1, 2, 5]

        if 'gauss_percentage' in option_dict:
            self.proportion_to_keep = float(option_dict['gauss_percentage']) / 100.0
        else:
            self.proportion_to_keep = 0.15
        self.sample_idx = 0


    def get_config_override(self):
        override_dict = self.__dict__

        final_dict = {}

        for k, v in override_dict.items():
            if k != 'proportion_to_keep':
                final_dict[k] = str(v).lower()

        return final_dict