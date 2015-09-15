__author__ = 'jens'

import cPickle


def database(pluginManager):
    path = pluginManager.config.get('APD', 'DatabasePath')
    picklepointer = open(path + '/database.pkl', 'r')
    data = cPickle.load(picklepointer)
    picklepointer.close()
    return data.values()


def atoms_of_element(molecule, element='H'):
    return [atom for atom in molecule.atoms if atom.element == element]

