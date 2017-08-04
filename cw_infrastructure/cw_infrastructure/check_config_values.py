#
# @file check_config_values.py
#
# Copyright (C) Metaswitch Networks 2014
# If license terms are provided to you in a COPYING file in the root directory
# of the source code repository by which you are accessing this code, then
# the license outlined in that COPYING file applies to your use.
# Otherwise no rights are granted except for those provided to you by
# Metaswitch Networks in a separate written agreement.

import os
import sys
import socket
import re
import dns

from nsenter import Namespace

## Statuses

ERROR=5
WARNING=4
OK=0

def error(option_name, message):
    """Utility method to print error messages to stderr.

       @param option_name - The name of the option the error relates to.
       @param message     - A description of the problem"""
    sys.stderr.write("ERROR: {}: {}\n".format(option_name, message))


def warning(option_name, message):
    """Utility method to print warning messages to stderr.

       @param option_name - The name of the option the warning relates to.
       @param message     - A description of the problem"""
    sys.stderr.write("WARN: {}: {}\n".format(option_name, message))


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


def is_resolvable_domain_name(value):
    """Return whether the supplied string is a resolvable domain name"""
    try:
        socket.gethostbyname(value)
        return True
    except socket.gaierror:
        return False


def is_naptr_resolvable(naptr):
    """Check whether an NAPTR domain has any records"""

    return is_domain_resolvable(naptr, 'NAPTR')


def is_srv_resolvable(srv):
    """Check whether an SRV domain has any records"""

    return is_domain_resolvable(srv, 'SRV')


def is_domain_resolvable(name, rrtype):
    """Check whether the given domain has any records of the given type"""

    try:
        answers = dns.resolver.query(name, rrtype)
        return len(answers) != 0

    except:
        return False


class Option(object):
    """Description of a config option"""

    MANDATORY = 0
    SUGGESTED = 1
    OPTIONAL = 2

    def __init__(self, name, type=MANDATORY, validator=None):
        """Create a new config option

           @param name      - The name of the option.
           @param type      - Is this option mandatory, suggested, or optional
           @param validator - If supplied this must be a callable object that
             checks the option's value. If the check fails this function must
             print an error to stderr and return False. Otherwise it must return
             True.
        """
        self.name = name
        self.type = type
        self.validator = validator

    def mandatory(self):
        return self.type == Option.MANDATORY

    def suggested(self):
        return self.type == Option.SUGGESTED


# Validator definitions. Each of these functions takes two parameters: the
# parameter name and its value (both as strings). They should behave as follows:
#
# - If the value is acceptable, produce no output and return True.
# - If the value is unacceptable, produce an error log describing the problem
#   and return False.


def integer_validator(name, value):
    """Validate a config option that should be an integer"""
    try:
        int(value)
        return OK
    except ValueError:
        error(name, "{} is not an integer".format(value))
        return ERROR


def ip_addr_validator(name, value):
    """Validate a config option that should be an IP address"""
    if not is_ip_addr(value):
        error(name, "{} is not an IP address".format(value))
        return ERROR
    else:
        return OK


def ip_addr_list_validator(name, value):
    """Validate a config option that should be a comma-separated list of IP
    addresses"""
    if not all(is_ip_addr(i) for i in value.split(',')):
        error(name, "{} is not a comma separated list of IP addresses".format(value))
        return ERROR
    else:
        return OK


def domain_name_validator(name, value):
    """Validate a config option that should be a domain name"""
    if not is_domain_name(value):
        error(name, "{} is not a valid domain name".format(value))
        return ERROR
    else:
        return OK


def ip_or_domain_name_validator(name, value):
    """Validate a config option that should be a domain name or IP address"""
    if not is_ip_addr(value) and not is_domain_name(value):
        error(name, "{} is neither a valid IP address or domain name".format(value))
        return ERROR
    else:
        return OK


def resolvable_domain_name_validator(name, value):
    """Validate a config option that should be a resolvable domain name"""
    if not is_domain_name(value):
        error(name, "{} is not a valid domain name".format(value))
        return ERROR

    if is_resolvable_domain_name(value):
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

    if is_ip_addr(host):
        return OK

    elif not is_domain_name(host):
        error(name, ("{} is neither an IP address or a valid domain "
                     "name".format(host)))
        return ERROR

    elif port:
        if is_resolvable_domain_name(host):
            return OK

        else:
            error(name, "{} is not resolvable".format(host))
            return ERROR

    elif transport:
        srv = '_sip._{}.{}'.format(params['transport'], host)

        if is_srv_resolvable(srv):
            return OK
        else:
            error(name, "{} is not a valid SRV record".format(srv))
            return ERROR
    else:

        if is_naptr_resolvable(host):
            return OK
        else:
            error(name, "{} is not a valid NAPTR record".format(host))
            return ERROR


def diameter_realm_validator(name, value):
    """Validate a config option that should be a diameter realm"""

    # Realms should be valid domain names
    if not is_domain_name(value):
        error(name, "{} is not a valid realm".format(value))
        return ERROR

    if not is_srv_resolvable('_diameter._tcp.' + name):
        error(name, (
            '_diamater._tcp.{} does not resolve to any SRV '
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

    elif ip_version(stem) == 4:
        return OK

    elif is_domain_name(stem):

        if is_resolvable_domain_name(stem):
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


def number_present(*args):
    """Determine the number of configuration items given which are present"""
    config = 0

    for option in args:
        value = os.environ.get(option)
        if value:
            config += 1

    return config


def validate_hss_config():
    """
    Require that exactly one of hss_realm, hss_hostname,
    and hs_provisioning_hostname is set.
    """

    hss_config = number_present('hss_realm', 'hss_hostname', 'hs_provisioning_hostname')

    if hss_config > 1:
        error('HSS',
              ('Only one of hss_realm, hss_hostname, or '
               'hs_provisioning_hostname should be set'))
        return ERROR
    elif hss_config == 0:
        error('HSS',
              ('One of hss_realm, hss_hostname or hs_provisioning_hostname'
               'must be set'))
        return ERROR

    return OK


def validate_etcd_config():
    """Require that exactly one of etcd_proxy or etcd_cluster is set"""
    etcd_config = number_present('etcd_proxy', 'etcd_cluster')

    if etcd_config > 1:
        error('etcd', 'Only one of etcd_proxy and etcd_cluster may be set')
        return ERROR

    elif etcd_config == 0:
        error('etcd', 'One of etcd_proxy and etcd_cluster must be set')
        return ERROR

    return OK


def validate_sprout_hostname():
    """Check that the default URIs based on the Sprout hostname are valid"""

    sprout_hostname = os.environ.get('sprout_hostname')

    status = OK

    for sproutlet in ('scscf', 'bgcf', 'icscf'):

        # If the default hasn't been overriden, check that the URI
        # based on the Sprout hostname is a valid SIP URI
        if not os.environ.get('{}_uri'.format(sproutlet)):
            uri = 'sip:{}.{};transport=TCP'.format(sproutlet, sprout_hostname)
            code = run_in_sig_ns(sip_uri_validator)('sprout_hostname', uri)
            if code > status:
                status = code

    return status


# Options that we wish to check.
OPTIONS = [
    Option('local_ip', Option.MANDATORY, ip_addr_validator),
    Option('public_ip', Option.MANDATORY, ip_addr_validator),
    Option('public_hostname', Option.MANDATORY,
           run_in_sig_ns(resolvable_domain_name_validator)),
    Option('home_domain', Option.MANDATORY, domain_name_validator),
    Option('sprout_hostname', Option.MANDATORY,
           run_in_sig_ns(ip_or_domain_name_validator)),
    Option('hs_hostname', Option.MANDATORY,
           run_in_sig_ns(ip_or_domain_name_with_port_validator)),

    # Mandatory nature of one of these is enforced below
    Option('etcd_cluster', Option.OPTIONAL, ip_addr_list_validator),
    Option('etcd_proxy', Option.OPTIONAL, ip_addr_list_validator),

    # Mandatory nature of one of these is enforced below
    Option('hss_realm', Option.OPTIONAL, run_in_sig_ns(diameter_realm_validator)),
    Option('hss_hostname', Option.OPTIONAL, run_in_sig_ns(domain_name_validator)),
    Option('hs_provisioning_hostname', Option.OPTIONAL,
           run_in_sig_ns(ip_or_domain_name_with_port_validator)),

    Option('snmp_ip', Option.SUGGESTED, ip_addr_list_validator),
    Option('sas_server', Option.SUGGESTED, ip_or_domain_name_validator),

    Option('scscf_uri', Option.OPTIONAL, run_in_sig_ns(sip_uri_validator)),
    Option('bgcf_uri', Option.OPTIONAL, run_in_sig_ns(sip_uri_validator)),
    Option('icscf_uri', Option.OPTIONAL, run_in_sig_ns(sip_uri_validator)),

    Option('enum_server', Option.OPTIONAL, ip_addr_list_validator),
    Option('signaling_dns_server', Option.OPTIONAL, ip_addr_validator),
    Option('remote_cassandra_seeds', Option.OPTIONAL, ip_addr_validator),
    Option('billing_realm', Option.OPTIONAL,
           run_in_sig_ns(diameter_realm_validator)),
    Option('node_idx', Option.OPTIONAL, integer_validator),
    Option('ralf_hostname', Option.OPTIONAL,
           run_in_sig_ns(ip_or_domain_name_with_port_validator)),
    Option('xdms_hostname', Option.OPTIONAL,
           run_in_sig_ns(ip_or_domain_name_with_port_validator))
]


def check_config():
    status = 0

    # Check that each option is present (if mandatory) and correctly formatted (if
    # it has a particular format we wish to check).
    for option in OPTIONS:
        value = os.environ.get(option.name)

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

    #
    # More advanced checks (e.g. checking consistency between multiple options) can
    # be performed here.
    #

    code = validate_hss_config()

    if code > status:
        status = code

    code = validate_etcd_config()

    if code > status:
        status = code

    code = validate_sprout_hostname()

    if code > status:
        status = code

    return status


sys.exit(check_config())
