#
# @file check_config_utilities.py
#
# Copyright (C) Metaswitch Networks 2017
# If license terms are provided to you in a COPYING file in the root directory
# of the source code repository by which you are accessing this code, then
# the license outlined in that COPYING file applies to your use.
# Otherwise no rights are granted except for those provided to you by
# Metaswitch Networks in a separate written agreement.

import sys
import socket
import re
import dns.resolver
import os

# Statuses

ERROR = 5
WARNING = 4
OK = 0


def error(option_name, message):
    """Utility method to print error messages to stderr.

       @param option_name - The name of the option the error relates to.
       @param message     - A description of the problem"""
    sys.stderr.write("ERROR: {}: {}\n".format(option_name, message))


def warning(option_name, message):
    """Utility method to print warning messages to stderr.

       @param option_name - The name of the option the warning relates to.
       @param message     - A description of the problem"""
    sys.stderr.write("WARNING: {}: {}\n".format(option_name, message))


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
    return (ip_version(value) is not None)


def is_domain_name(value):
    """Return whether the supplied string is a valid domain name"""

    # A domain consists of one or more labels separated by dots.  Each label
    # must start and end with a letter or number. The characters in between can
    # be either letters, numbers or a hyphen. In addition a label can be at
    # most 63 characters long, and the address as a whole can be 255 characters
    # long.
    #
    # Note that RFC 1035, section 2.3.1 technically forbids labels from
    # starting with a digit. However this does happen in practice, so we allow
    # it.
    #
    # The following code builds a regex that only matches on valid domain
    # names. The only thing it does not police is the total length of the name,
    # which is checked separately below.
    label_regex = r"[a-zA-Z\d]([a-zA-Z\d-]{0,61}[a-zA-Z\d])?"
    domain_regex = re.compile(r"^({0})(\.{0})*$".format(label_regex))

    if len(value) > 255 or not domain_regex.match(value):
        return False
    else:
        return True


def is_resolvable_domain_name(value):
    """Return whether the supplied string is a resolvable domain name"""
    return (is_domain_resolvable(value, 'A') or
            is_domain_resolvable(value, 'AAAA'))


def is_naptr_resolvable(naptr):
    """Check whether an NAPTR domain has any records"""

    return is_domain_resolvable(naptr, 'NAPTR')


def is_srv_resolvable(srv):
    """Check whether an SRV domain has any records"""

    return is_domain_resolvable(srv, 'SRV')


def is_domain_resolvable(name, rrtype):
    """Check whether the given domain has any records of the given type"""

    try:
        resolver = dns.resolver.get_default_resolver()
        resolver.timeout = 2
        answers = resolver.query(name, rrtype)
        return len(answers) != 0

    except Exception:
        return False


def number_present(*args):
    """Determine the number of configuration items given which are present"""
    config = 0

    for option in args:
        value = os.environ.get(option)
        if value:
            config += 1

    return config


class Option(object):
    """Description of a config option"""

    MANDATORY = 0
    SUGGESTED = 1
    OPTIONAL = 2
    DEPRECATED = 3

    def __init__(self, name, type=MANDATORY, validator=None):
        """Create a new config option

           @param name      - The name of the option.
           @param type      - Is this option mandatory, suggested, or optional
           @param validator - If supplied this must be a callable object that
             checks the option's value. If the check fails this function must
             print an error to stderr and return False. Otherwise it must
             return True.
        """
        self.name = name
        self.type = type
        self.validator = validator

    def mandatory(self):
        return self.type == Option.MANDATORY

    def suggested(self):
        return self.type == Option.SUGGESTED

    def deprecated(self):
        return self.type == Option.DEPRECATED
