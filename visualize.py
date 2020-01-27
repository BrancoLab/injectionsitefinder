import os
import napari
import numpy as np
from brainio import brainio
from brainrender.scene import Scene
from brainrender.Utils.actors_funcs import edit_actor
import matplotlib.pyplot as plt
from vtkplotter.analysis import surfaceIntersection


# ---------------------------------------------------------------------------- #
#                             SMALL UTIL FUNCTIONS                             #
# ---------------------------------------------------------------------------- #

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




# ---------------------------------------------------------------------------- #
#                          COMPLETE SCENES/VISUALIZERS                         #
# ---------------------------------------------------------------------------- #

def outcome_visualizer(thresholded_nii, regfolder, other_channels=[]):
    """ 
        Visualizes in napari viewer the thresholded image over the brain regions
        boundaries and optionally other user provided channels

        :param thresholded_nii: str path
        :param regfolder: str path to registration folder
        :param other_channels: list of strings with other .nii images to add to visualization
    """
    boundaries = [os.path.join(regfolder, f) for f in os.listdir(regfolder)\
                    if 'boundaries.nii' in f][0]
    other_channels.append(boundaries)

    visualize_nii(thresholded_nii, other_imgs=other_channels )



def visualize_injections(injections, colors, regions=[], add_com=True,
                    regions_kwargs={}, com_kwargs={}, actor_kwargs={},
                    edit_actor_kwargs={}, add_root=True,
                    intersect_regions=[]):
    """
        Renders a number of user provided .obj files with injection site 
        surface into a brainrender scene. Also provides opportunity to 
        add other elements and personalize the scene.

        :param injections: list of strings with paths to .obj files
        :param colors: list of strings with colors. needs to be at least as long as injections
        :param regions: list of strings with acronyms of brain regions to add
        :param regions_kwargs: dict, with kwargs to specify how regions are rendered
        :param add_com: bool, if true a  sphere at the center of mass of each injection is rendered
        :param com_kwargs: dict, with kwargs to specify how com are rendred
        :param actor_kwargs: dict, with kwargs to specify how injections actors are rendered
        :param edit_actor_kwargs: dict, with kwargs to specify furter details of the injection sites appearance
        :param add_root: bool, if true the outline of the whole brain is added to the scene
    """
    def add_CoM(act, scene, color, **kwargs):
        """ Adds center of mass to the scene """
        com = act.centerOfMass()
        scene.add_sphere_at_point(com, color=color, **kwargs)

    scene = Scene(add_root=add_root)
    fakescene = Scene(add_root=add_root) # used to load meshes that should not be rendered

    for fl, c in zip(injections, colors): 
        act = scene.add_from_file(fl, c=c, **actor_kwargs)
        edit_actor(act, **edit_actor_kwargs)

        if add_com:
            add_CoM(act, scene, c, **com_kwargs)

        if intersect_regions:
            fakescene.add_brain_regions(intersect_regions)
            for iregion in intersect_regions:
                reg = fakescene.actors['regions'][iregion]
                intersection = surfaceIntersection(act, reg)
                scene.add_vtkactor(intersection)

    
    if regions:
        scene.add_brain_regions(regions, use_original_color=True, **regions_kwargs)
        

    return scene 


def render_experiment(injections, cells, injections_colors, cells_colors, regions=[], regions_kwargs={}):
    if not isinstance(injections, list): injections = [injections]
    if not isinstance(cells, list): cells = [cells]
    if not isinstance(injections_colors, list): injections_colors = [injections_colors]
    if not isinstance(cells_colors, list): cells_colors = [cells_colors]

    scene = Scene()

    for injection, color in zip(injections, injections_colors):
        scene.add_from_file(injection, c=color)
    
    for cellfile, cellcolor in zip(cells, cells_colors):
        scene.add_cells_from_file(cellfile, color=cellcolor, radius=10, alpha=.3)

    if regions:
        scene.add_brain_regions(regions, use_original_color=True, **regions_kwargs)

    return scene
