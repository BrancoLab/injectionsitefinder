from vtkplotter import load

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