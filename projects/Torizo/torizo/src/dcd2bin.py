
__author__ = ''

KEY = 'dcd'  # Edit this to control which cmd line keyword starts the plugin.
OPTION_ARGUMENTS = {'load': 'myFile.txt',
                    'n': 12}  # Edit this to define cmd line options for
# the plugin and their default values.
from lauescript.core.core import *
from subprocess import Popen, PIPE

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
    # binCount = int(pluginManager.arg('n'))
    # newBins = [0] * binCount
    #
    # binSize = 360/binCount
    # binRange = binSize/2
    # testRange = range(0,360,4)
    # for smallBin in testRange:
    #     diff = smallBin % binSize
    #     binNumber = smallBin / binSize
    #     binNumber = (binNumber + 1 if diff > binRange else binNumber)%binCount
    #     newBins[binNumber] += 1
    # printer(newBins)
    p = Popen(['/home/jens/Laue-Script/projects/Torizo/bin/torsion_probability_function.exe'], stdin=PIPE, stdout=PIPE,
              stderr=PIPE, shell=True)
    stdout, stderr = p.communicate('simulation_out\n1\n1\n23\n2 1 6 5\nout.bins\n')
    print stdout
    print stderr

    # p.communicate('10\n')
    # p.communicate('1 2 5 6\n')


