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
    """
    Returns a list of all atoms of a given element.
    """
    return [atom for atom in molecule.atoms if atom.element == element]

def atoms_with_attribute(molecule, attribute, value=None):
    """
    Returns a list of all atoms that either have a certain attribute if
    'value' is None or all atoms where the attribute has the value 'value'
    """
    atoms = [atom for atom in molecule.atoms if hasattr(atom, attribute)]
    if not value:
        return atoms
    return [atom for atom in atoms if getattr(atom,attribute) == value]

def selected_atoms(molecule, function, value):
    """
    Returns a list of atoms selected by a selector function.
    Each atom is passed to the function and the return value is compared
    to 'value'. If return value and 'value' are equal, the atom is
    'selected'.
    """
    return[atom for atom in molecule.atoms if function(atom) == value]


def iter_atoms(molecule, sort=False):
    return molecule.iter_atoms(sort)


def iter_atom_pairs(molecule, bound=True, unique=True, sort=True):
    return molecule.iter_atom_pairs(bound, unique, sort=sort)

