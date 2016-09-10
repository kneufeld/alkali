#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
alkali is a simple database engine. If you're currently using a list of
dicts then you should come take a look. alkali's main goal is to allow
the developer to easily control the on disk format.
"""

import os
import sys
from setuptools import setup

base_dir = os.path.dirname(os.path.abspath(__file__))
pkg_name = 'alkali'

# adapted from: http://code.activestate.com/recipes/82234-importing-a-dynamically-generated-module/
def pseudo_import( pkg_name ):
    """
    return a new module that contains the variables of pkg_name.__init__
    """
    init = os.path.join( pkg_name, '__init__.py' )

    # remove imports and 'from foo import'
    lines = open(init,'r').readlines()
    lines = filter( lambda l: not l.startswith('from'), lines)
    lines = filter( lambda l: not l.startswith('import'), lines)

    code = '\n'.join(lines)

    import imp
    module = imp.new_module(pkg_name)

    exec code in module.__dict__
    return module

# trying to make this setup.py as generic as possible
module = pseudo_import(pkg_name)

conditional_dependencies = {}

setup(
    name = pkg_name,
    packages = [pkg_name],

    install_requires = open('requirements.txt').readlines(),

    # use via: pip install -e .[docs]
    extras_require = {
        'dev' : open('req_tests.txt').readlines(),
        'docs': open('req_docs.txt').readlines(),
    },

    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Topic :: Database"
    ],

    # metadata for upload to PyPI
    description = "alkali is a simple database engine",
    long_description = __doc__,
    version = module.__version__,
    author = module.__author__,
    author_email = module.__author_email__,
    license = module.__license__,
    keywords = "database".split(),
    url = module.__url__,

    data_files = [],
)
