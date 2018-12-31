#!/usr/bin/env python
#
# Copyright (c) 2019 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from setuptools import setup, find_packages
import sys

if sys.version_info < (3,6,0):
    sys.exit('Atelier requires Python 3.6 or newer.')

# allow the in-place import of the version
sys.path.insert(0, 'src')
from atelier import version

setup(name='atelier',
      version=version,
      author='Stefan Seefeld',
      author_email='stefan@seefeld.name',
      maintainer='Stefan Seefeld',
      maintainer_email='stefan@seefeld.name',
      description='Atelier is a graphical frontend to faber.',
      url='https://stefanseefeld.github.io/faber',
      download_url='https://github.com/stefanseefeld/faber/releases',
      license='BSL',
      classifiers = ['Environment :: X11 Applications :: Qt',
                     'Intended Audience :: Developers',
                     'License :: OSI Approved :: Boost Software License 1.0 (BSL-1.0)',
                     'Operating System :: OS Independent',
                     'Topic :: Software Development :: Build Tools',
                     'Topic :: Software Development :: Testing',
                     'Programming Language :: Python'],
      package_dir={'':'src'},
      packages=find_packages('src/atelier'),
      install_requires=['PyQt5', 'graphviz', 'pygments'],
      scripts=['scripts/atelier'],
      )
