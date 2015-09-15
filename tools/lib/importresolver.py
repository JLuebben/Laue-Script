__author__ = 'jens'
import os
import glob
import imp


class ImportResolver(object):
    def __init__(self, root):
        self.modules = {}
        self.root = root
        self.primaryFiles = set()
        self.imports = set()
        self.secondaryFiles = set()

    def resolve(self):
        print 'Identifying dependencies.'
        for currentRoot, dirnames, filenames in os.walk(self.root):
            pyFiles = glob.glob(currentRoot + '/*.py')
            for pyFile in pyFiles:
                self.primaryFiles.add(pyFile)

        # for currentRoot, dirnames, filenames in os.walk(imp.find_module('lauescript')[1]):
        #     pyFiles = glob.glob(currentRoot + '/*.py')
        #     for pyFile in pyFiles:
        #         self.primaryFiles.add(pyFile)

        setSize = -1
        fileList = set(self.primaryFiles)
        newFiles = set(fileList)
        while True:
            if len(fileList) == setSize:
                break
            self.imports = self.imports.union(self.findImports(fileList))
            newImports = self.findImports(newFiles)
            setSize = len(fileList)
            fileList = fileList.union(self.expandImports(newImports))
            newFiles = self.expandImports(newImports)
            fileList = fileList.union(newFiles)
            self.imports = self.imports.union(newImports)
        self.secondaryFiles = fileList.difference(self.primaryFiles)
        print '{} source files identified.'.format(len(fileList))

    def findImports(self, fileList):
        newImports = set()
        for pyFile in fileList:
            try:
                fp = open(pyFile, 'r')
                for line in fp.readlines():
                    line = line.lstrip().rstrip('\n\r')
                    if line.startswith('#'):
                        continue
                    if line.startswith('import '):
                        newImports.add([i for i in line.split(' ') if i and not '{' in i][1])
                    elif line.startswith('from ') and 'import' in line:
                        newImports.add([i for i in line.split(' ') if i and not '{' in i][1])
            except IOError as error:
                if '[Errno 21]' in str(error):
                    newImports.add(pyFile)
                else:
                    pass
                    # print error
                    # exit(1)
            else:
                fp.close()
        return newImports

    def expandImports(self, imports):
        fileNames = set()
        for moduleName in imports:
            try:
                fileNames.add(self.find_dotted_module(moduleName))
            except ImportError as error:
                pass
                # print '***Warning: Module {} not found.'.format(moduleName)
        return fileNames

    def find_dotted_module(self, name, path=None):
        """
        Example: find_dotted_module('mypackage.myfile')

        Background: imp.find_module() does not handle hierarchical module names (names containing dots).

        Important: No code of the module gets executed. The module does not get loaded (on purpose)
        ImportError gets raised if the module can't be found.

        Use case: Test discovery without loading (otherwise coverage does not see the lines which are executed
                  at import time)
        """

        for x in name.split('.'):
            if path is not None:
                path = [path]
            filename, path, descr = imp.find_module(x, path)
        return path




if __name__ == '__main__':
    iR = ImportResolver('/home/jens/Laue-Script')
    iR.resolve()