# @file setup.py
#
# Copyright (C) 2017 Metaswitch Networks

from setuptools import setup

setup(
    name='cw_infrastructure',
    version='1.0',
    install_requires=[
        "nsenter",
        "argparse",
        "contextlib2",
        "pathlib",
        "dnspython",
    ],
    packages=['cw_infrastructure'])
