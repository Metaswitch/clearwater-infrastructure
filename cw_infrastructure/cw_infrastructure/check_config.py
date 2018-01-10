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
import check_config_utilities as utils


class EnvironmentVariables():
    def __getitem__(self, key):
        return os.environ.get(key)


def _check_config_option(option, value):
    if value:
        # The option is present.
        if option.deprecated():
            # If a deprecated option has been set, warn the user
            utils.warning(option.name,
                          'option has been deprecated')
            code = utils.WARNING
        elif option.validator:
            # If the option has a a validator, run it now.
            code = option.validator(option.name, value)

    else:
        # The option is not present, which is an error if it's mandatory.
        if option.mandatory():
            utils.error(option.name, 'option is mandatory but not present')
            code = utils.ERROR
        elif option.suggested():
            utils.warning(option.name,
                          'option is recommended but not configured')
            code = utils.WARNING
        else:
            code = utils.OK
    return code


def _check_config_options(options, values):
    status = 0

    # Check that each option is present (if mandatory) and correctly formatted
    # (if it has a particular format we wish to check).
    for option in options:
        value = values[option.name]
        code = _check_config_option(option, value)

        # A higher value indicates a worse error.
        status = max(status, code)
    return status


def check_config(option_schema, values):

    # Build up a list of checks to be performed. Each check should take no
    # arguments and return a status code.
    checks = [functools.partial(_check_config_options,
                                option_schema.get_options(),
                                values),
              option_schema.check_advanced_config]

    # Determine the resultant status code - since ERROR > WARNING > OK, take
    # the maximum.
    return max(check() for check in checks)


if __name__ == '__main__':
    sys.exit(check_config(clearwater_options, EnvironmentVariables()))
