"""
Created on Apr 22, 2014

@author: jens
"""

#from distutils.core import setup
from setuptools import setup,find_packages

setup(name='APD-Toolkit',
      version='0.1.0',
      description='A program for estimating hydrogen ADPs from the invariom database',
      author='Jens Luebben',
      author_email='jens.luebben@chemie.uni-goettingen.de',
      #=========================================================================
      # url='http://www.python.org/sigs/distutils-sig/',
      #=========================================================================
      packages=find_packages(),
      #packages=['apd',
      #          'apd.data',
      #          'apd.examplePlugins',
      #          'apd.lib',
      #          'apd.lib.apdio',
      #          'apd.lib.crystgeom2',
      #          'apd.lib.apdgui',
      #          'bin'],
      py_modules=['config'],
      #data_files=[('apd/data',['apd/data/database.pkl','apd/data/APD_MAP.txt','apd/data/empirical_corrections.txt']),]
                  #('',['sample_script.apd'])],
      package_data={'':['*.txt','*.dat']},
      install_requires=['numpy>=0.1', 'cx_Freeze'],
      setup_requires=['numpy>=0.1'],
     )
