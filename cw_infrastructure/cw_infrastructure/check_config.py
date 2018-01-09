#
# @file check_config.py
#
# Copyright (C) Metaswitch Networks 2017
# If license terms are provided to you in a COPYING file in the root directory
# of the source code repository by which you are accessing this code, then
# the license outlined in that COPYING file applies to your use.
# Otherwise no rights are granted except for those provided to you by
# Metaswitch Networks in a separate written agreement.

import sys
import os
import functools

import clearwater_options
from check_config_utilities import WARNING, ERROR, error, warning


def get_environment_variable(env_var_name):
    return os.environ.get(env_var_name)


def check_config_option(option, value):
    if value:
        # The option is present.
        if option.deprecated():
            # If a deprecated option has been set, warn the user
            warning(option.name,
                    'option has been deprecated')
            code = WARNING
        elif option.validator:
            # If the option has a a validator, run it now.
            code = option.validator(option.name, value)

    else:
        # The option is not present, which is an error if it's mandatory.
        if option.mandatory():
            error(option.name, 'option is mandatory but not present')
            code = ERROR
        elif option.suggested():
            warning(option.name, 'option is recommended but not configured')
            code = WARNING
    return code


def check_config_options(options, fun_get_option_value):
    status = 0

    # Check that each option is present (if mandatory) and correctly formatted
    # (if it has a particular format we wish to check).
    for option in options:
        value = fun_get_option_value(option.name)
        code = check_config_option(option, value)

        # A higher value indicates a worse error.
        status = max(status, code)
    return status


def check_config(options, fun_get_option_value):

    # Build up a list of checks to be performed. Each check should take no
    # arguments and return a status code.
    checks = [functools.partial(check_config_options,
                                options.get_options(),
                                fun_get_option_value),
              options.check_advanced_config]

    # Determine the resultant status code - since ERROR > WARNING > OK, take
    # the maximum.
    return max(check() for check in checks)


if __name__ == '__main__':
    sys.exit(check_config(clearwater_options, get_environment_variable))
