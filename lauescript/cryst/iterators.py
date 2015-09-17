__author__ = 'jens'

import cPickle
from os.path import join


def database(pluginManager):
    path = pluginManager.config.get('APD', 'DatabasePath')
    picklepointer = open(join(path, 'database.pkl'), 'r')
    data = cPickle.load(picklepointer)
    picklepointer.close()
    return data.values()


def atoms_of_element(molecule, element='H'):
    return [atom for atom in molecule.atoms if atom.element == element]


def iter_atoms(molecule, sort=False):
    return molecule.iter_atoms(sort)


def iter_atom_pairs(molecule, bound=True, unique=True, sort=True):
    return molecule.iter_atom_pairs(bound, unique, sort=sort)

