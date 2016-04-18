"""
Created on Apr 1, 2014

@author: jens
"""
from numpy import array

from lauescript.cryst.transformations import frac2cart, \
    frac2cart_ADP, \
    cart2frac, \
    cart2frac_ADP
from lauescript.laueio.io import IOP
from lauescript.types.atom import AtomInterface


class KEY(dict):
    """
    Class representing the xd refinement keys for a given
    atom.
    """

    def __init__(self, name):
        super(KEY, self).__init__()
        self.name = name

    def set_U2(self, value):
        self['U2'] = value

    def __str__(self):
        string = '{:<8}{:3} {:6} {:10} {:15} {:2} {:3} {:5} {:7} {:9}\n'.format(self.name,
                                                                                self['xyz'],
                                                                                self['U2'],
                                                                                self['U3'],
                                                                                self['U4'],
                                                                                self['Mono'],
                                                                                self['Dipo'],
                                                                                self['Quato'],
                                                                                self['Okto'],
                                                                                self['Hexa'])
        return string


class XDAtom(AtomInterface):
    def __init__(self, *args, **kwargs):
        super(XDAtom, self).__init__(*args, **kwargs)
        self.cell = None
        self.adp_frac = None
        
    def set_frac(self, value):
        super(XDAtom, self).set_frac(value)

    def set_adp_cart(self, value):
        if not None == value:
            self.adp_frac = cart2frac_ADP(value, self.cell)

    def get_adp_cart(self):
        return frac2cart_ADP(self.adp_frac, self.cell)

    def set_cart(self, value):
        if not None == value:
            self.frac = cart2frac(value, self.cell)

    def get_cart(self):
        return frac2cart(self.frac, self.cell)

    def set_cell(self, value):
        self.cell = value

    def __str__(self):
        string = '{name:<8s}{icor1:>3}{icor2:>2}{nax:>5}{nay1:>4}{nay2:>4}{jtf:>2}{itbl:>3}{isfz:>3}{lmax:>2}'\
                 '{isym:>3}{ichcon:>4} {x:>9.6f} {y:>9.6f} {z:>9.6f} {o:6.4f}\n'\
            .format(name=self.get_name(),
                    icor1=self.get_custom_attribute('icor1'),
                    icor2=self.get_custom_attribute('icor2'),
                    nax=self.get_custom_attribute('nax'),
                    nay1=self.get_custom_attribute('nay1'),
                    nay2=self.get_custom_attribute('nay2'),
                    jtf=self.get_custom_attribute('max_U'),
                    itbl=self.get_custom_attribute('sfac'),
                    isfz=self.get_custom_attribute('kappa_set'),
                    lmax=self.get_custom_attribute('lmax'),
                    isym=self.get_custom_attribute('isym'),
                    ichcon=self.get_custom_attribute('ichcon'),
                    x=self.get_frac()[0], y=self.get_frac()[1],
                    z=self.get_frac()[2], o=self.get_occupancy())
        string += ' {:9.6f} {:9.6f} {:9.6f} {:9.6f} {:9.6f} {:9.6f}'.format(*self.get_adp_frac())
        for i, mult in enumerate(self.get_custom_attribute('multipoles')):
            if i % 10 == 0:
                string += '\n '
            string += '{:7.4f} '.format(mult)
        string += '\n'

        return string


class XDIOP(IOP):

    def __init__(self, *args, **kwargs):
        super(XDIOP, self).__init__(*args, **kwargs)
        self.key_dict = None
        self.master_body = None
        self.cell = None
        self.current_atom_record = None
        self.master_file_name = None
        self.atoms = None
        self.body = None
        self.adp_cart = None
        self.adp_error_cart = None
        self.adp_frac = None
        self.adp_error_frac = None
        self.names = None
        self.cart = None
        self.frac = None
        self.element = None
        self.T = None
        self.multipoles = None
        self.chemcons = None

    def parse(self):
        self.cell = None
        self.master_file_name = self.filename.replace('.res', '.mas')
        self.parse_master_file()
        self.atoms = {}
        self.body = []
        self.current_atom_record = []
        self.names = []
        self.adp_frac = {}
        self.adp_error_frac = {}
        self.adp_cart = {}
        self.adp_error_cart = {}
        self.frac = {}
        self.cart = {}
        self.element = {}
        self.multipoles = {}
        self.T = None
        switch = False
        counter = 0
        for raw_line in self.content:
            if raw_line.startswith('USAGE'):
                self.body.append(raw_line)
                switch = True
                continue
            if not switch:
                self.body.append(raw_line)
                continue
            if not raw_line[0] == '!':
                newRec = True if not raw_line[0] == ' ' else False
                line = [i for i in raw_line[:-1].split(' ') if i]
                print self.current_atom_record, newRec, counter
                if self.current_atom_record and newRec and '(' in self.current_atom_record[0]:# or counter > 3:
                    self.parse_atom_record()
                    counter = 0

                # if len(line) == 0:
                #     continue
                if not newRec:
                    self.current_atom_record += line
                    counter += 1

                else:
                    self.current_atom_record = line
            else:
                self.body.append(raw_line)
        for name, atom in self.atoms.items():
            self.cart[name] = atom.get_cart()
            self.frac[name] = atom.get_frac()
            self.adp_cart[name] = atom.get_adp_cart()
            self.element[name] = atom.get_element()
            self.multipoles[name] = atom.get_custom_attribute('multipoles')
            self.names.append(name)

    def parse_atom_record(self):
        rec = self.current_atom_record
        atom = XDAtom()
        atom.set_name(rec[0])
        atom.set_element(rec[0][:rec[0].index('(')])
        atom.set_custom_attribute('icor1', rec[1])
        atom.set_custom_attribute('icor2', rec[2])
        atom.set_custom_attribute('nax', rec[3])
        atom.set_custom_attribute('nay1', rec[4])
        atom.set_custom_attribute('nay2', rec[5])

        atom.set_custom_attribute('max_U', rec[6])
        atom.set_custom_attribute('sfac', rec[7])
        atom.set_custom_attribute('kappa_set', rec[8])
        atom.set_custom_attribute('lmax', rec[9])
        atom.set_custom_attribute('isym', rec[10])
        atom.set_custom_attribute('ichcon', rec[11])

        atom.set_frac(array([float(i) for i in rec[12:15]]))
        atom.set_occupancy(float(rec[15]))

        atom.set_adp_frac([float(i) for i in rec[16:22]])
        atom.set_custom_attribute('multipoles', [float(i) for i in rec[22:]])
        self.atoms[rec[0]] = atom
        atom.set_cell(self.cell)
        self.body.append(atom)

    def parse_master_file(self):
        self.key_dict = {}
        self.master_body = []
        keyswitch = False
        atomsswitch = False
        self.chemcons = {}
        filepointer = open(self.master_file_name)
        for line in filepointer.readlines():
            if line.lstrip(' ').startswith('!'):
                continue
            if 'END SCAT' in line:
                atomsswitch = True
            if line.startswith('DUM'):
                atomsswitch = False
            if atomsswitch:
                sline = [item for item in line[:-1].split(' ') if item]
                try:
                    self.chemcons[sline[0]] = sline[12]
                except IndexError:
                    pass
            if line.startswith('CELL') and self.cell is None:
                self.cell = list([float(i) for i in line.split(' ')[1:] if i])
            elif line.startswith('END KEY'):
                keyswitch = False
            elif line.startswith('KEY'):
                keyswitch = True
            if keyswitch:
                sline = [i.rstrip('\n') for i in line.split(' ') if i]
                if '(' in sline[0] and ')' in sline[0]:
                    key = sline[0]
                    if key in self.chemcons.keys():
                        self.key_dict[key] = self.key_dict[self.chemcons[key]]
                        self.master_body.append(key+'\n')
                        continue
                    atom_key_dict = KEY(key)
                    atom_key_dict['xyz'] = sline[1]
                    try:
                        atom_key_dict['U2'] = sline[2]
                        atom_key_dict['U3'] = sline[3]
                        atom_key_dict['U4'] = sline[4]
                    except IndexError:
                        atom_key_dict['U2'] = 0
                        atom_key_dict['U3'] = 0
                        atom_key_dict['U4'] = 0
                    try:
                        atom_key_dict['Mono'] = sline[5]
                        atom_key_dict['Dipo'] = sline[6]
                        atom_key_dict['Quato'] = sline[7]
                        atom_key_dict['Okto'] = sline[8]
                        atom_key_dict['Hexa'] = sline[9]
                    except KeyError:
                        pass
                    except IndexError:
                        atom_key_dict['Mono'] = 0
                        atom_key_dict['Dipo'] = 0
                        atom_key_dict['Quato'] = 0
                        atom_key_dict['Okto'] = 0
                        atom_key_dict['Hexa'] = 0
                    self.key_dict[key] = atom_key_dict
                    self.master_body.append(atom_key_dict)
                else:
                    self.master_body.append(line)
            else:
                self.master_body.append(line)
        filepointer.close()

    def set_U2(self, name, value):
        self.key_dict[name].set_U2(value)

    def set_adp_cart(self, name, value):
        self.atoms[name].set_adp_cart(value)
        if self.atoms[name].get_element() == 'H':
            self.set_U2(name, '000000')
            self.atoms[name].set_custom_attribute('max_U', '2')
        self.adp_cart[name] = self.atoms[name].get_adp_cart()

    def set_multipoles(self, name, value):
        self.atoms[name].set_custom_attribute('multipoles', value)
        self.multipoles[name] = self.atoms[name].get_custom_attribute('multipoles')

    def set_cart(self, name, value):
        self.atoms[name].set_cart(value)
        self.cart[name] = self.atoms[name].get_cart()

    def get_id(self):
        return 'XD'

    def __str__(self):
        self.write_master_file()
        string = ''
        for line in self.body:
            string += str(line)
        string += '\n'
        return string

    def write_master_file(self):
        filepointer = open(self.master_file_name + '2', 'w')
        for line in self.master_body:
            filepointer.write(str(line))

    def export_shelxl(self, temp = 100, waveLength=0.71073, title='XDImport',
                      disps=True, fixXYZ=False, globalU=False, scale = 1.0,
                      hklf=4):
        from lauescript.cryst.tables import atomtable
        if fixXYZ:
            fixXYZ = 10
        else:
            fixXYZ = 0
        sfacs = set([atom.get_element() for atom in self.atoms.values()])
        try:
            sfacs.remove('H')
        except KeyError:
            pass
        sfacList = sorted(list(sfacs), key=lambda sfac: atomtable[sfac]) + ['H']
        sfacs = {x: i+1 for i, x in enumerate(sfacList)}
        content = 'TITL {}\nCELL {} {}\nZERR 1 {}'.format(title, waveLength, ' '.join(['{:7.4f}'.format(x) for x in self.cell]), ' '.join(['{:7.4f}'.format(d/100.) for d in self.cell]))
        content += '\nLATT 1'
        content += '\nSFAC {}'.format(' '.join(sfacList))
        if not disps:
            for sfa in sfacList:
                content += '\nDISP ${} 0.000 0.000'.format(sfa)
        content += '\nUNIT {}'.format(' '.join([str(sfacs[x]) for x in sfacList]))
        content += '\nL.S. 10'
        content += '\nLIST 6'
        content += '\nTEMP {}'.format(temp-273)
        content += '\nPLAN 20'
        content += '\nWGHT 0.0'
        content += '\nFVAR {:.2f}'.format(scale)
        if globalU:
            content += ' {}'.format(globalU)
        atomList = sorted(self.atoms.values(), reverse=True, key= lambda atom: atom.get_name())
        for atom in atomList:
            content += '\n{:<5} {} {} 11.0'.format(atom.get_name().replace('(', '').replace(')', ''),
                                                             sfacs[atom.get_element()],
                                                             ' '.join(['{:9.5f}'.format(x+fixXYZ) for x in atom.get_frac()]))
            if not globalU:
                content += ' {}\n {}'.format(' '.join(['{:9.5f}'.format(x) for x in atom.get_adp_frac()[:2]]),
                                             ' '.join(['{:9.5f}'.format(x) for x in atom.get_adp_frac()[2:]]))
            else:
                content += ' 21.0'
        content += '\nHKLF {}\nEND'.format(hklf)
        return content


if __name__ == '__main__':
    test = XDIOP('xd.res')
    test.read()