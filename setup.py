# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from version import version
#from distance import __version__


with open('README.rst') as f:
  readme = f.read()

with open('LICENSE') as f:
  license = f.read()

setup(
  name='distance',
  version=version,
  #version=__version__,
  #version='0.0.1',
  description='Sample package for Python-Guide.org',
  long_description=readme,
  author='Aaron Schroeder',
  #author_email='me@kennethreitz.com',
  install_requires = [
    'numpy',
    'pandas',
  ],
  url='https://github.com/aaron-schroeder/py-distance',
  license=license,
  packages=find_packages(exclude=('tests', 'docs'))
)

