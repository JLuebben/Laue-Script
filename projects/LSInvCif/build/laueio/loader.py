"""
Created on Mar 31, 2014

@author: jens
"""
import glob
import os

from lauescript.core import apd_printer
from lauescript.laueio.shelxl_iop import ShelxlIOP
from lauescript.laueio.cif_iop import CIFIOP
from lauescript.laueio.xd_iop import XDIOP
from lauescript.laueio.pdb_iop import PDBIOP
from lauescript.types.molecule import MOLECULE
from lauescript.core.core import apd_exit


class Loader(object):
    """
    A class for creating and managing IOPs. All Loader instances
    share their created IOPs via the Loader.IOPs attribute.
    """
    IOPs = {}
    filetypes = ('.res',
                 '.cif',
                 '.mas',
                 '.pdb')
    suffix = {'shelxl': '.ins',
              'CIF': '.cif',
              'XD': '.inp',
              'PDB': '.pdb'}
    read_files = []

    def __init__(self, printer):
        self.printer = printer
        self.IOP = None

    @staticmethod
    def get_read_files():
        """
        :return: A list of all filenames used.
        """
        return Loader.read_files

    def register_IOP(self, IOP):
        """
        Adds an IOP to the Loader.IOPs attribute and
        makes it active.
        """
        self.IOP = IOP
        Loader.IOPs[IOP.get_id()] = IOP

    def get_active_id(self):
        """
        Returns the ID of the currently active IOP.
        """
        return self.IOP.get_id()

    def auto_setup(self, path='./'):
        """
        Automatically sets up an IOP depending on the files
        present in the directory 'path'. The newest file with
        known file extension is determined and a corresponding
        IOP is registered and set active.
        """
        selected_filename = None
        for filename in sorted(glob.iglob(path + '*'), key=os.path.getctime, reverse=True):
            if any([filename.endswith(filetype) for filetype in Loader.filetypes]):
                selected_filename = filename
                break
        if not selected_filename:
            self.no_file_exit()
        self.printer('Using file \'{}\' for coordinates and ADPs.'.format(filename))
        self.register_IOP(self._determine_correct_IOP(filename))

    def load(self, name):
        """
        Creates and returns a molecule object.
        """
        Loader.read_files.append(self.IOP.filename)
        self.IOP.read()
        molecule = MOLECULE(name, cell=self.IOP.get_cell())
        for atom in self.IOP.provide(['cart', 'frac', 'adp_cart', 'element']):
            if not atom[4].startswith('W'):
                molecule.add_atom(name=atom[0],
                                  cart=atom[1],
                                  frac=atom[2],
                                  molecule=molecule,
                                  element=atom[4])
                molecule[atom[0]].give_adp(key='cart_meas', value=atom[3])
        return molecule

    def get_cell(self):
        return self.IOP.get_cell()

    def get_temperature(self):
        T = self.IOP.get_temperature()
        return T

    def switch_IOP(self, ID, newest=False):
        """
        Makes the IOP corresponding to 'ID' active.
        If 'newest' is True, the IOP created last with an
        ID that starts with 'ID' is set active.
        """
        if not newest:
            key = ID
        else:
            key = max([key for key in Loader.IOPs.keys() if key.startswith(ID)])
        self.IOP = Loader.IOPs[key]


    def for_IOP_of_type(self, ID):
        """
        Generator for iterating over all registered IOPs of
        a type defined by 'ID'. Legal IDs are 'shelx', 'cif'
        etc.
        """
        for key in [key for key in Loader.IOPs.keys() if key.startswith(ID)]:
            yield Loader.IOPs[key]

    def create(self, filename):
        self.register_IOP(self._determine_correct_IOP(filename))

    def _determine_correct_IOP(self, filename):
        """
        Returns an IOP for the given filetype.
        """
        if any([string in filename for string in ['xd.res', 'xd.inp']]):
            return XDIOP(filename)
        elif any([filename.endswith(string) for string in ['.ins', '.res']]):
            return ShelxlIOP(filename)
        elif filename.endswith('.cif'):
            return CIFIOP(filename)
        elif filename.endswith('.pdb'):
            return PDBIOP(filename)

    def no_file_exit(self):
        message = 'ERROR: No suitable file found in working directory.'
        apd_exit(message=message)

    def get_symmetry(self):
        return self.IOP.get_symmetry()

    def get_lattice(self):
        return self.IOP.get_lattice()

    def write(self):
        self.IOP.write()

    def get_IOP(self):
        return self.IOP

    def get_write_copy(self, filename):
        filename += Loader.suffix[self.get_active_id().rstrip('1234567890')]
        return self.IOP.clone(filename)


if __name__ == '__main__':
    printer = apd_printer()
    test = Loader(printer)
    test.auto_setup()
    test.load('test')
