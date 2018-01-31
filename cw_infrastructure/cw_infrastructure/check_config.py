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
import functools
import pkg_resources

import check_config_utilities as utils


def _check_config_option(option, value):

    code = utils.OK

    if value:
        # The option is present.

        if option.deprecated():

            # If a deprecated option has been set, warn the user
            utils.warning(option.name,
                          'option has been deprecated')
            code = utils.WARNING

        if option.validator:

            # If the option has a a validator, run it now.
            code = max(code, option.validator(option.name, value))

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


def _check_config_options(options, get_option_value):
    status = 0

    # Check that each option is present (if mandatory) and correctly formatted
    # (if it has a particular format we wish to check).
    for option in options:
        value = get_option_value(option.name)
        code = _check_config_option(option, value)

        # A higher value indicates a worse error.
        status = max(status, code)
    return status


def check_config(option_schema, get_option_value):

    # Build up a list of checks to be performed. Each check should take no
    # arguments and return a status code.
    checks = []
    checks += [functools.partial(_check_config_options,
                                 option_schema.get_options(),
                                 get_option_value)]
    checks += [functools.partial(advanced_check)
               for advanced_check in option_schema.get_advanced_checks()]

    # Determine the resultant status code - since ERROR > WARNING > OK, take
    # the maximum.
    return max(check() for check in checks)


if __name__ == '__main__':
    option_schemas = [entry_point.load()
                      for entry_point
                      in pkg_resources.iter_entry_points('option_schemas')]

    sys.exit(max(check_config(option_schema, utils.get_environment_variable)
             for option_schema in option_schemas))
