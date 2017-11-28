#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Based on https://github.com/kennethreitz/setup.py.

# Note: To use the 'upload' functionality of this file, you must:
#   $ pip install twine

# import io
import os
from shutil import rmtree
import sys

from setuptools import Command, setup

# Package meta-data.
NAME = 'covimerage'
DESCRIPTION = 'Generate coverage information for Vim scripts.'
URL = 'https://github.com/Vimjas/covimerage'
# EMAIL = 'me@example.com'
AUTHOR = 'Daniel Hahler'

# What packages are required for this module to be executed?
REQUIRED = ['attrs', 'click', 'coverage']

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.rst' is present in your MANIFEST.in
# file!
# with io.open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
#     long_description = '\n' + f.read()

# Load the package's __version__.py module as a dictionary.
about = {}
with open(os.path.join(here, NAME, '__version__.py')) as f:
    exec(f.read(), about)


class PublishCommand(Command):
    """Support setup.py publish."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution…')
        os.system('{0} setup.py sdist bdist_wheel --universal'.format(
            sys.executable))

        self.status('Uploading the package to PyPi via Twine…')
        os.system('twine upload dist/*')

        sys.exit()


DEPS_QA = [
    'flake8',
    'flake8-isort',
    'flake8-quotes',
]
DEPS_TESTING = [
    'pytest>=3.3.0',
    'pytest-cov',
    'pytest-mock',
]

# Where the magic happens:
setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    # long_description=long_description,
    author=AUTHOR,
    # author_email=EMAIL,
    url=URL,
    packages=['covimerage'],
    entry_points={
        'console_scripts': ['covimerage=covimerage.cli:main'],
    },
    install_requires=REQUIRED,
    extras_require={
        'testing': DEPS_TESTING,
        'dev': DEPS_TESTING + DEPS_QA + [
            'pdbpp',
            'pytest-pdb',
        ],
        'qa': DEPS_QA,
    },
    include_package_data=True,
    license='MIT',
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
    # $ setup.py publish support.
    cmdclass={
        'publish': PublishCommand,
    },
)
