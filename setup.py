# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from version import get_git_version

with open('README.md') as f:
    readme = f.read()

with open('requirements.txt') as f:
    install_requires = f.read().splitlines()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='ths-tools',
    version=get_git_version(),
    description='Tools for interacting with the API of the Treuhandstelle Greifswald',
    long_description=readme,
    #author='',
    #author_email='',
    url='https://github.com/osaris-dev/ths-tools',
    license=license,
    packages=['ths_tools'],
    install_requires=install_requires,
    entry_points = {
        "console_scripts": [
            "ths-tools = ths_tools:ths_tools_cli"
        ]
    },
)
