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
# parameter name and its value (both as strings). They should behave as
# follows:
#
# - If the value is acceptable, produce no output and return utils.OK.
# - If the value is unacceptable, produce an error log describing the problem
#   and return utils.ERROR.
# - If the value is acceptable but not recommended, produce a warning log
#   describing the problem and return WARNING.

import dns
import re
import os
from nsenter import Namespace

import check_config_utilities as utils


def integer_validator(name, value):
    """Validate a config option that should be an integer"""
    try:
        int(value)
        return utils.OK
    except ValueError:
        utils.error(name, "{} is not an integer".format(value))
        return utils.ERROR


def create_integer_range_validator(min_value=None, max_value=None,
                                   warn_min_value=None, warn_max_value=None):
    """ Creates and returns an integer_range_validator """

    def integer_range_validator(name, value):
        """Validate a config option that should be an integer lying in a given
        range"""
        if integer_validator(name, value) == utils.ERROR:
            return utils.ERROR
        value_int = int(value)

        # Check if the value lies in the allowed range
        if min_value is not None and value_int < min_value:
            utils.error(name,
                        "{} is below the allowed minimum {}".format(value,
                                                                    min_value))
            return utils.ERROR
        if max_value is not None and value_int > max_value:
            utils.error(name,
                        "{} is above the allowed maximum {}".format(value,
                                                                    max_value))
            return utils.ERROR

        # Check if the value lies in the recommended range
        if warn_min_value is not None and value_int < warn_min_value:
            utils.warning(name,
                          "{} is below the recommended minimum {}".format(value,
                                                                          warn_min_value))
            return utils.WARNING
        if warn_max_value is not None and value_int > warn_max_value:
            utils.warning(name,
                          "{} is above the recommended maximum {}".format(value,
                                                                          warn_max_value))
            return utils.WARNING

        return utils.OK
    return integer_range_validator


def ip_addr_validator(name, value):
    """Validate a config option that should be an IP address"""
    if not utils.is_ip_addr(value):
        utils.error(name, "{} is not an IP address".format(value))
        return utils.ERROR
    else:
        return utils.OK


def ip_addr_list_validator(name, value):
    """Validate a config option that should be a comma-separated list of IP
    addresses"""
    if not all(utils.is_ip_addr(i) for i in value.split(',')):
        utils.error(name,
                    "{} is not a comma separated list of IP addresses".format(value))
        return utils.ERROR
    else:
        return utils.OK


def domain_name_validator(name, value):
    """Validate a config option that should be a domain name"""
    if not utils.is_domain_name(value):
        utils.error(name, "{} is not a valid domain name".format(value))
        return utils.ERROR
    else:
        return utils.OK


def ip_or_domain_name_validator(name, value):
    """Validate a config option that should be a domain name or IP address"""
    if not utils.is_ip_addr(value) and not utils.is_domain_name(value):
        utils.error(name,
                    "{} is neither a valid IP address or domain name".format(value))
        return utils.ERROR
    else:
        return utils.OK


def resolvable_domain_name_validator(name, value):
    """Validate a config option that should be a resolvable domain name"""
    if not utils.is_domain_name(value):
        utils.error(name, "{} is not a valid domain name".format(value))
        return utils.ERROR

    if utils.is_resolvable_domain_name(value):
        return utils.OK
    else:
        utils.error(name, "{} is not resolvable".format(value))
        return utils.ERROR


def resolveable_ip_or_domain_name_list_validator(name, value):
    """
    Check whether a config option is a list of IP addresses, or domain names
    that resolve with the current DNS setup
    """

    if not all(utils.is_ip_addr(i) or utils.is_resolvable_domain_name(value)
               for i in value.split(',')):
        utils.error(name,
                    ("{} is not a comma separated list of resolvable domain "
                     "names or IP addresses".format(value)))
        return utils.ERROR

    return utils.OK


def sip_uri_validator(name, value):
    """Validate a config option represents a valid SIP URI"""

    match = re.match(r"^([a-z]+):(?:([^@])+@)?([^:;]*)(?::(\d+))?(?:;(.*))?$",
                     value)

    if not match:
        utils.error(name, "{} is not a valid SIP URI".format(value))
        return utils.ERROR

    scheme = match.group(1)
    host = match.group(3)
    port = match.group(4)
    params = match.group(5)

    if scheme != "sip":
        utils.error(name, "{} is not a SIP URI".format(value))
        return utils.ERROR

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
            utils.error(name, ("{} is not a valid SIP "
                               "transport").format(params['transport']))
            return utils.ERROR

        else:
            transport = params['transport']

    if utils.is_ip_addr(host):
        return utils.OK

    elif not utils.is_domain_name(host):
        utils.error(name, ("{} is neither an IP address or a valid domain "
                           "name".format(host)))
        return utils.ERROR

    elif port:
        if utils.is_resolvable_domain_name(host):
            return utils.OK
        else:
            utils.error(name, "{} is not resolvable".format(host))
            return utils.ERROR

    elif transport:
        srv = '_sip._{}.{}'.format(params['transport'].lower(), host)

        if utils.is_srv_resolvable(srv):
            return utils.OK
        else:
            utils.error(name, "{} is not a valid SRV record".format(srv))
            return utils.ERROR
    else:

        if utils.is_naptr_resolvable(host):
            return utils.OK
        else:
            utils.error(name, "{} is not a valid NAPTR record".format(host))
            return utils.ERROR


def diameter_realm_validator(name, value):
    """Validate a config option that should be a diameter realm"""

    # Realms should be valid domain names
    if not utils.is_domain_name(value):
        utils.error(name, "{} is not a valid realm".format(value))
        return utils.ERROR

    if not utils.is_srv_resolvable('_diameter._tcp.' + value):
        utils.error(name, (
            '_diameter._tcp.{} does not resolve to any SRV '
            'records'.format(value)))
        return utils.ERROR

    return utils.OK


def ip_or_domain_name_with_port_validator(name, value):
    """Validate a config option that should be a IP address or domain name,
    followed by a port"""
    match = re.match(r"^(.*):(\d+)$", value)
    if not match:
        utils.error(name, "{} does not contain a port".format(value))
        return utils.ERROR

    stem = match.group(1)
    port = match.group(2)

    if int(port) >= 2**16:
        utils.error(name, "The port value ({}) is too large".format(port))
        return utils.ERROR

    if (stem[0] == '[') and (stem[-1] == ']'):
        ip = stem[1:-1]
        if utils.ip_version(ip) == 6:
            return utils.OK
        else:
            utils.error(name, "{} is not a valid IPv6 address".format(ip))
            return utils.ERROR

    elif utils.ip_version(stem) == 4:
        return utils.OK

    elif utils.is_domain_name(stem):
        if utils.is_resolvable_domain_name(stem):
            return utils.OK
        else:
            utils.error(name, "Unable to resolve domain name {}".format(stem))
            return utils.ERROR

    else:
        utils.error(name, ("{} is neither a domain name, "
                           "IPv4 address, or bracketed IPv6 address").format(stem))
        return utils.OK


def run_validator_with_dns(validator, name, value, dns_server):
    """Run a validator in the signaling namespace"""

    if dns_server:
        dns.resolver.override_system_resolver()
        dns.resolver.get_default_resolver().nameservers = dns_server.split(',')

    result = validator(name, value)

    if dns_server:
        dns.resolver.restore_system_resolver()
        dns.resolver.reset_default_resolver()

    return result


def run_in_sig_ns(validator):
    """Run a validator in the signaling namespace"""

    def sig_ns_validator(name, value):

        sig_ns = os.environ.get('signaling_namespace')

        # If we have a configured signaling DNS server
        # use it in preference for both DNS Python requests
        # and none DNS Python requests
        sig_dns = os.environ.get('signaling_dns_server')

        if sig_ns:
            with Namespace('/var/run/netns/' + sig_ns, 'net'):
                return run_validator_with_dns(validator, name, value, sig_dns)
        else:
            return run_validator_with_dns(validator, name, value, sig_dns)

    return sig_ns_validator
