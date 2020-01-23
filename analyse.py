from vtkplotter import load, save
from vtkplotter.analysis import extractLargestRegion

def get_center_of_mass(actor):
    return actor.centerOfMass()

def get_volume(actor):
    return actor.volume()

def analyse(obj_filepath):
    actor = load(obj_filepath)

    props = {}
    props['center_of_mass'] = get_center_of_mass(actor)
    props['volume'] = get_volume(actor)

    return props

def get_largest_component(obj_filepath):
    actor = load(obj_filepath)
    actor =  extractLargestRegion(actor).flipNormals()
    save(actor, obj_filepath)