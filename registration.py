import os

from brainio import brainio
from amap.tools import source_files
from amap.config.config import get_binary
from amap.tools.exceptions import RegistrationError


from cellfinder.tools.system import (
    safe_execute_command,
    SafeExecuteCommandError,
)

PROGRAM_NAME = "reg_resample"
SOURCE_IMAGE_NAME = "downsampled.nii"
DEFAULT_CONTROL_POINT_FILE = "inverse_control_point_file.nii"
DEFAULT_OUTPUT_FILE_NAME = "roi_transformed.nii"
DEFAULT_TEMP_FILE_NAME = "ROI_TMP.nii"
default_atlas_name = "registered_atlas.nii"

# TODO this should be integrated in celllfinder ?
def prepare_segmentation_cmd(
    program_path,
    floating_image_path,
    output_file_name,
    destination_image_filename,
    control_point_file,):
    cmd = "{} -cpp {} -flo {} -ref {} -res {}".format(
        program_path,
        control_point_file,
        floating_image_path,
        destination_image_filename,
        output_file_name,
    )
    return cmd


def get_registered_image(nii_path, registration_dir):
    # get binaries
    nifty_reg_binaries_folder = source_files.get_niftyreg_binaries()
    program_path = get_binary(nifty_reg_binaries_folder, PROGRAM_NAME)

    # get file paths
    basedir = os.path.split(nii_path)[0]
    output_filename = os.path.join(basedir, 'transformed.nii')
    if os.path.isfile(output_filename):
        yn = input("Registred output exists already. Do you wish to run registration again?  [y,n]  ")
        if yn.lower() == "y":
            run = True
        else:
            run = False
    else:
        run = False
    
    if run:
        destination_image = os.path.join(registration_dir, default_atlas_name)
        control_point_file = os.path.join(registration_dir, DEFAULT_CONTROL_POINT_FILE)
        
        log_file_path = os.path.join(basedir,'registration_log.txt')
        error_file_path = os.path.join(basedir, 'registration_err.txt')

        reg_cmd = prepare_segmentation_cmd(
            program_path,
            nii_path,
            output_filename,
            destination_image,
            control_point_file,
        )
        print("Running registration")
        try:
            safe_execute_command(reg_cmd, log_file_path, error_file_path)
        except SafeExecuteCommandError as err:
            raise RegistrationError("Registration failed; {}".format(err))
    else:
        print('Skipping registration as output file already exists')

    return brainio.load_any(output_filename)