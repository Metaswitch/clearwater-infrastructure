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
import socket
import re


def error(option_name, message):
    """Utility method to print error messages to stderr.

       @param option_name - The name of the option the error relates to.
       @param message     - A description of the problem"""
    sys.stderr.write("ERROR: {}: {}\n".format(option_name, message))


def ip_version(value):
    """Return the IP version of the supplied IP address, which is passed as a
    string. If the argument is not an IP address this function returns None,
    which is more convenient than raising an exception"""
    try:
        socket.inet_pton(socket.AF_INET, value)
        return 4
    except socket.error:
        try:
            socket.inet_pton(socket.AF_INET6, value)
            return 6
        except socket.error:
            return None


def is_ip_addr(value):
    """Return whether the supplied string is a valid IP address"""
    return (ip_version(value) != None)


def is_domain_name(value):
    """Return whether the supplied string is a valid domain name"""

    # A domain consists of one or more labels separated by dots.  Each label
    # must start and end with a letter or number. The characters in between can
    # be either letters, numbers or a hyphen. In addition a label can be at most
    # 63 characters long, and the address as a whole can be 255 characters long.
    #
    # Note that RFC 1035, section 2.3.1 technically forbids labels from starting
    # with a digit. However this does happen in practice, so we allow it.
    #
    # The following code builds a regex that only matches on valid domain names.
    # The only thing it does not police is the total length of the name, which
    # is checked separately below.
    label_regex = r"[a-zA-Z\d]([a-zA-Z\d-]{0,61}[a-zA-Z\d])?"
    domain_regex = re.compile(r"^({0})(\.{0})*$".format(label_regex))

    if len(value) > 255 or not domain_regex.match(value):
        return False
    else:
        return True


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


#-------------------------------------------------------------------------------
# Validator definitions. Each of these functions takes two parameters: the
# parameter name and its value (both as strings). They should behave as follows:
#
# - If the value is acceptable, produce no output and return True.
# - If the value is unacceptable, produce an error log describing the problem
#   and return False.
#-------------------------------------------------------------------------------


def integer_validator(name, value):
    """Validate a config option that should be an integer"""
    try:
        int(value)
        return True
    except ValueError:
        error(name, "{} is not an integer".format(value))
        return False


def ip_addr_validator(name, value):
    """Validate a config option that should be an IP address"""
    if not is_ip_addr(value):
        error(name, "{} is not an IP address".format(value))
        return False
    else:
        return True


def ip_addr_list_validator(name, value):
    """Validate a config option that should be a comma-separated list of IP
    addresses"""
    if not all(is_ip_addr(i) for i in value.split(',')):
        error(name, "{} is not a comma separated list of IP addresses".format(value))
        return False
    else:
        return True


def domain_name_validator(name, value):
    """Validate a config option that should be a domain name"""
    if not is_domain_name(value):
        error(name, "{} is not a valid domain name".format(value))
        return False
    else:
        return True


def ip_or_domain_name_validator(name, value):
    """Validate a config option that should be a domain name or IP address"""
    if not is_ip_addr(value) and not is_domain_name(value):
        error(name, "{} is neither a valid IP address or domain name".format(value))
        return False
    else:
        return True

def resolvable_domain_name_validator(name, value):
    """Validate a config option that should be a resolvable domain name"""
    if not is_domain_name(value):
        error(name, "{} is not a valid domain name".format(value))
        return False

    try:
        socket.gethostbyname(value)
        return True
    except socket.gaierror:
        error(name, "{} is not resolvable".format(value))
        return False


def ip_or_domain_name_with_port_validator(name, value):
    """Validate a config option that should be a IP address or domain name,
    followed by a port"""
    match = re.match(r"^(.*):(\d+)$", value)
    if not match:
        error(name, "{} does not contain a port".format(value))
        return False

    stem = match.group(1)
    port = match.group(2)

    if int(port) >= 2**16:
        error(name, "The port value ({}) is too large".format(port))
        return False

    if (stem[0] == '[') and (stem[-1] == ']'):
        ip = stem[1:-1]
        if ip_version(ip) == 6:
            return True
        else:
            error(name, "{} is not a valid IPv6 address".format(ip))
            return False

    elif ip_version(stem) == 4:
        return True

    elif is_domain_name(stem):
        return True

    else:
        error(name, ("{} is neither a domain name, "
                     "IPv4 address, or bracketed IPv6 address").format(stem))
        return False


# Options that we wish to check.
OPTIONS = [
  Option('local_ip', True, ip_addr_validator),
  Option('public_ip', True, ip_addr_validator),
  Option('public_hostname', True, resolvable_domain_name_validator),
  Option('etcd_cluster', True, ip_addr_list_validator),
  Option('home_domain', True, domain_name_validator),
  Option('sprout_hostname', True, ip_or_domain_name_validator),
  Option('hs_hostname', True, ip_or_domain_name_with_port_validator),

  Option('node_idx', False, integer_validator),
  Option('ralf_hostname', False, ip_or_domain_name_with_port_validator),
  Option('xdms_hostname', False, ip_or_domain_name_with_port_validator),
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
            if not option.validator(option.name, value):
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
