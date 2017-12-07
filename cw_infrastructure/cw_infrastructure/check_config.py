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


def check_config_options(options):
    status = 0

    # Check that each option is present (if mandatory) and correctly formatted (if
    # it has a particular format we wish to check).
    for option in options:
        value = os.environ.get(option.name)

        if value:
            # The option is present. If the option has a validator, run it now.
            if option.validator:
                code = option.validator(option.name, value)

        else:
            # The option is not present, which is an error if it's mandatory.
            if option.mandatory():
                error(option.name, 'option is mandatory but not present')
                code = ERROR
            elif option.suggested():
                warning(option.name, 'option is not configured')
                code = WARNING
        # A higher value indicates a worse error.
        status = max(status, code)
    return status


def get_file_name(path):
    """
    Given a path, retrieve the file name without the extension, e.g.
    foo from /path/directory/foo.py
    """
    file_name_with_ext = os.path.basename(path)
    (file_name, ext) = os.path.splitext(file_name_with_ext)
    return file_name


def check_config():

    # Build up a list of checks to be performed. Each check should take no
    # arguments and return a status code.
    checks = [functools.partial(check_config_options,
                                clearwater_options.get_options()),
              clearwater_options.check_advanced_config]

    # Determine the resultant status code - since ERROR > WARNING > OK, take
    # the maximum.
    return max(check() for check in checks)


if __name__ == '__main__':
    sys.exit(check_config())
