# @file check_config_contents.py
#
# Project Clearwater - IMS in the Cloud
# Copyright (C) 2013  Metaswitch Networks Ltd
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version, along with the "Special Exception" for use of
# the program along with SSL, set forth below. This program is distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details. You should have received a copy of the GNU General Public
# License along with this program.  If not, see
# <http://www.gnu.org/licenses/>.
#
# The author can be reached by email at clearwater@metaswitch.com or by
# post at Metaswitch Networks Ltd, 100 Church St, Enfield EN2 6BQ, UK
#
# Special Exception
# Metaswitch Networks Ltd  grants you permission to copy, modify,
# propagate, and distribute a work formed by combining OpenSSL with The
# Software, or a work derivative of such a combination, even if such
# copying, modification, propagation, or distribution would otherwise
# violate the terms of the GPL. You must comply with the GPL in all
# respects for all of the code used other than OpenSSL.
# "OpenSSL" means OpenSSL toolkit software distributed by the OpenSSL
# Project and licensed under the OpenSSL Licenses, or a work based on such
# software and licensed under the OpenSSL Licenses.
# "OpenSSL Licenses" means the OpenSSL License and Original SSLeay License
# under which the OpenSSL Project distributes the OpenSSL toolkit software,
# as those licenses appear in the file LICENSE-OPENSSL.

import os
import sys


def error(option_name, message):
    """Utility method to print error messages to stderr.

       @param option_name - The name of the option the error relates to.
       @param message     - A description of the problem"""
    sys.stderr.write("ERROR: {}: {}\n".format(option_name, message))


class Option(object):
    """Description of a config option"""

    def __init__(self, name, mandatory=True, validator=None):
        """Create a new config option

           @param name      - The name of the option.
           @param mandatory - Whether the option is mandatory or not.
           @param validator - If supplied this must be a callable object that
             checks the option's value. If the check fails this function must
             print an error to stderr and return False. Otherwise it must return
             True.
        """
        self.name = name
        self.mandatory = mandatory
        self.validator = validator


# Options that we wish to check.
OPTIONS = [
  Option('local_ip', True),
  Option('public_ip', True),
  Option('public_hostname', True),
  Option('etcd_cluster', True),
  Option('home_domain', True),
  Option('sprout_hostname', True),
  Option('hs_hostname', True),
]

# Flag indicating whether all the config checks have passed. This affects the
# script's exit code.
all_ok = True

# Check that each option is present (if mandatory) and correctly formatted (if
# it has a particular format we wish to check).
for option in OPTIONS:
    value = os.environ.get(option.name)

    if value:
        # The option is present. If it has validator, run it now.
        if option.validator:
            if not option.validator(value):
                # The validator is responsible for printing an error message.
                all_ok = False

    else:
        # The option is not present, which is an error if it's mandatory.
        if option.mandatory:
            error(option.name, 'option is mandatory but not present')
            all_ok = False

#
# More advanced checks (e.g. checking consistency between multiple options) can
# be performed here.
#

# Return an appropriate error code to the caller.
if not all_ok:
    sys.exit(1)
else:
    sys.exit(0)
