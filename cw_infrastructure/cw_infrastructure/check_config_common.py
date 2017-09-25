#
# @file check_config_utilities.py
#
# Copyright (C) Metaswitch Networks 2017
# If license terms are provided to you in a COPYING file in the root directory
# of the source code repository by which you are accessing this code, then
# the license outlined in that COPYING file applies to your use.
# Otherwise no rights are granted except for those provided to you by
# Metaswitch Networks in a separate written agreement.

from check_config_utilities import OK, WARNING, ERROR

def number_present(*args):
    """Determine the number of configuration items given which are present"""
    config = 0

    for option in args:
        value = os.environ.get(option)
        if value:
            config += 1

    return config

def check_config(OPTIONS):
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
    for option in OPTIONS:
        # value = os.environ.get(option.name) TODO: Uncomment
        value = config.get(option.name)

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
