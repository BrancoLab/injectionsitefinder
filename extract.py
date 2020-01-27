import os
import numpy as np 
import argparse
from skimage.filters import gaussian as gaussian_filter
from skimage.filters import threshold_otsu
from skimage import measure 

from brainio import brainio

from visualize import visualize_obj
from registration import get_registered_image
from analyse import analyse, get_largest_component

def reorient_image(image, invert_axes=None, orientation="saggital"):
    """
    Reorients the image to the coordinate space of the atlas

    :param image_path: str
    :param threshold: float
    :param invert_axes: tuple (Default value = None)
    :param image: 
    :param orientation:  (Default value = "saggital")

    """
    if invert_axes is not None:
        for axis in list(invert_axes):
            image = np.flip(image, axis=axis)

    if orientation is not "saggital":
        if orientation is "coronal":
            transposition = (2, 1, 0)
        elif orientation is "horizontal":
            transposition = (1, 2, 0)

        image = np.transpose(image, transposition)
    return image

def marching_cubes_to_obj(marching_cubes_out, output_file):
    """
    Saves the output of skimage.measure.marching_cubes as an .obj file

    :param marching_cubes_out: tuple
    :param output_file: str

    """

    verts, faces, normals, _ = marching_cubes_out
    with open(output_file, 'w') as f:
        for item in verts:\
            f.write(f"v {item[0]} {item[1]} {item[2]}\n")
        for item in normals:
            f.write(f"vn {item[0]} {item[1]} {item[2]}\n")
        for item in faces:
            f.write(f"f {item[0]}//{item[0]} {item[1]}//{item[1]} "
                    f"{item[2]}//{item[2]}\n")
        f.close()

def analyze(marching_cubes_out):
    verts, faces, normals, _ = marching_cubes_out
    res = measure.mesh_surface_area(verts, faces)
    # WIP


def extract(datapath, regfld, objpath=False, voxel_size=10.0, 
                render=False, 
                transform=True, 
                gaussian_kernel=2,
                threshold_type='otsu',
                threshold=99.99,
                run_registration_anyway=False,
                debug=True):
    """
        Extracts the location of injections from volumetric data.
        This is done by smoothing the the images with a gaussian filter,
        then the image is thresholded and binarized. The threshold
        is defined as a user given percentile of the distribution of 
        pixel intensity values across the entire volume.
        The extracted injection site 3d shape is saved as a .obj file

        :param datapath: str with path to a downsampled.nii file
        :param regfld: str, path to cellfinder/registration
        :param transform: bool, if false all operations are performed on the non transformed image
        :param objpath: str {optional}. Destination path to save the .obj file
        :param voxel_size: float {optional, 1}.
        :param render: bool, default False. If true brainrender is used to render the injection site
        :param gaussian_kernel: float, size of the kernel used to filter the images.
        :param threshold_type: str, either 'otsu' or 'perc' (percentile)
        :param threshold: float, range [0, 100] percentile to use for the percentile threshold
        :param debug: bool, is true functionality useful for debugging is enabled.
        :param run_registration_anyway: bool, if true the registration step is run even if there is a xxx_transformed.nii already. 
    """

    # Check if output file exists
    if not objpath: 
        objpath = datapath.split(".")[0]+".obj"

    if not transform:
        objpath = objpath.split(".")[0]+"_not_transformed.obj"

    if os.path.isfile(objpath) and not debug:
        print("Output file {} already exists. Skipping injection site extraction".format(objpath))
    else:
        # Load downsampled data registered to the atlas
        data = get_registered_image(datapath, regfld, debug, run_registration_anyway=run_registration_anyway)

        if transform:
            data = reorient_image(data, invert_axes=[2,], orientation='coronal')
        else:
            print("     analysing without applying the transform")

        print("Ready to extract injection site from: " + datapath)
        print("     Starting gaussian filtering")

        # Gaussian filter 
        kernel_shape = [gaussian_kernel, gaussian_kernel, 2]
        filtered = gaussian_filter(data, kernel_shape)
        print("     Filtering completed. Thresholding with {}".format(threshold_type))

        if threshold_type.lower() == 'otsu':
            thresh = threshold_otsu(filtered)
        elif threshold_type.lower() == 'percentile' or threshold_type.lower() == 'perc':
            thresh = np.percentile(filtered.ravel(), threshold)
        else:
            raise valueError("Unrecognised thresholding type: "+ threshold_type)
        binary = filtered > thresh

        if debug:
            if transform:
                brainio.to_nii(binary.astype(np.int16), os.path.join(datapath.split(".")[0] + "_thresholded.nii"))
            else:
                brainio.to_nii(binary.astype(np.int16), os.path.join(datapath.split(".")[0] + "_thresholded_not_transformed.nii"))

        # apply marching cubes 
        print("     Extracting surface from thresholded image")
        verts, faces, normals, values = \
            measure.marching_cubes_lewiner(binary, 0, step_size=1)

        # Scale to atlas spacing
        if voxel_size is not 1:
            verts = verts * voxel_size

        # Save image to .obj
        print("     Saving .obj at objpath\n\n")
        faces = faces + 1
        marching_cubes_to_obj((verts, faces, normals, values), objpath)

        # Keep only the largest connected component
        get_largest_component(objpath)

    # Analyze
    props = analyse(objpath)

    # Visualize
    if render:
        return visualize_obj(objpath, alpha=.5)


def get_parser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        dest="datapath",
        type=str,
        help="Path to brain volume (.nii) data",
    )

    parser.add_argument(
        dest="regfld",
        type=str,
        help="Path to cellfinder registration folder",
    )

    parser.add_argument(
        "-o",
        "--obj-path",
        dest="objpath",
        type=str,
        default=False,
        help="Path to output .obj file. Optional.",
    )

    parser.add_argument(
        "-r",
        "--render",
        dest="render",
        type=bool,
        default=False,
        help="If true the .obj file will be visualized in brainrender.",
    )
    parser.add_argument(
        "-k",
        "--gaussian-kernel",
        dest="gaussian_kernel",
        type=int,
        default=2.5,
        help="Int, size of kernel for gaussian smooting (x,y directions).",
    )
    parser.add_argument(
        "-t",
        "--threshold",
        dest="threshold",
        type=float,
        default=99.995,
        help="Float in range [0, 100]. The percentile number of pixel intensity values for tresholding",
    )

    parser.add_argument(
        "-tt",
        "--treshold-type",
        dest="threshold_type",
        type=str,
        default='otsu',
        help="'otsu' or 'percentile'. Determines how the threshold value is computed",
    )
    parser.add_argument(
        "-tr",
        "--transform",
        dest="transform",
        type=str,
        default='otsu',
        help="'if false the data are not registered",
    )
    return parser


def main():
    args = get_parser().parse_args()
    extract(
        args.datapath,
        args.regfld,
        objpath=args.objpath,
        render=args.render,
        gaussian_kernel=args.gaussian_kernel,
        threshold=args.threshold,
        threshold_type=args.threshold_type,
        transform=args.transform,
    )


if __name__ == "__main__":
    main()
