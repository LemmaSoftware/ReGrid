#!/usr/bin/env python
import sys
from setuptools import setup, Extension
from setuptools.command.build_py import build_py

try:
    from pyqt_distutils.build_ui import build_ui
except ImportError:
    print("Please install pyqt_distutils")
    print( "(sudo) pip(3) install pyqt-distutils")
    exit()

class custom_build_py(build_py):
    def run(self):
        self.run_command('build_ui')
        build_py.run(self)


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='ReGrid',
      version='0.0.2',
      description='Grid conversion utilities for multiphase flow modelling software',
      author='Trevor P. Irons',
      author_email='Trevor.Irons@egi.utah.edu',
      url='https://git.lemmasofware.org/co2/ReGrid',
      setup_requires=[
        'pyqt_distutils',
        'PyQt5',
        'setuptools>=18.0',
      ],
      install_requires=[
          'matplotlib',
          'scipy',
          'numpy',
          'cmocean',
#          'vtk'
      ],
      packages=['regrid', 'regrid.flowgrid','regrid.gui'],
      # for forced build of pyuic
      cmdclass={
          'build_ui': build_ui,
          'build_py': custom_build_py,
      },
      license=['GPL 4.0'],
)
