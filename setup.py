#!/usr/bin/env python3

"""DocManager Setup


See also:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

import sys
from os import path, environ
# To use a consistent encoding
from codecs import open

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


here = path.abspath(path.dirname(__file__))

class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)

setupdict = dict(
    name='docmanager',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='3.1.0',

    description='Manage Meta Information in DocBook5-XML Files',
    # long_description=long_description,

    # The project's main homepage.
    url='https://github.com/openSUSE/docmanager',

    # Author details
    author='Rick Salevsky',
    author_email='rsalevsky@suse.de',

    # Choose your license
    license='GPL-3.0',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',

        # Indicate who your project is intended for
        'Topic :: Documentation',
        'Topic :: Software Development :: Documentation',
        'Intended Audience :: Developers',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',

        # Supported Python versions
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],

    # What does your project relate to?
    keywords='docbook5 metainformation',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['contrib', 'docs']),

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=['lxml'],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    #extras_require={
    #    'dev': ['check-manifest'],
    #    'test': ['coverage'],
    #},

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    package_data={
        'docmanager': ['template/*'],
    },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    # data_files=[('my_data', ['data/data_file'])],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'docmanager=docmanager:main',
        ],
    },

    # Required packages for testing
    tests_require=['pytest'],

    #
    cmdclass = {'test': PyTest},
)


# Only use this for Travis:
# From http://docs.travis-ci.com/user/environment-variables/#Default-Environment-Variables
if environ.get('CI') or environ.get('TRAVIS') or hasattr(sys, 'base_prefix'):
    setupdict.update(# data_files specifies a sequence of (directory, files) pairs
        data_files=[
            ('docmanager/', ['docmanager/docmanager.conf']),
            ],
        )

# Call it:
setup(**setupdict)
