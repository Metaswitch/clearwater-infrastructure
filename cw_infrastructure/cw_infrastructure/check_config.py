#
# @file check_config.py
#
# Copyright (C) Metaswitch Networks 2017
# If license terms are provided to you in a COPYING file in the root directory
# of the source code repository by which you are accessing this code, then
# the license outlined in that COPYING file applies to your use.
# Otherwise no rights are granted except for those provided to you by
# Metaswitch Networks in a separate written agreement.

import imp
import sys
import warnings # TODO remove
import os

from glob import glob

from check_config_utilities import OK, WARNING, ERROR

def number_present(*args):
    """Determine the number of configuration items given which are present"""
    config = 0

    for option in args:
        value = os.environ.get(option)
        if value:
            config += 1

    return config


def check_config(options):
    status = 0

    # BEGIN DEBUG CODE TODO: Remove
    config = {}
    with open('shared_config') as myfile:
        for line in myfile:
            name, var = line.partition('=')[::2]
            config[name.strip()] = var
    # END DEBUG CODE TODO: Remove

    # Check that each option is present (if mandatory) and correctly formatted (if
    # it has a particular format we wish to check).
    for option in options:
        # value = os.environ.get(option.name) TODO: Uncomment
        value = config.get(option.name) # TODO: Remove

        if value:
            # The option is present. If it has validator, run it now.
            if option.validator:
                code = option.validator(option.name, value)

                # The validator is responsible for printing an error message.
                if code > status:
                    status = code

        else:
            # The option is not present, which is an error if it's mandatory.
            if option.mandatory():
                error(option.name, 'option is mandatory but not present')
                status = ERROR
            elif option.suggested():
                warning(option.name, 'option is not configured')
                status = WARNING
    return status


def import_option_modules(option_modules):
    """Retrieve and import option modules from the options/ directory"""
    options_path = os.path.join(os.path.dirname(__file__), 'options', '*.py')
    option_pairs = [(os.path.split(path)[1], path) for path in glob(options_path)]
    option_modules = [imp.load_source(name, path) for (name, path) in option_pairs]


# Retrieve and import option modules
option_modules = []
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import_option_modules(option_modules)

# Build up the list of options to be validated
options = []
for module in option_modules:
    options += module.get_options()

# Validate the options in this list
check_config(options)

# Run advanced config checks in each option module
status = OK
for module in option_modules:
    code = module.check_advanced_config()
    if code > status:
        status = code

sys.exit(status)
