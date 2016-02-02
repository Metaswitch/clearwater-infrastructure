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

# Flag indicating whether all the config checks have passed. This affects the
# script's exit code.
all_ok = True

def error(option_name, message):
    """Utility method to print error messages to stderr.

       @param option_name - The name of the option the error relates to.
       @param message     - A description of the problem"""
    sys.stderr.write("ERROR: {}: {}\n".format(option_name, message))


# Check that all mandatory options are present and correct.
MANDATORY_OPTIONS = [
  'local_ip',
  'public_ip',
  'public_hostname',
  'etcd_cluster',
  'home_domain',
  'sprout_hostname',
  'hs_hostname',
]

for opt_name in MANDATORY_OPTIONS:
    if not os.environ.has_key(opt_name):
        error(opt_name, "option is mandatory but not present")
        all_ok = False

#
# Values of individual options can be checked here.
#

# Return an appropriate error code to the caller.
if not all_ok:
    sys.exit(1)
else:
    sys.exit(0)
