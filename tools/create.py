__author__ = 'jens'


import os
import stat
from tools.lib.projectmanager import ProjectManager
from sys import argv


def main():
    projectManager = ProjectManager(mode='create')
    projectPath = projectManager.getProjectsDirectory()
    if len(argv) < 2:
        print('Please specify the name of the project.')
        exit(1)
    newName = argv[1]
    if projectManager.projectExists(newName):
        print('Project files with this name already exist.')
        exit(2)
    projectPath += '/{}'.format(newName)
    makeFiles(projectPath, newName)
    print('****** Created project: \'{}\' ******'.format(argv[1]))
    print( 'Project files are located in \'{}\''.format(projectPath))
    print( 'To execute your program you will have to add \'{}\'\nto your PYTHONPATH environment variable.' \
          ' The executable is located in the \'bin\' subdirectory.\n' \
          'To add code to your project edit the *.py file created in the \'source\' subdirectory.'.format(projectPath))
    print( 'Have fun!')


def makeFiles(rootPath, projectName):
    mainPath = rootPath+'/{}'.format(projectName.lower())
    binPath = rootPath+'/bin'
    sourcePath = mainPath+'/src'
    os.makedirs(mainPath)
    os.makedirs(binPath)
    os.makedirs(sourcePath)
    with open(rootPath+'/__init__.py', 'w') as fp:
        pass
    with open(mainPath+'/__init__.py', 'w') as fp:
        pass

    with open(rootPath+'/setup.py', 'w') as fp:
        fp.write(makeSetupFile(projectName))

    with open(mainPath+'/{}_main.py'.format(projectName), 'w') as fp:
        fp.write(makeMainFile(projectName))

    with open(sourcePath+'/{}.py'.format(projectName), 'w') as fp:
        fp.write(makeSourceFile(projectName))

    with open(binPath+'/{}'.format(projectName), 'w') as fp:
        fp.write(makeExecutable(projectName))
    os.chmod('{}'.format(binPath+'/{}'.format(projectName)), stat.S_IRWXU)


    # iniPath = os.path.expanduser('~/.{0}.ini'.format(projectName))
    # with open(iniPath, 'w') as fp:
    #    fp.write(makeIniFile(projectName,rootPath))


def makeExecutable(projectName):
    pN = projectName.lower()
    return '''#!/usr/bin/python

if __name__ == '__main__':
    try:
        from {0}.{1}_main import main
    except ImportError:
        print( 'ImportError: Main module not found. Please check if PYTHONPATH ist set up correctly.'

        print( 'Trying to guess project path. Even if this works, please try to fix PYTHONPATH.'
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
        try:
            from {0}.{1}_main import main
        except ImportError:
            print( 'Nope. Not working. Nothing more I can do.'
            exit(1)
        else:
            main()
            exit(0)
    main()
'''.format(pN, projectName)


def makeSetupFile(projectName):
    return '''
projectName = '{}'
'''.format(projectName)


def makeMainFile(projectName):
    return '''
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
        print( '\\n\\n########################################################################################\\n'\
              '#                                         {0}                                           #\\n'\
              '########################################################################################\\n'
        print( 'A program for '
        exit()
    argvs=argv[0:1]+['-{0}']+argv[1:]
    config_file = expanduser(join('~', '.{0}.ini'))
    if not isfile(config_file):
        from lauescript.makeconfig import run
        run(outputName='~/.{0}.ini',
            data_path=join(dirname(dirname(dirname(dirname(realpath(__file__))))), join('lauescript', 'data')),
            plugin_path=join(dirname(dirname(realpath(__file__))), join('{1}', 'src')))
    pm = pluginmanager.PluginManager(argvs=argvs,
                                  headline='                              {0}                              ',
                                bottomline='                          Exiting {0}                          ',
                                headlines=False,
                                config=config_file,
                                macro_file=False)
    pm.execute()
    exit()
'''.format(projectName, projectName.lower())


def makeSourceFile(projectName):
    return '''
__author__ = ''

KEY = '{}'  # Edit this to control which cmd line keyword starts the plugin.
OPTION_ARGUMENTS = {}  # Edit this to define cmd line options for
# the plugin and their default values.
from lauescript.core.core import *

def run(pluginManager):
    """
    This is the entry point for the plugin manager.
    The plugin manager will pass a reference to itself
    to the function.
    Use the APD_Printer instance returned by
    pluginManager.setup() instead of the 'print('
    statement to generate auto-formatted cmd line output.
    :param pluginManager: Reference to the plugin manager
    instance.
    """
    print(er = pluginManager.setup()
'''.format(projectName, '{\'load\': \'myFile.txt\'}')


def makeIniFile(projectName, rootPath):
    path = os.path.realpath(__file__)
    return '''
[Main]
pluginpath = {}/source
'''.format(rootPath)

if __name__ == '__main__':
    main()