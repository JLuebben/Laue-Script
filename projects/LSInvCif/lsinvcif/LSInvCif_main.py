
from os.path import expanduser
from sys import argv
from sys import exit
import lauescript.core.pluginmanager as pluginmanager


def main():
    """
    Creates an instance of the plugin manager and configures is
    appropriately.
    After configuration the plugin manager is executed.
    """
    if 'help' in argv:
        print '\n\n########################################################################################\n'              '#                                         LSInvCif                                           #\n'              '########################################################################################\n'
        print 'A program for '
        exit()
    argvs=argv[0:1]+['-LSInvCif']+argv[1:]
    config_file = expanduser('~/.LSInvCif.ini')
    pm = pluginmanager.PluginManager(argvs=argvs,
                                  headline='                              LSInvCif                              ',
                                bottomline='                          Exiting LSInvCif                          ',
                                headlines=False,
                                config=config_file,
                                macro_file=False)
    pm.execute()
    exit()
