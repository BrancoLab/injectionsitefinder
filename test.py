import sys
sys.path.append("./")

import os
from extract import extract
from visualize import *
from brainrender.colors import color_nicks

import sys

mouse_id = 'CC_134_1'
regfolder = 'Z:\\swc\\branco\\BrainSaw\\{}\\cellfinder\\registration'.format(mouse_id)
injfld = 'Z:\\swc\\branco\\BrainSaw\\injections'

print("\n\n Starting Channel 0")
ch = 'downsampled_channel_0.nii'
datapath = os.path.join(regfolder, ch)
outpath = os.path.join(injfld, mouse_id+'_ch0.obj')
scene = extract(datapath, regfolder, objpath=outpath, debug=True, threshold=99.9)

print("\n\n Starting Channel 1")
ch = 'downsampled_channel_1.nii'
datapath = os.path.join(regfolder, ch)
outpath = os.path.join(injfld, mouse_id+'_ch1.obj')
scene = extract(datapath, regfolder, objpath=outpath, debug=True, threshold=99.9)


# scene.add_brain_regions(['SCm'], use_original_color=True, wireframe=1)
# scene.render()



# injfld = 'Z:\\swc\\branco\\BrainSaw\\injections'
# files = [os.path.join(injfld, f) for f in os.listdir(injfld)]
# colors = list(color_nicks.values())

# visualize_injections(files, colors, regions=['SCs']).render()