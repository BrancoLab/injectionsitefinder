import os
import numpy as np 
import argparse
from skimage.filters import gaussian as gaussian_filter
from skimage import measure
from brainio import brainio

import matplotlib.pyplot as plt

from image import marching_cubes_to_obj
from visualize import visualize_obj

def display_test(data, mx=1000):
    f, axarr = plt.subplots(4, 4)
    axarr = axarr.flatten()
    slices = np.linspace(200, data.shape[2]-201, num=16).astype(np.int32)

    for ax, idx in zip(axarr, slices):
        ax.imshow(np.rot90(data[:, ::-1, idx]), vmin=0, vmax=mx, cmap='gray')
    plt.show()


def extract(datapath, objpath=False, voxel_size=1.0, render=False):
    # Check if output file exists
    if not objpath: 
        objpath = datapath.split(".")[0]+".obj"

    if os.path.isfile(objpath):
        print("Output file {} already exists. Skipping injection site extraction".format(objpath))
    else:
        # Load downsampled data
        print("Ready to extract injection site from: " + datapath)
        data = brainio.load_any(datapath) # width, height, n images
        print("     data loaded. Starting gaussian filtering")

        # Gaussian filter
        datashape = data.shape
        # kernel_shape = [np.sqrt(datashape[0]).astype(np.int8), np.sqrt(datashape[1]).astype(np.int8), 5]
        kernel_shape = [2, 2, 2]
        filtered = gaussian_filter(data, kernel_shape)
        print("     filtering completed. Thresholding")

        # treshold and binarize
        thresh = np.percentile(filtered.ravel(), 99.99)
        binary = filtered > thresh

        # apply marching cubes 
        verts, faces, normals, values = \
            measure.marching_cubes_lewiner(binary, 0, step_size=1)

        # Scale to atlas spacing
        if voxel_size is not 1:
            verts = verts * voxel_size

        # Save image to .obj
        faces = faces + 1
        marching_cubes_to_obj((verts, faces, normals, values), objpath)

    # Visualize
    if render:
        visualize_obj(objpath)


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
        type=str,
        default=False,
        help="If true the .obj file will be visualized in brainrender.",
    )
    return parser


def main():
    args = get_parser().parse_args()
    extract(
        args.datapath,
        objpath=args.objpath,
        render=args.render,
    )


if __name__ == "__main__":
    main()
