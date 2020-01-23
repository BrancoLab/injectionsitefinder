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
    # TODO: move this to brainio
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
                gaussian_kernel=2,
                threshold=99.99,
                debug=False):
    """
        Extracts the location of injections from volumetric data.
        This is done by smoothing the the images with a gaussian filter,
        then the image is tresholded and binarized. The treshold
        is defined as a user given percentile of the distribution of 
        pixel intensity values across the entire volume.
        The extracted injection site 3d shape is saved as a .obj file

        :param datapath: str with path to a downsampled.nii file
        :param regfld: str, path to cellfinder/registration
        :param objpath: str {optional}. Destination path to save the .obj file
        :param voxel_size: float {optional, 1}.
        :param render: bool, default False. If true brainrender is used to render the injection site
        :param gaussian_kernel: float, size of the kernel used to filter the images.
        :param threshold: float, range [0, 100] percentile to use for the treshold
        :param debug: bool, is true functionality useful for debugging is enabled.
    """

    # Check if output file exists
    if not objpath: 
        objpath = datapath.split(".")[0]+".obj"

    if os.path.isfile(objpath) and not debug:
        print("Output file {} already exists. Skipping injection site extraction".format(objpath))
    else:
        # Load downsampled data registered to the atlas
        data = get_registered_image(datapath, regfld)
        data = reorient_image(data, invert_axes=[2,], orientation='coronal')
        print("Ready to extract injection site from: " + datapath)
        print("     Starting gaussian filtering")

        # Gaussian filter 
        kernel_shape = [gaussian_kernel, gaussian_kernel, 2]
        filtered = gaussian_filter(data, kernel_shape)
        print("     Filtering completed. Thresholding")

        # thresh = np.percentile(filtered.ravel(), threshold)
        thresh = threshold_otsu(filtered)
        binary = filtered > thresh

        if debug:
            brainio.to_nii(binary.astype(np.int16), os.path.join(os.path.split(datapath)[0], "tresholded.nii"))

        # apply marching cubes 
        print("     Extracting surface from tresholded image")
        verts, faces, normals, values = \
            measure.marching_cubes_lewiner(binary, 0, step_size=1)

        # Scale to atlas spacing
        if voxel_size is not 1:
            verts = verts * voxel_size

        # Save image to .obj
        print("     Saving as .obj")
        faces = faces + 1
        marching_cubes_to_obj((verts, faces, normals, values), objpath)

        # Keep only the largest connected component
        get_largest_component(objpath)

    # Analyze
    props = analyse(objpath)
    print(props)

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
        "--treshold",
        dest="treshold",
        type=float,
        default=99.995,
        help="Float in range [0, 100]. The percentile number of pixel intensity values for tresholding",
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
        treshold=args.treshold,
    )


if __name__ == "__main__":
    main()
