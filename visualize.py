import napari
import numpy as np
from brainio import brainio
from brainrender.scene import Scene

def visialize_nii(nii_path):
    with napari.gui_qt():
        v = napari.Viewer(title="amap viewer")

        image_scales = (1, 1, 1)
        image = brainio.load_any(nii_path)
        image = np.swapaxes(image, 2, 0)

        v.add_image(
            image,
            name="Downsampled data",
        )


def visualize_obj(obj_path, *args, color='salmon', **kwargs):
    scene = Scene(add_root=False)
    scene.add_from_file(obj_path, *args,
        c=color, **kwargs)
    scene.render()