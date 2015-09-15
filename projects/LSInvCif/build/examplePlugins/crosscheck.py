"""
Created on May 16, 2014

@author: Jens Luebben

Plugin for analysing the results of a cross validation.
Designed for macro molecules.
"""

import cPickle
import glob
import os

from numpy import mean
from numpy.linalg import norm

from lauescript.laueio.pdb_iop import PDBAtom, PDBMolecule, PDBIOP


KEY = 'C'
OPTION_ARGUMENTS = {'mask': '',
                    'path': './',
                    'list': 10,
                    'gt': 0.0,
                    'residue': None,
                    'type': None,
                    'sigma': 3.0}


class Accumulator(object):
    """
    Class providing an interface to manage the 'Accumulator_Molecule'
    pseudo molecule and its 'Accumulator_Atom' pseudo atoms.
    """

    def __init__(self, molecule, length):
        """
        Initilizes the Accumulator.

        'molecule' must be a 'PDB_Molecule' instance.

        'length' must be the number of input files that will
        be read.
        """
        self.pseudo_molecule = Accumulator_Molecule(molecule, length)
        self.lengts = length

    def __add__(self, molecule):
        """
        Incorporates the data from molecule into the 'Accumulator_Molecule'
        pseudo molecule.
        """
        for atom in self.pseudo_molecule.atoms():
            atom.accumulate(molecule[atom.get_name()])
        return self

    def atoms(self):
        """
        Iterates over all pseudo atoms in the 'Accumulator_Molecule'.
        """
        for atom in self.pseudo_molecule.atoms():
            yield atom


class Accumulator_Atom(PDBAtom):
    """
    Class representing a pseudo molecule that is the
    average of a large number of model atoms.
    """

    def __init__(self, atom, length):
        super(Accumulator_Atom, self).__init__()
        self.length = length
        self.set_cart(atom.get_cart() / length)
        self.set_name(atom.get_name())
        self.set_serial_number(atom.get_serial_number())
        self.set_residue_number(atom.get_residue_number())
        self.set_residue(atom.get_residue())
        self.set_element(atom.get_element())
        self.set_type(atom.get_type())
        self.set_occupancy(atom.get_occupancy())
        self.set_adp_cart(atom.get_adp_cart())
        cart = atom.get_cart()
        self.x = cart[0]
        self.xx = cart[0] ** 2
        self.y = cart[1]
        self.yy = cart[1] ** 2
        self.z = cart[2]
        self.zz = cart[2] ** 2
        self.n = 1

        self.center = cart
        self.d = 0
        self.dd = 0
        self.error_dist = None

    def get_sigma_ratio(self, position):
        """
        Returns the ratio of the distance of 'position' from
        the averave position divided by the E.S.D of the average
        position.
        :param position: np.array representing an atom position.
        """
        dist = norm(position - self.cart)
        return dist / self.get_error_dist()

    def accumulate(self, atom):
        """
        Incorporates the data from a model atom into itself.
        """
        self.set_cart(self.get_cart() + atom.get_cart() / self.length)
        self.update_error_cart(atom)

    def update_error_cart(self, atom):
        """
        Updates the data needed for calculating the E.S.D. of the
        atomic position.
        """
        cart = atom.get_cart()
        x = cart[0]
        y = cart[1]
        z = cart[2]


        # ##
        self.center = (self.center * self.n + atom.get_cart()) / (self.n + 1)
        ###

        d = abs(norm(self.center - cart))
        self.n += 1

        self.x += x
        self.xx += x ** 2

        self.y += y
        self.yy += y ** 2

        self.z += z
        self.zz += z ** 2

        self.d += d
        self.dd += d ** 2
        if self.name == 'O4_323_HOH_ _30':
            print self.center,d

    def get_error_dist(self):
        """
        Returns the E.S.D. of the average position of the pseudo atom.
        """
        if self.error_dist:
            return self.error_dist
        self.n = float(self.n)
        if self.n > 1:
            self.error_dist = (1. / (self.n - 1) * ((self.dd) - 1. / self.n * (self.d) ** 2) ) ** 0.5
            return self.error_dist

    def get_error_cart(self):
        """
        Returns a list with the E.S.D.s of the three coordinates.
        """
        self.n = float(self.n)
        if self.n > 1:
            self.error_x = (1. / (self.n - 1) * ((self.xx) - 1. / self.n * (self.x) ** 2) ) ** 0.5
            self.error_y = (1. / (self.n - 1) * ((self.yy) - 1. / self.n * (self.y) ** 2) ) ** 0.5
            self.error_z = (1. / (self.n - 1) * ((self.zz) - 1. / self.n * (self.z) ** 2) ) ** 0.5
            return self.error_x, self.error_y, self.error_z

    def get_error_cart_mean(self):
        """
        Returns the average E.S.D. of the three cartesian coordinates.
        """
        return mean(self.get_error_cart())


class Accumulator_Molecule(PDBMolecule):
    """
    Class representing a pseudo molecule that is the representation
    of an average of many molecules.
    """

    def __init__(self, molecule, length):
        """
        Initializes the pseudo molecule.

        'molecule' must be an instance of an 'PDB_Molecule'.

        'length' must be the number of input files that will be read.
        """
        super(Accumulator_Molecule, self).__init__()
        self.lengths = length
        for atom in molecule.atoms():
            if atom.get_type() == 'W':
                continue
            # print
            # print atom.get_cart(), atom.cart
            atom = Accumulator_Atom(atom, length)
            self.add_atom(atom)
            # print atom.get_cart(), atom.cart


def run(configuration):
    """
    Executes the plugin.
    Asks the plugin manager for user input and calls the appropriate functions.
    """
    global config, printer
    config = configuration
    printer = config.setup()

    path = config.arg('path')

    global mask
    mask = config.arg('mask')

    file_names = [i for i in glob.iglob(path + mask + '*.pdb') if not i.endswith('crosscheck.pdb')]
    file_names = sorted(file_names)

    number_of_files = len(file_names)

    created = False

    if file_names:
        printer('{} matching PDB files detected.'.format(number_of_files))
    elif not glob.iglob(path + mask + '*.dat'):
        printer('ERROR: no files matching the mask \'{}{}***.pdb\' found.\n'.format(path, mask))
        config.exit()

    if not config.arg('clean') and os.path.exists('crosscheck_{}.dat'.format(mask)):
        if all([os.stat(f_name).st_mtime < os.stat('crosscheck_{}.dat'.format(mask)).st_mtime \
                for f_name in file_names if not f_name.endswith('crosscheck.pdb')]) \
                or config.arg('force'):
            printer(
                '\nFound valid cache file \'{}\'.\nUsing cache file instaed.'.format('crosscheck_{}.dat'.format(mask)))
            with open('crosscheck_{}.dat'.format(mask), 'r') as filepointer:
                accumulator = cPickle.load(filepointer)

    else:
        accumulator = create(file_names, number_of_files)
        created = True

    report(accumulator)

    sigma = config.arg('sigma')
    if config.arg('detail'):
        report_outliers(accumulator, file_names, number_of_files, sigma)

    if created:
        with open('crosscheck_{}.dat'.format(mask), 'w') as filepointer:
            cPickle.dump(accumulator, filepointer)


def create(file_names, number_of_files):
    """
    Creates and returns an Accumulator instance based
    on a list of filenames.
    """
    printer()
    printer('Processing files:')
    pdb_iop = PDBIOP(file_names[0])
    molecule = provide(pdb_iop)
    accumulator = Accumulator(molecule, number_of_files)

    printer.create_progressbar(67)
    percent = 1. / float(number_of_files) * 100
    printer.update_progressbar(percent)

    for i, file_name in enumerate(file_names[1:]):
        accumulator += provide(PDBIOP(file_name))
        percent = float(i + 1) / float(number_of_files) * 100
        printer.update_progressbar(percent)
    printer.finish_progressbar()

    # for atom in accumulator.atoms():
    #     print atom.name, atom.cart
    return accumulator


def report_outliers(accumulator, file_names, number_of_files, sigma):
    """
    Writes a file named depending on the chosen 'mask' and 'sigma' options
    that contain a list of *sigma outliers for every input file.
    """
    printer('\nCalculating report data for {}*sigma outliers.'.format(sigma))
    printer('\nProcessing 2nd pass:')
    printer.create_progressbar(67)
    percent = 1. / float(number_of_files) * 100
    printer.update_progressbar(percent)
    fp = open('{}_{}sigma_outliers.txt'.format(mask, sigma), 'w')
    sigma = float(sigma)
    y = 0
    n = 0
    for i, file_name in enumerate(file_names[1:]):
        fp.write('\n{}\n'.format(file_name))
        molecule = provide(PDBIOP(file_name))
        for atom in accumulator.atoms():
            # ===================================================================
            # print atom.get_sigma_ratio(molecule[atom.get_name()].get_cart()),sigma
            #===================================================================
            ratio = atom.get_sigma_ratio(molecule[atom.get_name()].get_cart())
            if ratio >= sigma:
                fp.write('{:25} {}\n'.format(atom.get_name(), '{:5.3}'.format(ratio)))
                #===============================================================
                # print atom.get_type(),atom.get_residue(),file_name,ratio,'{:3.1f}'.format(atom.get_error_dist())
                #===============================================================
                y += 1
            else:
                n += 1
        percent = float(i + 1) / float(number_of_files) * 100
        printer.update_progressbar(percent)
    printer.finish_progressbar()
    # print 'yes: {}\n no: {}'.format(y, n)
    fp.close()


def report(accumulator):
    """
    Compiles a table representing the data analysis results and
    prints it to the output.
    """
    printer('\n')
    length = int(config.arg('list'))

    gt = float(config.arg('gt'))
    resi = config.arg('residue')
    rtype = config.arg('type')
    sigma = float(config.arg('sigma'))

    sorted_atoms = sorted(accumulator.atoms(), key=lambda atom: atom.get_error_dist(), reverse=True)
    printer.table(['Type', 'ID', 'Resi', '#', 'ESD', 'ESD: X Y Z', 'Average Position'], head=True)

    counter = 0
    for atom in sorted_atoms:
        errors = '{:3.1f}'.format(atom.get_error_dist())
        if gt:
            if not float(errors) >= gt:
                continue
        if resi:
            if not atom.get_residue() == resi:
                continue
        if rtype:
            if not atom.get_type() == rtype:
                continue
        xyz_err = '{:3.1f} {:3.1f} {:3.1f}'.format(*atom.get_error_cart())
        position = '{:5.1f} {:5.1f} {:5.1f}'.format(*atom.get_cart())
        printer.table([atom.get_type(),
                       atom.get_serial_number(),
                       atom.get_residue(),
                       atom.get_residue_number(),
                       errors,
                       xyz_err,
                       position])
        counter += 1
        if counter == length:
            break
    printer.table(done=True)

    def provideNew():
        """
        Generator providing data to a PDB file.
        """
        for atom in sorted_atoms:
            if atom.get_error_dist() < sigma:
                yield [atom.get_name(),
                       atom.get_serial_number(),
                       atom.get_type(),
                       atom.get_residue(),
                       atom.get_residue_number(),
                       atom.get_cart(),
                       atom.get_occupancy(),
                       atom.get_adp_cart()]
    mask = config.arg('mask')
    if not mask:
        mask = 'all'
    crosspdb = PDBIOP('{}_crosscheck.pdb'.format(mask))
    crosspdb.setup(new=True)

    crosspdb.set(['serial_numbers', 'name_prefixes', 'residues',
                  'residue_numbers', 'cart', 'occupancies', 'adp_cart'],
                 provideNew, new=True)
    crosspdb.complete_rebuild()
    crosspdb.write()
    printer('\n\nAveraged PDB file without {}*sigma outliers written to: {}'.format(sigma,
                                                                                    '{}_crosscheck.pdb'.format(mask)))


def provide(pdb_iop):
    """
    Interface function for accessing the PDBIOP.
    Returns a PDBMolecule instance conatining
    a PDBAtom instance for every atom in the PDB
    file.
    """
    pdb_iop.read()
    molecule = PDBMolecule()
    for atom_data in pdb_iop.provide(['cart', 'serial_numbers', 'residue_numbers', 'elements', 'residues',
                                      'name_prefixes', 'occupancies', 'adp_cart']):
        atom = PDBAtom()
        atom.set_name(atom_data[0])
        atom.set_cart(atom_data[1])
        atom.set_serial_number(atom_data[2])
        atom.set_residue_number(atom_data[3])
        atom.set_element(atom_data[4])
        atom.set_residue(atom_data[5])
        atom.set_type(atom_data[6])
        atom.set_occupancy(atom_data[7])
        atom.set_adp_cart(atom_data[8])
        molecule.add_atom(atom)
    return molecule


