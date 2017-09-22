#
# @file check_config_values.py
#
# Copyright (C) Metaswitch Networks 2017
# If license terms are provided to you in a COPYING file in the root directory
# of the source code repository by which you are accessing this code, then
# the license outlined in that COPYING file applies to your use.
# Otherwise no rights are granted except for those provided to you by
# Metaswitch Networks in a separate written agreement.

import glob
import imp
import sys
import os
from os.path import join, split, dirname
from validator_infrastructure import *

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

def check_config(OPTIONS):
    status = 0

    config = {}
    with open('shared_config') as myfile:
        for line in myfile:
            name, var = line.partition('=')[::2]
            config[name.strip()] = var

    # Check that each option is present (if mandatory) and correctly formatted (if
    # it has a particular format we wish to check).
    for option in OPTIONS:
        # value = os.environ.get(option.name) UNCOMMENT!!
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

# Retrieve options from the options/ directory
options_path = join(dirname(__file__), 'options', '*.py')
option_pairs = [(split(path)[1], path) for path in glob.glob(options_path)]
option_modules = [imp.load_source(name, path) for (name, path) in option_pairs]

OPTIONS = []
for module in option_modules:
    OPTIONS += module.OPTIONS

sys.exit(check_config(OPTIONS))
