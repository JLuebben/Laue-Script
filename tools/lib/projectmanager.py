__author__ = 'jens'

try:
    from ConfigParser import ConfigParser, NoSectionError
except ImportError:
    from configparser import ConfigParser, NoSectionError
from os.path import expanduser, isdir
from sys import argv


class ProjectManager(object):
    def __init__(self, mode=None):
        self.options = {}
        self.exePath = ''
        self.configPath = expanduser('~/.laue_script.ini')
        self.config = ConfigParser()
        try:
            self.config.read(self.configPath)
            self.config.items('Projects')
        except NoSectionError:
            self._make_config()
            self.config.read(self.configPath)
        if not mode == 'create':
            self._parseArgs()

    def getProjectsDirectory(self):
        return self.config.get('Projects', 'ProjectPath')

    def projectExists(self, projectName):
        return isdir(self.getProjectsDirectory() + '/{}'.format(projectName))

    def _make_config(self):
        conf = ConfigParser()
        conf.add_section('Projects')
        conf.add_section('Options')
        conf.set('Projects', 'ProjectPath', expanduser('~/Laue-Script/projects'))
        conf.set('Options', '-p', 'true')
        conf.set('Options', '-v', 'false')
        conf.set('Options', 'build', 'false')
        with open(expanduser('~/.laue_script.ini'), 'w') as fp:
            conf.write(fp)

    def _parseArgs(self):
        self.options = {}
        parser = FirstParser(self)
        items = {item[0]: item[1] for item in self.config.items('Options')}
        for string in argv:
            try:
                parser = parser(string, items)
            except ArgParseError:
                print( 'Exiting gracefully after argument parsing error.')
                exit()
        try:
            parser.validate()
        except ArgParseError:
            print( 'Exiting gracefully...')
            exit()

    def arg(self, string):
        try:
            return self.options[string]
        except KeyError:
            return False


class Parser(object):
    def __init__(self, manager):
        self.manager = manager

    def __call__(self, string, items):
        return self

    def validate(self):
        pass


class FirstParser(Parser):
    def __call__(self, string, _):
        self.manager.exePath = string
        return DefaultParser(self.manager)


class DefaultParser(Parser):
    def __call__(self, string, items):
        try:
            if items[string] == 'True':
                return ArgumentParser(self.manager, string)
            else:
                self.manager.options[string] = True
                return self
        except KeyError:
            print( '\'{}\' not recognised.'.format(string))
            raise ArgParseError


class ArgumentParser(Parser):
    def __init__(self, manager, option):
        self.manager = manager
        self.option = option

    def __call__(self, string, items):
        self.manager.options[self.option] = string
        return DefaultParser(self.manager)

    def validate(self):
        print( 'Error: Missing argument for option {}'.format(self.option))
        raise ArgParseError


class ArgParseError(Exception):
    pass



if __name__ == '__main__':
    pm = ProjectManager()
    print( pm.arg('-p'))
    print( pm.arg('-v'))
    print( pm.arg('build'))
