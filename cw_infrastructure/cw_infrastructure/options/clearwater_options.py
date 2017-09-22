#
# @file clearwater_options.py
#
# Copyright (C) Metaswitch Networks 2017
# If license terms are provided to you in a COPYING file in the root directory
# of the source code repository by which you are accessing this code, then
# the license outlined in that COPYING file applies to your use.
# Otherwise no rights are granted except for those provided to you by
# Metaswitch Networks in a separate written agreement.

from validator_infrastructure import *

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

    Option('homestead_diameter_watchdog_timer', Option.OPTIONAL,
           integer_range_validator_creator(min_value = 6)),
    Option('ralf_diameter_watchdog_timer', Option.OPTIONAL,
           integer_range_validator_creator(min_value = 6)),

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
