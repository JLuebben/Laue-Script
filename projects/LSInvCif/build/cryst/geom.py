"""
Created on Feb 18, 2014

@author: Jens Luebben

Module for simple geometry operations.
"""
import numpy as np

from lauescript.cryst.tables import covalence_radius


def bond_error(cart1, cart2, err1, err2):
    """
    Calculates and returns the error of a bond lengths based on the
    error of the coordinates.

    WARNING: Not properly tested.
    """
    cart1 = np.array(cart1)
    cart2 = np.array(cart2)
    norm = np.linalg.norm(cart1 - cart2)
    return sum([(((0.5 * (2 * cart1[i] - 2 * (cart2[i] + 1)) / norm) ** 2) * err1[i]) * 2 for i in xrange(3)])


def is_bound(pos1, el1, pos2, el2):
    """
    Uses the covalence radii to test whether two atoms are bound
    based on their cartesian coordinates and thei element symbol.
    """
    threshold = 0.1
    if el1 == 'H' or el2 == 'H':
        threshold = 0.2
    if np.linalg.norm(np.array(pos1) - np.array(pos2)) < covalence_radius[el1] + covalence_radius[el2] + threshold:
        return True
    return False


# ===============================================================================
# cart1=[1.1,1.2,0]
# cart2=[-1.1,1.2,0]
# err1=[0.01,0.01,0.02]
# err2=[0.01,0.01,0.02]
# print bond_error(cart1,cart2,err1,err2)
#===============================================================================


def framework_crawler(atom, direction, rigid_group_old=None):
    """
    Function to identify atoms belonging to a rigid group defined by
    a bond axis.
    Arguments:
        atom:            the name of the first atom of the rigid group.
        direction:       the name of the second atom of the rigid group.
        rigid_group_old: used by the function itself for recursive calls.

    Returns a list of atom names belonging to the rigid group.
    """
    if not rigid_group_old:
        rigid_group = [atom, direction]
    else:
        rigid_group = rigid_group_old
    for atom in get_framework_neighbors(direction):
        if not atom in rigid_group and not atom.element == 'H':
            rigid_group.append(atom)
            framework_crawler(rigid_group[0], atom, rigid_group)
    if not rigid_group_old:
        #=======================================================================
        # print '    Determined rigid group:', [i.name for i in rigid_group]
        #=======================================================================
        return rigid_group


def get_framework_neighbors(atom, useH=True):
    """
    Needs a ATOM.atom instance as argument.
    Returns the names of the framework atoms bound to that atom.
    """
    neighborlist = []
    for atom2 in atom.partner[:5]:
        if np.linalg.norm(atom.cart - atom2.cart) <= float(covalence_radius[atom.element]) + float(
                covalence_radius[atom2.element]) + .1:
            if not 'H' == atom2.element or useH:
                neighborlist.append(atom2)
    return neighborlist


def get_center_of_mass(molecule, use='cart'):
    return np.mean(molecule.coords(use))
#===============================================================================
# def identify_molecules(molecule):
#     '''
#     Takes an instance of the MOLECULE class as argument and returns a
#     dictionary that keys an identifying integer to every atom name
#     specifying which of the atoms in the molecule form an 'independent'
#     molecule in the chemical sense.
#     If all atoms are part of the same molecule, all atoms get the
#     integer '0'.
#     '''
#     blacklist=set()
#     #===========================================================================
#     # molecules=[]
#     #===========================================================================
#     ID=0
#     for atom1 in molecule.atoms:
#         framework=[]
#         for atom2 in get_framework_neighbors(atom1):
#             if not atom1.get_name() in blacklist and not atom2.get_name() in blacklist:
#                 framework+=framework_crawler(atom1,atom2)
#                 framework+=framework_crawler(atom2,atom1)
#                 framework = list(set(framework))
#                 [blacklist.add(atom.get_name()) for atom in framework]
#                 #===============================================================
#                 # molecules.append(framework)
#                 #===============================================================
#         if framework:
#             for atom in framework:
#                 atom.set_molecule_id(ID)
#             ID+=1
#===============================================================================








