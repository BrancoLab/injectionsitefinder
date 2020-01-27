import sys
sys.path.append("./")

import os
from extract import extract
from visualize import *
from brainrender.colors import color_nicks
from brainrender.scene import Scene
import sys

# mice = ['CC_134_1', 'CC_134_2', 'AY_246_4', 'AY_254_2']
# for mouse in mice:    
#     rgf = 'Z:\\swc\\branco\\BrainSaw\\{}\\cellfinder\\registration'.format(mouse)
#     data = os.path.join(rgf, 'downsampled_channel_1.nii')
#     extract(data, rgf, threshold_type='percentile', threshold=99.96, transform=False)
#     extract(data, rgf, threshold_type='percentile', threshold=99.96, transform=True)


mouse = "CC_134_2"
reg_fld = 'Z:\\swc\\branco\\BrainSaw\\{}\\cellfinder\\registration'.format(mouse)
tresh = os.path.join(reg_fld, 'downsampled_channel_1_thresholded_not_transformed.nii')
d1 = os.path.join(reg_fld, 'downsampled_channel_1.nii')
outcome_visualizer(tresh, reg_fld, other_channels=[d1])



