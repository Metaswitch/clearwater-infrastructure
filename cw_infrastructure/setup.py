# @file setup.py
#
# Copyright (C) 2017 Metaswitch Networks

from setuptools import setup

setup(
    name='cw_infrastructure',
    version='1.0',
    install_requires=[
        "nsenter==0.2",
        "argparse==1.4.0",
        "contextlib2==0.5.5",
        "pathlib==1.0.1",
        "dnspython==1.15.0",
    ],
    packages=['cw_infrastructure'])
