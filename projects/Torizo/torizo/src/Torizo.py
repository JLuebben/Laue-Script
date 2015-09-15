
__author__ = ''

KEY = 'Torizo'  # Edit this to control which cmd line keyword starts the plugin.
OPTION_ARGUMENTS = {'load': 'myFile.txt',
                    'psf': 'psf file',
                    'torsion': [1, 2, 3, 4],
                    'bins': '12',
                    'model': 'shelx.res'}  # Edit this to define cmd line options for
# the plugin and their default values.
from lauescript.core.core import *
import struct
from numpy import zeros
import numpy as np
from copy import deepcopy
from lauescript.cryst.transformations import cart2frac, cart2frac_ADP
from lauescript.cryst.crystgeom import get_adp_as_matrix
from lauescript.cryst.geom import rotate_point_about_axis, rotate_ADP_about_axis


def dihedral(p):
    b = p[:-1] - p[1:]
    b[0] *= -1
    v = np.array([v - (v.dot(b[1])/b[1].dot(b[1])) * b[1] for v in [b[0], b[2]]])
    v /= np.sqrt(np.einsum('...i,...i', v, v)).reshape(-1, 1)
    b1 = b[1] / np.linalg.norm(b[1])
    x = np.dot(v[0], v[1])
    m = np.cross(v[0], b1)
    y = np.dot(m, v[1])
    return np.degrees(np.arctan2(y, x))


def readF(fp, form):
    return struct.unpack(form, fp.read(struct.calcsize(form)))[0]


def frame2molecules(frame, Natoms):
    molecule = []
    for i, atom in enumerate(frame):
        molecule.append(atom)
        if not (i+1) % Natoms:
            yield molecule
            molecule = []


def guessMoleculeSize(filename):
    with open(filename, 'r') as fp:
        switch = False
        number = 0
        names = []
        for line in fp.readlines():
            if switch:
                number = int(line[14])
                if number:
                    return len(names)
                else:
                    names.append(line[23:26])

            else:
                if '!NATOM' in line:
                    switch = True


def makeBlankFile(pluginManager):
    bins = int(pluginManager.arg('bins'))
    average = 1./float(bins)
    fvars = ['{:5.3f}'.format(average) if (n+1) % 6 else '{:4.2f} =\n'.format(average) for n in xrange(bins/3)]
    print ' '.join(fvars)
    print
    print 'SUMP 1 0.01 {}'.format(''.join([' 1 {}'.format(n+2) if (n+1) % 6 else ' 1 {} =\n'.format(n+2) for n in xrange(bins/3)]))
    binSize = 360/bins
    model = ExpModel(pluginManager.arg('model'), pluginManager)
    model.setRotamerGroup(['H12A', 'H12B', 'H12C'], ['C11', 'C12'], ['O3', 'C11', 'C12', 'H12A'])
    for i in xrange(bins):
        angle = -180 + binSize * i
        if 0 <= angle < 120:
            print '\nREM Angle: {:3.0f}'.format(angle)
            model.makeRotamer(['H12A', 'H12B', 'H12C'], ['C11', 'C12'], angle, None)





def run(pluginManager):
    """
    This is the entry point for the plugin manager.
    The plugin manager will pass a reference to itself
    to the function.
    Use the APD_Printer instance returned by
    pluginManager.setup() instead of the 'print'
    statement to generate autoformated cmd line output.
    :param pluginManager: Reference to the plugin manager
    instance.
    """
    printer = pluginManager.setup()
    # pluginManager.call('dcd')
    # exit()
    if pluginManager.arg('blank'):
        printer('Append to FVAR:')
        return makeBlankFile(pluginManager)



    # import sys
    #
    # sys.path.append('/home/jens/Laue-Script/projects/Torizo/torizo/src')

    import MDAnalysis.coordinates
    dcd = MDAnalysis.coordinates.reader(pluginManager.arg('load'))

    Natoms = guessMoleculeSize(pluginManager.arg('psf'))
    printer('{} atoms found.'.format(Natoms))
    Nframes = float(len(dcd))
    atomIndices = [int(i) for i in pluginManager.arg('torsion')]
    binBox = BinBox(int(pluginManager.arg('bins')))
    printer('\nProcessing trajectory file \'{}\':'.format(pluginManager.arg('load')))
    printer.create_progressbar(length=69)
    full = pluginManager.arg('full')
    for fNum, frame in enumerate(dcd):
        if not fNum % 100:
            printer.update_progressbar(float(fNum)/Nframes*100)
        for molecule in frame2molecules(frame, Natoms):
            points = np.array([molecule[i] for i in atomIndices])
            binBox.put(dihedral(points))
            if not full:
                break
    printer.finish_progressbar()
    printer('\nBins: {}'.format(' '.join(['{:4.2f}'.format(value) for value in binBox.harvest()])))
    printer('\nReading model data:')
    model = ExpModel(pluginManager.arg('model'), pluginManager)
    model.setRotamerGroup(['H12A', 'H12B', 'H12C'], ['C11', 'C12'], ['O3', 'C11', 'C12', 'H12A'])
    printer('\nGenerated Shelxl input:')
    for i, bin in enumerate(binBox.harvest()):
        angle = binBox.binSize*i%360
        # if 0 <= angle <= 120:
        print '\nREM Angle: {:4} Occ: {:3.0f} %'.format(angle, bin*100)
        model.makeRotamer(['H12A', 'H12B', 'H12C'], ['C11', 'C12'], angle, bin)


class BinBox(object):
    def __init__(self, Nbins=12):
        if 360 % Nbins:
            raise BinSizeError
        self.Nbins = Nbins
        self.binSize = 360/Nbins
        self.binWidth = float(self.binSize / 2.)
        self.bins = [0] * Nbins

    def put(self, angle):
        # angle += 180
        angle = angle if angle > 0 else 360-angle
        # angle += 180
        binNum = int(round(angle/self.binSize))
        binNum = (binNum + 1) % self.Nbins if angle % self.binSize > self.binWidth else binNum % self.Nbins
        # print angle, binNum
        self.bins[binNum] += 1

    def harvest(self):
        binSum = float(sum(self.bins))
        return [float(bin)/binSum for bin in self.bins]


class BinSizeError(Exception):
    pass


class ExpModel(object):
    def __init__(self, filename, pluginManager):
        self.molecule = quickLoad(pluginManager, filename)
        self.counter = 0

    def makeRotamer(self, atoms, axis, angle, occ=0.25):
        angle += self.dihedralAngle
        axisDir = self.molecule[axis[0]].cart - self.molecule[axis[1]].cart
        axisDir /= np.linalg.norm(axisDir)
        letters = ('A', 'B', 'C')
        if not occ == None:
            print 'PART {} 1{:4.2f}'.format(self.counter+1, occ)
        else:
            print 'PART {} {}1.0'.format(self.counter+1, self.counter + 2)
        for i, atomName in enumerate(atoms):
            newAtom = deepcopy(self.molecule[atomName])
            newAtom.cart = rotate_point_about_axis(newAtom.cart, angle, axisDir, self.molecule[axis[0]].cart)
            newADP = rotate_ADP_about_axis(newAtom.adp['cart_meas'], angle, axisDir)
            # newADP = rotate_ADP_about_axis((.01,.1,.05,0,0,0) if not i else (0,0,0,0,0,0), angle, axisDir)
            newADP = cart2frac_ADP(newADP, self.molecule.get_cell())
            # print np.linalg.eig(get_adp_as_matrix(cart2frac_ADP(newADP, self.molecule.get_cell())))[0]
            newADP = xdADP2shelxADP(newADP)
            print 'H{}{}'.format(12+self.counter, letters[i]), '2', ' '.join(['{:9.6f}'.format(c + 10) for c in cart2frac(newAtom.cart, self.molecule.get_cell())]), '10.    =\n    ', ' '.join(['{:8.5f}'.format(c + 10) for c in newADP])
        self.counter += 1

    def normalizeRotamer(self):
        self.normalAtoms = []
        for atomName in self.dihedralAtoms:
            normalAtom = deepcopy(self.molecule[atomName])
            normalAtom.set_cart(rotate_point_about_axis(normalAtom.get_cart(), self.dihedralAngle*-1, self.axisDir, self.axisOrigin))
            normalAtom.adp['cart_meas'] = rotate_ADP_about_axis(normalAtom.adp['cart_meas'], self.dihedralAngle*-1, self.axisDir)
            self.normalAtoms.append(normalAtom)

    def setRotamerGroup(self, atoms, axis, dihedralAtoms):
        axisDir = self.molecule[axis[0]].cart - self.molecule[axis[1]].cart
        self.axisDir = axisDir / np.linalg.norm(axisDir)
        self.axisOrigin = self.molecule[axis[0]].cart
        self.rotamer = list(atoms)
        self.dihedralAtoms = dihedralAtoms
        self.dihedralAngle = dihedral(np.array([self.molecule[i].get_cart() for i in self.dihedralAtoms]))
        self.normalizeRotamer()


def xdADP2shelxADP(adp):
    return adp[0], adp[1], adp[2], adp[5], adp[4], adp[3]


# def rotate_point_about_axis(point, angle, axisDirection, axisOrigin=(0, 0, 0)):
#     """
#     Rotates a point about an axis by a given angle.
#     :param point: list type containing three floats representing a point in cartesian space. (x, y ,z)
#     :param angle: float representing the angle the point is about to be rotated in degree.
#     :param axisDirection: list type containing three floats representing the direction of the vector
#     the point is rotated about. (x, y, z)
#     :param axisOrigin: list type containing three floats representing a point on the axis the point is
#     rotated about. (x, y, z)
#     :return: numpy.array representing the rotated point. (x, y, z)
#     """
#     from numpy import sin, cos, pi
#     t = angle * (pi/180)
#     x, y, z = point[0], point[1], point[2]
#     a, b, c = axisOrigin[0], axisOrigin[1], axisOrigin[2]
#     axisDirection /= np.linalg.norm(axisDirection)
#     u, v, w = axisDirection[0], axisDirection[1], axisDirection[2]
#     xx = (a*(v**2+w**2)-u*(b*v+c*w-u*x-v*y-w*z)) * (1-cos(t)) + x*cos(t) + (-1*c*v+b*w-w*y+v*z) * sin(t)
#     yy = (b*(u**2+w**2)-v*(a*u+c*w-u*x-v*y-w*z)) * (1-cos(t)) + y*cos(t) + ( 1*c*u-a*w+w*x-u*z) * sin(t)
#     zz = (c*(u**2+v**2)-w*(a*u+b*v-u*x-v*y-w*z)) * (1-cos(t)) + z*cos(t) + (-1*b*u+a*v-v*x+u*y) * sin(t)
#     return np.array((xx, yy, zz))
#
#
# def rotate_ADP_about_axis(ADP, angle, axisDirection):
#     """
#     Rotates an ADP about an axis by a given angle.
#     :param ADP: list type containing six floats representing an ADP in XD format. (U11, U22, U33, U12, U13, U23)
#     :param angle: float representing the angle the point is about to be rotated in degree.
#     :param axisDirection: list type containing three floats representing the direction of the vector
#     the point is rotated about. (x, y, z)
#     :return: tuple containing six floats representing the rotated ADP.
#     """
#     from lauescript.cryst.match import get_transform
#     adp = get_adp_as_matrix(ADP)
#     u, v = np.linalg.eig(adp)
#     startPoints = [v[:, i].flatten().tolist()[0] for i in xrange(3)]
#     endPoints = [rotate_point_about_axis(point, angle, axisDirection, (0, 0, 0)) for point in startPoints]
#     rotMat = get_transform(startPoints, endPoints, matrix=True).transpose()
#     newadp = np.dot(rotMat.transpose(), np.dot(adp, rotMat))
#     return newadp[0, 0], newadp[1, 1], newadp[2, 2], newadp[0, 1], newadp[0, 2], newadp[1, 2]


