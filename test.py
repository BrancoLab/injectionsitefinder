import sys
sys.path.append("./")

import os
from extract import extract

test_fld = '/Users/federicoclaudi/Dropbox (UCL - SWC)/Rotation_vte/Anatomy/testbrain'
ch = 'downsampled_channel_1.nii'
datapath = os.path.join(test_fld, ch)

extract(datapath, render=True)