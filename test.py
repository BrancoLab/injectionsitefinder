import os
from injection_finder.extraction.extraction import Extractor

import logging
from fancylog import fancylog
import fancylog as package

mouse='CC_134_1'    
rgf = 'Z:\\swc\\branco\\BrainSaw\\{}\\cellfinder\\registration'.format(mouse)
data = os.path.join(rgf, 'downsampled_channel_1.nii')


fancylog.start_logging(
        rgf, package, verbose=True)


Extractor(
        data, 
        rgf, 
        logging, 
        overwrite=True,
        percentile_threshold=99.95,
        threshold_type='perc',
)
