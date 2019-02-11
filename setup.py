from setuptools import setup


DEPS_QA = [
    'flake8',
    'flake8-isort',
    'flake8-per-file-ignores',
]
DEPS_TESTING = [
    'pytest>=3.3.0',
    'pytest-mock',
]


setup(
    name='covimerage',
    author='Daniel Hahler',
    url='https://github.com/Vimjas/covimerage',

    setup_requires=['setupmeta'],
    versioning='post',

    install_requires=[
        'attrs',
        'click',
        'coverage',
    ],
    tests_require=DEPS_TESTING,
    extras_require={
        'testing': DEPS_TESTING,
        'dev': DEPS_TESTING + DEPS_QA + [
            'pdbpp',
            'pytest-pdb',
        ],
        'qa': DEPS_QA,
    },
    entry_points={
        'console_scripts': ['covimerage=covimerage.cli:main'],
    },
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
)
