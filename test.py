import sys
sys.path.append("./")

import os
from extract import extract
from visualize import visualize_nii

import sys
if sys.platform == "darwin":
    test_fld = '/Users/federicoclaudi/Dropbox (UCL - SWC)/Rotation_vte/Anatomy/testbrain'
else:
    test_fld = 'Z:\\swc\\branco\\BrainSaw\\CC_134_2\\cellfinder\\registration'
ch = 'downsampled_channel_1.nii'
datapath = os.path.join(test_fld, ch)

scene = extract(datapath, test_fld, render=True, debug=True, threshold=99.9)
scene.add_brain_regions(['SCm'], use_original_color=True, wireframe=1)
scene.render()


# visualize_nii(r'Z:\swc\branco\BrainSaw\CC_134_1\cellfinder\registration\tresholded.nii',
#         other_imgs=[r'Z:\swc\branco\BrainSaw\CC_134_1\cellfinder\registration\boundaries.nii',
#                     r'Z:\swc\branco\BrainSaw\CC_134_1\cellfinder\registration\downsampled_channel_1.nii'])

