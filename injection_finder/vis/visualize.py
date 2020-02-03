import os
import napari
import numpy as np
from brainio import brainio
from brainrender.scene import Scene
from brainrender.Utils.actors_funcs import edit_actor
import matplotlib.pyplot as plt
from vtkplotter.analysis import surfaceIntersection


def outcome_visualizer(thresholded_nii, regfolder, other_channels=[]):
    """ 
        Visualizes in napari viewer the thresholded image over the brain regions
        boundaries and optionally other user provided channels

        :param thresholded_nii: str path
        :param regfolder: str path to registration folder
        :param other_channels: list of strings with other .nii images to add to visualization
    """
    # Prepare data
    boundaries = [
        os.path.join(regfolder, f)
        for f in os.listdir(regfolder)
        if "boundaries.nii" in f
    ][0]

    # Visualize in napari
    with napari.gui_qt():
        v = napari.Viewer(title="extraction's outcome viewer")

        # Added thresholded
        v.add_image(
            image, name="Thresholded image", colormap="cyan", opacity=0.4,
        )

        for img in other_imgs:
            if not os.path.isfile(img):
                raise FileNotFoundError(
                    "Other_channels parameter was passed an incorrect value"
                )
            image = brainio.load_any(img)
            image = np.swapaxes(image, 2, 0)

            v.add_image(
                image, name=os.path.split(img)[-1].split(".")[0], opacity=0.3,
            )

        # Add boundaries image
        image = brainio.load_any(boundaries)
        image = np.swapaxes(image, 2, 0)
        v.add_image(
            image, name="Boundaries",
        )
