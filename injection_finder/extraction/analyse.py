from vtkplotter import load, save
from vtkplotter.analysis import extractLargestRegion


from brainrender.Utils.ABA.connectome import ABA


def get_center_of_mass(actor):
    """
        Get the center of mass of a vtk actor
    """
    return actor.centerOfMass()


def get_volume(actor):
    """
        Get the volume of a vtk actor
    """
    return actor.volume()


def analyse(obj_filepath):
    """
        Extracts a few stats from the .obj file with the data for an injection site.
        These include: volume, center of mass, brain regions it incluedes...

        :param obj_filepath: str, path to the .obj file for an injection site
    """
    # Load as vtk actor
    actor = load(obj_filepath)

    # Get stats
    props = {}
    props["center_of_mass"] = get_center_of_mass(actor)
    props["volume"] = get_volume(actor)

    # Get brain region of CoM and of other points on the outher surface
    aba = ABA()
    props["com_region"] = aba.get_structure_from_coordinates(
        get_center_of_mass(actor)
    )["acronym"]

    return props


def get_largest_component(obj_filepath):
    """
        Given a .obj file with multiple disconnected meshes in it, it
        selects the largest of these and discards the rest. 
    """
    actor = load(obj_filepath)
    actor = extractLargestRegion(actor).flipNormals()
    save(actor, obj_filepath)
