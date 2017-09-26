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

from check_config_utilities import OK, WARNING, ERROR, error, warning

option_module_path = "/usr/share/clearwater/infrastructure/scripts/config_validation"


def check_config(options):
    status = 0

    # Check that each option is present (if mandatory) and correctly formatted (if
    # it has a particular format we wish to check).
    for option in options:
        value = os.environ.get(option.name)

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


def import_option_modules():
    """Retrieve and import option modules from the options/ directory"""
    options_path = os.path.join(option_module_path, '*.py')
    option_pairs = [(os.path.split(path)[1], path) for path in glob(options_path)]
    option_modules = [imp.load_source(name, path) for (name, path) in option_pairs]
    return option_modules


# Retrieve and import option modules
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    option_modules = import_option_modules()

# Build up the list of options to be validated
options = []
for module in option_modules:
    options += module.get_options()

status = OK

# Validate the options in this list
code = check_config(options)
if code > status:
    status = code

# Run advanced config checks in each option module
for module in option_modules:
    code = module.check_advanced_config()
    if code > status:
        status = code

sys.exit(status)
