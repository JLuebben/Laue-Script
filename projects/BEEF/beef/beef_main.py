"""
Created on May 16, 2014

@author: Jens Luebben

Module for configuring and instantiating the plugin manager
for using the crosscheck.py module as a stand alone program.
"""
from os.path import expanduser
from sys import argv

import lauescript.core.pluginmanager as pluginmanager


def main():
    """
    Creates an instance of the plugin manager and configures is
    appropriately.
    After configuration the plugin manager is executed.
    """
    if 'help' in argv:
        print '\n\n########################################################################################\n'\
              '#                                         BEEF                                           #\n'\
              '########################################################################################\n'
        print 'A program for '
        exit()
    argvs=argv[0:1]+['-BEEF']+argv[1:]
    config_file = expanduser('~/.beef.ini')
    pm = pluginmanager.PluginManager(argvs=argvs,
                                  headline='                              BEEF                              ',
                                bottomline='                          Exiting BEEF                          ',
                                headlines=False,
                                config=config_file,
                                macro_file=False)#config_file.DatabasePath+'/crosscheck.mcr')
    pm.execute()
    exit()

