__author__ = 'jens'

from networkx import cycle_basis, Graph
from numpy import dot, cross

from lauescript.cryst.geom import is_bound
from lauescript.cryst.iterators import iter_atom_pairs


def find_rings(atoms, bonds=None):
    graph = Graph()
    # bonds = None
    class DummyMolecule(object):
        pass
    mol = DummyMolecule()
    mol.atoms = atoms
    if bonds is None:
        for atom1, atom2 in iter_atom_pairs():
            graph.add_edge(atom1.name, atom2.name)
    else:
        blacklist = []
        for b in bonds:
            for atom2i in b[1:10]:
                string = ' : '.join(sorted([atoms[b[0]].name, atoms[atom2i].name]))
                if not string in blacklist:
                    if is_bound(atoms[b[0]].cart, atoms[b[0]].element, atoms[atom2i].cart, atoms[atom2i].element):
                        graph.add_edge(atoms[b[0]].name, atoms[atom2i].name)
                    blacklist.append(string)
    ring_list = cycle_basis(graph)
    return ring_list


def find_planar_rings(atoms, bonds=None):
    all_rings = find_rings(atoms, bonds=bonds)
    return are_planar(atoms, all_rings)


def are_planar(atoms, all_rings):
    atom_dict = {atom.get_name(): atom for atom in atoms}
    planar_rings = []
    for ring in all_rings:
        l = len(ring)
        planarity = 0
        for i, atom_name0 in enumerate(ring):
            atom_name1 = ring[(i+1) % l]
            atom_name2 = ring[(i+2) % l]
            atom_name3 = ring[(i+3) % l]
            atom0 = atom_dict[atom_name0]
            atom1 = atom_dict[atom_name1]
            atom2 = atom_dict[atom_name2]
            atom3 = atom_dict[atom_name3]
            v = abs(dot((atom0.cart - atom3.cart), cross((atom1.cart - atom3.cart), (atom2.cart - atom3.cart)))) / 6.
            planarity += v
        if planarity / l < .1:
            planar_rings.append(ring)
    return planar_rings


