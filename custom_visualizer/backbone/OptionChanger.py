class OptionChanger(object):

    def __init__(self):
        # Initial settings belong to the base model
        self.wo_depth_refine = False
        self.wo_cost_volume = False
        self.wo_backbone_cross_attn = False
        self.wo_cost_volume_refine = False
        self.use_epipolar_trans = False

        self.multiview_trans_attn_split = 5

        self.d_feature = 128

        self.costvolume_unet_feat_dim = 64
        self.costvolume_unet_attn_res = [40]
        self.costvolume_unet_channel_mult = [1, 2, 5]

        self.depth_unet_feat_dim = 64
        self.depth_unet_attn_res = [40]
        self.depth_unet_channel_mult = [1, 2, 5]

        self.proportion_to_keep = 0.05


    def get_config_override(self):
        override_dict = self.__dict__

        for k, v in override_dict.items():
            override_dict[k] = str(v).lower()

        return override_dict