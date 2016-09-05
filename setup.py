#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
alkali is a simple database engine. If you're currently using a list of
dicts then you should come take a look. alkali's main goal is to allow
the developer to easily control the on disk format.
"""

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import os
import sys

base_dir = os.path.dirname(os.path.abspath(__file__))
pkg_name = os.path.basename( base_dir )

# trying to make this setup.py as generic as possible
import importlib
module = importlib.import_module( pkg_name )


def get_changelog(filename="CHANGELOG.md"):
    changelog = {}
    current_version = None

    with open(os.path.join(base_dir, filename)) as changelog_file:
        for line in changelog_file.readlines():

            if line.startswith("* __"):
                parts = line.strip("* ").split(" ", 1)

                if len(parts) == 2:
                    current_version, changes = parts[0].strip("_\n"), parts[1]
                    changelog[current_version] = [changes.strip()]
                else:
                    current_version = parts[0].strip("_\n")
                    changelog[current_version] = []

            elif line.strip() and current_version and not line.startswith("#"):
                changelog[current_version].append(line.strip(" *\n"))

    return changelog

def dist_pypi():
    os.system("python setup.py sdist upload")
    sys.exit()

def dist_github():
    """Creates a release on github"""
    import requests
    import keyring
    import getpass

    version = module.__version__
    version_tuple = version.split(".")

    print("preparing release {}...".format(version))

    # TODO convert this to a function
    changes_since_last_version = ["* __{}__: {}".format(key, "\n".join(changes)) for key, changes in get_changelog().items() if key.startswith("{}.{}".format(*version_tuple))]
    changes_since_last_version = "\n".join(sorted(changes_since_last_version, reverse=True))

    payload = {
        "tag_name"         : version,
        "target_commitish" : "master",
        "name"             : version,
        "body"             : "changes in version {}.{} : \n\n{}".format(version_tuple[0], version_tuple[1], changes_since_last_version)
    }

    username = keyring.get_password("github", "__default_user") or raw_input("Github username: ")
    password = keyring.get_password("github", username) or getpass.getpass()
    url = "https://api.github.com/repos/{}/{}/releases".format(username,pkg_name)
    auth = (username, password)

    otp = raw_input("One Time Token: ")

    response = requests.post(url, headers={"X-GitHub-OTP": otp}, json=payload, auth=auth)
    if response.status_code in (403, 404):
        print("Authentication error.")
    else:
        keyring.set_password("github", "__default_user", username)
        keyring.set_password("github", username, password)

        if response.status_code > 299:
            if  "message" in response.json():
                print("error: {}".format(response.json()['message']))

                for error_dict in response.json().get('errors', []):
                    print("*", error_dict)
            else:
                print("Unkown error")
                print(response.text)
        else:
            print("release created")
    sys.exit()

if sys.argv[-1] == 'publish':
    dist_pypi()

if sys.argv[-1] == 'github_release':
    dist_github()

conditional_dependencies = {}

setup(
    name = pkg_name,
    packages = [pkg_name],

    install_requires = open('requirements.txt').readlines(),

    extras_require = {
        'dev': open('req_tests.txt').readlines(),
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
