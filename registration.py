
from brainio import brainio
from cellfinder.tools import source_files
from amap.config.config import get_binary
from cellfinder.tools.exceptions import RegistrationError


from cellfinder.tools.system import (
    safe_execute_command,
    SafeExecuteCommandError,
)

PROGRAM_NAME = "reg_resample"

def prepare_segmentation_cmd(
    program_path,
    floating_image_path,
    output_file_name,
    destination_image_filename,
    control_point_file,)
    :
    cmd = "{} -cpp {} -flo {} -ref {} -res {}".format(
        program_path,
        control_point_file,
        floating_image_path,
        destination_image_filename,
        output_file_name,
    )
    return cmd

def get_registered_image(nii_path, control_point_filepath):
    downsampled_source_image = brainio.load_any(nii_path)

    # get binaries
    nifty_reg_binaries_folder = source_files.get_niftyreg_binaries()
    program_path = get_binary(nifty_reg_binaries_folder, PROGRAM_NAME)

    # get file paths
    basedir = os.path.split(nii_path)
    temp_output_filename = os.path.join(basedir, "temp.nii")
    output_filename = os.path.join(basedir, 'transformed.nii')
    destination_image_filename = os.path.join(basedir, 'destination.nii')
    log_file_path = os.path.join(basedir,'registrationlog.txt')
    error_file_path = os.path.join(basedir, 'registrationerr.txt')

    reg_cmd = prepare_segmentation_cmd(
        program_path,
        temp_output_filename,
        output_filename,
        destination_image_filename,
        control_point_file,
    )
    print("Running ROI registration")
    try:
        safe_execute_command(reg_cmd, log_file_path, error_file_path)
    except SafeExecuteCommandError as err:
        raise RegistrationError("ROI registration failed; {}".format(err))
