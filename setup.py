#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Based on https://github.com/kennethreitz/setup.py.

# Note: To use the 'upload' functionality of this file, you must:
#   $ pip install twine

import os
from shutil import rmtree
import sys

from setuptools import Command, setup

here = os.path.abspath(os.path.dirname(__file__))


def read(fname):
    with open(fname) as f:
        return f.read()


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
    'flake8>=3.7.0',
    'flake8-isort',
]
DEPS_TESTING = [
    'pytest>=3.3.0',
    'pytest-mock',
]

setup(
    name='covimerage',
    description='Generate coverage information for Vim scripts.',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    author='Daniel Hahler',
    url='https://github.com/Vimjas/covimerage',
    packages=['covimerage'],
    entry_points={
        'console_scripts': ['covimerage=covimerage.cli:main'],
    },
    use_scm_version={
        'write_to': 'covimerage/__version__.py',
    },
    setup_requires=[
        'setuptools_scm',
    ],
    install_requires=[
        'attrs>=16.1.0',
        'click',
        'coverage<5.0a6',
    ],
    extras_require={
        'testing': DEPS_TESTING,
        'dev': DEPS_TESTING + DEPS_QA + [
            'pdbpp',
            'pytest-pdb',
        ],
        'qa': DEPS_QA,
    },
    include_package_data=True,
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
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
    # $ setup.py publish support.
    cmdclass={
        'publish': PublishCommand,
    },
)
