
from os.path import expanduser, isfile, join, realpath, dirname
from sys import argv
import lauescript.core.pluginmanager as pluginmanager


def main():
    """
    Creates an instance of the plugin manager and configures is
    appropriately.
    After configuration the plugin manager is executed.
    """
    if 'help' in argv:
        print '\n\n########################################################################################\n'              '#                                         myProject                                           #\n'              '########################################################################################\n'
        print 'A program for '
        exit()
    argvs=argv[0:1]+['-myProject']+argv[1:]
    config_file = expanduser(join('~', '.myProject.ini'))
    if not isfile(config_file):
        from lauescript.makeconfig import run
        run(outputName='~/.myProject.ini',
            data_path=join(dirname(dirname(dirname(dirname(realpath(__file__))))), join('lauescript', 'data')),
            plugin_path=join(dirname(dirname(realpath(__file__))), join('myproject', 'src')))
    pm = pluginmanager.PluginManager(argvs=argvs,
                                  headline='                              myProject                              ',
                                bottomline='                          Exiting myProject                          ',
                                headlines=False,
                                config=config_file,
                                macro_file=False)
    pm.execute()
    exit()
