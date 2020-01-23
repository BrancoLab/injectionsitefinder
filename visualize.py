import napari
import numpy as np
from brainio import brainio
from brainrender.scene import Scene
import matplotlib.pyplot as plt

def visualize_nii(nii_path, other_imgs=[]):
    """
        Uses napari to visualize 3d data from a .nii file

        :param nii_path: str, path to .nii file
    """
    with napari.gui_qt():
        v = napari.Viewer(title="viewer")

        image = brainio.load_any(nii_path)
        image = np.swapaxes(image, 2, 0)

        v.add_image(
            image,
            name="Data",
        )

        for img in other_imgs:
            image = brainio.load_any(img)
            image = np.swapaxes(image, 2, 0)

            v.add_image(
                image,
            )       

def visualize_nii_slices(data, mx=1000):
    """
        Plots a bunch of slices from a .nii file to visualize them

        :param data: np.ndarray with loaded .nii
    """
    f, axarr = plt.subplots(4, 4)
    axarr = axarr.flatten()
    slices = np.linspace(200, data.shape[2]-201, num=16).astype(np.int32)

    for ax, idx in zip(axarr, slices):
        ax.imshow(np.rot90(data[:, ::-1, idx]), vmin=0, vmax=mx, cmap='gray')
    plt.show()


def visualize_obj(obj_path, *args, color='lightcoral', **kwargs):
    """
        Uses brainrender to visualize a .obj file registered to the Allen CCF

        :param obj_path: str, path to a .obj file
        :param color: str, color of object being rendered
    """
    print("Visualizing : " + obj_path)
    scene = Scene(add_root=True)
    scene.add_from_file(obj_path, *args,
        c=color, **kwargs)
    return scene