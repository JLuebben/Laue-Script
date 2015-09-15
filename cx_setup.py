"""
cx_freeze setup script for compiling an executable software package.
"""

import sys
import os
import subprocess
from cx_Freeze import setup, Executable


def get_version_info():
    """
    Recovers the current SVN version number from the SVN server.
    :return: String representing the current SVN version number.
    """
    p = subprocess.Popen("svn info svn://134.76.64.183/APD-Toolkit/APD-toolkit | grep \"Revision\" | awk '{print $2}'",
                         stdout=subprocess.PIPE,
                         shell=True)
    (output, err) = p.communicate()
    return str(output)

includefiles = ['apd/data/', 'apd/examplePlugins']
build_exe_options = {"packages": ["os", 'apd'], "create_shared_zip": True, "compressed": True,
                     'optimize': 3, 'excludes': ['tkinter', 'pygame', 'matplotlib', 'scipy', 'tcl'],
                     'include_files': includefiles}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

svn_version = get_version_info()
full_version = "0.{}".format(svn_version)

print 'Creating APD-Tookit version {}'.format(full_version)
bkp = sys.stdout
sys.stdout = open(os.devnull, 'w')


setup(name="APD-Tookit",
      version=full_version,
      author='Jens Luebben',
      author_email='jens.luebben@chemie.uni-goettingen.de',
      url='http://ewald.ac.chemie.uni-goettingen.de/',
      description="A program for estimating anisotropic displacement parameters for hydrogen atoms.",
      options={"build_exe": build_exe_options},
      executables=[Executable("bin/apdtoolkit", base=base,)])

sys.stdout = bkp
print 'Creation successful.'
