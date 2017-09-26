#
# @file clearwater_options.py
#
# Copyright (C) Metaswitch Networks 2017
# If license terms are provided to you in a COPYING file in the root directory
# of the source code repository by which you are accessing this code, then
# the license outlined in that COPYING file applies to your use.
# Otherwise no rights are granted except for those provided to you by
# Metaswitch Networks in a separate written agreement.

import os

import cw_infrastructure.validators as vlds
from cw_infrastructure.check_config_utilities import (OK, ERROR, WARNING,
        error, warning, number_present, Option)

def get_options():
    """Set up the list of options to be validated"""
    options = [
        Option('local_ip', Option.MANDATORY, vlds.ip_addr_validator),
        Option('public_ip', Option.MANDATORY, vlds.ip_addr_validator),
        Option('public_hostname', Option.MANDATORY,
               vlds.run_in_sig_ns(vlds.resolvable_domain_name_validator)),
        Option('home_domain', Option.MANDATORY, vlds.domain_name_validator),
        Option('sprout_hostname', Option.MANDATORY,
               vlds.run_in_sig_ns(vlds.ip_or_domain_name_validator)),
        Option('hs_hostname', Option.MANDATORY,
               vlds.run_in_sig_ns(vlds.ip_or_domain_name_with_port_validator)),

        Option('homestead_diameter_watchdog_timer', Option.OPTIONAL,
               vlds.integer_range_validator_creator(min_value = 6)),
        Option('ralf_diameter_watchdog_timer', Option.OPTIONAL,
               vlds.integer_range_validator_creator(min_value = 6)),

        # Mandatory nature of one of these is enforced below
        Option('etcd_cluster', Option.OPTIONAL, vlds.ip_addr_list_validator),
        Option('etcd_proxy', Option.OPTIONAL, vlds.ip_addr_list_validator),

        # Mandatory nature of one of these is enforced below
        Option('hss_realm', Option.OPTIONAL,
               vlds.run_in_sig_ns(vlds.diameter_realm_validator)),
        Option('hss_hostname', Option.OPTIONAL,
               vlds.run_in_sig_ns(vlds.domain_name_validator)),
        Option('hs_provisioning_hostname', Option.OPTIONAL,
               vlds.run_in_sig_ns(vlds.ip_or_domain_name_with_port_validator)),

        Option('snmp_ip', Option.SUGGESTED, vlds.ip_addr_list_validator),
        Option('sas_server', Option.SUGGESTED, vlds.ip_or_domain_name_validator),

        Option('scscf_uri', Option.OPTIONAL,
               vlds.run_in_sig_ns(vlds.sip_uri_validator)),
        Option('bgcf_uri', Option.OPTIONAL,
               vlds.run_in_sig_ns(vlds.sip_uri_validator)),
        Option('icscf_uri', Option.OPTIONAL,
               vlds.run_in_sig_ns(vlds.sip_uri_validator)),

        Option('enum_server', Option.OPTIONAL, vlds.ip_addr_list_validator),
        Option('signaling_dns_server', Option.OPTIONAL, vlds.ip_addr_validator),
        Option('remote_cassandra_seeds', Option.OPTIONAL, vlds.ip_addr_validator),
        Option('billing_realm', Option.OPTIONAL,
               vlds.run_in_sig_ns(vlds.diameter_realm_validator)),
        Option('node_idx', Option.OPTIONAL, vlds.integer_validator),
        Option('ralf_hostname', Option.OPTIONAL,
               vlds.run_in_sig_ns(vlds.ip_or_domain_name_with_port_validator)),
        Option('xdms_hostname', Option.OPTIONAL,
               vlds.run_in_sig_ns(vlds.ip_or_domain_name_with_port_validator))
    ]
    return options


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

    return ccu.OK


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
            code = vlds.run_in_sig_ns(vlds.sip_uri_validator)('sprout_hostname', uri)
            if code > status:
                status = code

    return status

def check_advanced_config():
    """
    More advanced checks (e.g. checking consistency between multiple options)
    can be performed here.
    """
    status = OK

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
