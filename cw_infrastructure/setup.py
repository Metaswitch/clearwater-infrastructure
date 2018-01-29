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
    packages=['cw_infrastructure'],
    test_suite='cw_infrastructure.test',
    tests_require=[
        "mock",
        "hypothesis"
    ],
    entry_points={
        'option_schemas': [
            'clearwater = cw_infrastructure:clearwater_options'
        ]
    }
)
