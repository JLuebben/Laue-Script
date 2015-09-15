__author__ = 'Arrahed'

import imp
from tools.lib.projectmanager import ProjectManager
from tools.lib.importresolver import ImportResolver
import os
import shutil


def main():
    projectManager = ProjectManager()
    setupScript = imp.load_source('setup', './setup.py')
    verbose = projectManager.arg('-v')
    if projectManager.arg('build'):
        if verbose:
            print 'Building project \'{}\''.format(setupScript.projectName)
            importResolver = ImportResolver(projectManager.getProjectsDirectory() +
                                            '/{}'.format(setupScript.projectName))
            importResolver.resolve()
            os.removedirs('build')
            # os.makedirs('build')
            shutil.copytree(imp.find_module('lauescript')[1], './build/')
            # for f in importResolver.primaryFiles:
            #     shutil.copyfile(f, './build/{}'.format(''.join(f.partition('lauescript')[1:])))


if __name__ == '__main__':
    main()