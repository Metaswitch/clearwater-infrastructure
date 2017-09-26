#
# @file validators.py
#
# Copyright (C) Metaswitch Networks 2017
# If license terms are provided to you in a COPYING file in the root directory
# of the source code repository by which you are accessing this code, then
# the license outlined in that COPYING file applies to your use.
# Otherwise no rights are granted except for those provided to you by
# Metaswitch Networks in a separate written agreement.

# Validator definitions. Each of these functions takes two parameters: the
# parameter name and its value (both as strings). They should behave as follows:
#
# - If the value is acceptable, produce no output and return True.
# - If the value is unacceptable, produce an error log describing the problem
#   and return False.

import dns
import re
import os
from nsenter import Namespace

import check_config_utilities as utils
from check_config_utilities import OK, WARNING, ERROR, warning, error

def integer_validator(name, value):
    """Validate a config option that should be an integer"""
    try:
        int(value)
        return OK
    except ValueError:
        error(name, "{} is not an integer".format(value))
        return ERROR


""" Creates and returns an integer_range_validator """
def integer_range_validator_creator(min_value = None, max_value = None):

    """Validate a config option that should be an integer lying in a given
    range"""
    def integer_range_validator(name, value):
        if integer_validator(name, value) == ERROR:
            return utils.ERROR
        value_int = int(value)

        if min_value is not None and value_int < min_value:
            error(name, "{} is below the allowed minimum {}".format(value, min_value))
            return ERROR
        if max_value is not None and value_int > max_value:
            error(name, "{} is above the allowed maximum {}".format(value, max_value))
            return ERROR
        return OK
    return integer_range_validator


def ip_addr_validator(name, value):
    """Validate a config option that should be an IP address"""
    if not utils.is_ip_addr(value):
        error(name, "{} is not an IP address".format(value))
        return ERROR
    else:
        return OK


def ip_addr_list_validator(name, value):
    """Validate a config option that should be a comma-separated list of IP
    addresses"""
    if not all(utils.is_ip_addr(i) for i in value.split(',')):
        error(name, "{} is not a comma separated list of IP addresses".format(value))
        return ERROR
    else:
        return OK


def domain_name_validator(name, value):
    """Validate a config option that should be a domain name"""
    if not utils.is_domain_name(value):
        error(name, "{} is not a valid domain name".format(value))
        return ERROR
    else:
        return OK


def ip_or_domain_name_validator(name, value):
    """Validate a config option that should be a domain name or IP address"""
    if not utils.is_ip_addr(value) and not utils.is_domain_name(value):
        error(name, "{} is neither a valid IP address or domain name".format(value))
        return ERROR
    else:
        return OK


def resolvable_domain_name_validator(name, value):
    """Validate a config option that should be a resolvable domain name"""
    if not utils.is_domain_name(value):
        error(name, "{} is not a valid domain name".format(value))
        return ERROR

    if utils.is_resolvable_domain_name(value):
        return OK
    else:
        error(name, "{} is not resolvable".format(value))
        return ERROR


def sip_uri_validator(name, value):
    """Validate a config option represents a valid SIP URI"""

    match = re.match(r"^([a-z]+):(?:([^@])+@)?([^:;]*)(?::(\d+))?(?:;(.*))?$", value)

    if not match:
        error(name, "{} is not a valid SIP URI".format(value))
        return ERROR

    scheme = match.group(1)
    host = match.group(3)
    port = match.group(4)
    params = match.group(5)

    if scheme != "sip":
        error(name, "{} is not a SIP URI".format(value))
        return ERROR

    if params:
        pdict = {}

        for param in params.split(';'):
            pmatch = re.match(r"([^=]+)=(.*)", param)
            if pmatch:
                pdict[pmatch.group(1)] = pmatch.group(2)
            else:
                pdict[param] = True

        params = pdict
    else:
        params = {}

    # Check whether a transport parameter is provided and is valid
    transport = None

    if 'transport' in params:
        if params['transport'].lower() not in ('udp', 'tcp'):
            error(name, ("{} is not a valid SIP "
                         "transport").format(params['transport']))
            return ERROR

        else:
            transport = params['transport']

    if utils.is_ip_addr(host):
        return OK

    elif not utils.is_domain_name(host):
        error(name, ("{} is neither an IP address or a valid domain "
                     "name".format(host)))
        return ERROR

    elif port:
        if utils.is_resolvable_domain_name(host):
            return OK

        else:
            error(name, "{} is not resolvable".format(host))
            return ERROR

    elif transport:
        srv = '_sip._{}.{}'.format(params['transport'], host)

        if utils.is_srv_resolvable(srv):
            return OK
        else:
            error(name, "{} is not a valid SRV record".format(srv))
            return ERROR
    else:

        if utils.is_naptr_resolvable(host):
            return OK
        else:
            error(name, "{} is not a valid NAPTR record".format(host))
            return ERROR


def diameter_realm_validator(name, value):
    """Validate a config option that should be a diameter realm"""

    # Realms should be valid domain names
    if not utils.is_domain_name(value):
        error(name, "{} is not a valid realm".format(value))
        return ERROR

    if not utils.is_srv_resolvable('_diameter._tcp.' + value):
        error(name, (
            '_diameter._tcp.{} does not resolve to any SRV '
            'records'.format(value)))
        return ERROR

    return OK


def ip_or_domain_name_with_port_validator(name, value):
    """Validate a config option that should be a IP address or domain name,
    followed by a port"""
    match = re.match(r"^(.*):(\d+)$", value)
    if not match:
        error(name, "{} does not contain a port".format(value))
        return ERROR

    stem = match.group(1)
    port = match.group(2)

    if int(port) >= 2**16:
        error(name, "The port value ({}) is too large".format(port))
        return ERROR

    if (stem[0] == '[') and (stem[-1] == ']'):
        ip = stem[1:-1]
        if ip_version(ip) == 6:
            return OK
        else:
            error(name, "{} is not a valid IPv6 address".format(ip))
            return ERROR

    elif utils.ip_version(stem) == 4:
        return OK

    elif utils.is_domain_name(stem):

        if utils.is_resolvable_domain_name(stem):
            return OK
        else:
            error(name, "Unable to resolve domain name {}".format(stem))
            return ERROR

    else:
        error(name, ("{} is neither a domain name, "
                     "IPv4 address, or bracketed IPv6 address").format(stem))
        return OK


def run_in_sig_ns(validator):
    """Run a validator in the signaling namespace"""

    def sig_ns_validator(name, value):

        sig_ns = os.environ.get('signaling_namespace')

        # If we have a configured signaling DNS server
        # use it in preference for both DNS Python requests
        # and none DNS Python requests
        sig_dns = os.environ.get('signaling_dns_server')

        if sig_dns:
            dns.get_default_resolver().nameservers = [sig_dns]
            dns.override_system_resolver()

        if sig_ns:
            with Namespace('/var/run/netns/' + sig_ns, 'net'):
                return validator(name, value)

        if sig_dns:
            dns.restore_system_resolver()
            dns.reset_default_resolver()

        else:
            return validator(name, value)

    return sig_ns_validator
