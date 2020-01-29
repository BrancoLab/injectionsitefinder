import os
from injection_finder.extraction.extraction import Extractor

import logging
from fancylog import fancylog
import fancylog as package

mouse='AY_254_2'    
channel='1'
rgf = 'Z:\\swc\\branco\\BrainSaw\\{}\\cellfinder\\registration'.format(mouse)
data = os.path.join(rgf, 'downsampled_channel_{}.nii'.format(channel))
out_fld = 'Z:\\swc\\branco\\BrainSaw\\injections'
out_path = os.path.join(out_fld, mouse+'_ch{}inj.obj'.format(channel))


fancylog.start_logging(
        rgf, package, verbose=True)


Extractor(
        data, 
        rgf, 
        logging, 
        overwrite=True,
        percentile_threshold=99.95,
        threshold_type='perc',
        obj_path=out_path,
)
