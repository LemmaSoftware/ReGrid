#!/usr/bin/env python
import sys
from setuptools import setup, Extension

setup(name='ReGrid',
      version='0.0.2',
      description='Grid conversion utilities for multiphase flow modelling software',
      author='Trevor P. Irons',
      author_email='Trevor.Irons@egi.utah.edu',
      url='https://git.lemmasofware.org/co2/ReGrid',
      setup_requires=[
        'setuptools>=18.0',
      ],
      install_requires=[
          'matplotlib',
          'scipy',
          'numpy',
          'cmocean',
#          'vtk'
      ],
      packages=['regrid', 'regrid.flowgrid'],
      license=['GPL 4.0'],
)
