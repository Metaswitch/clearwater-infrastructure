#!/usr/bin/python2.7

# @file sas_socket_factory.py
#
# Copyright (C) Metaswitch Networks 2018
# If license terms are provided to you in a COPYING file in the root directory
# of the source code repository by which you are accessing this code, then
# the license outlined in that COPYING file applies to your use.
# Otherwise no rights are granted except for those provided to you by
# Metaswitch Networks in a separate written agreement.
#
# Script that writes the contents of sas.json to the relevant whitelist file.

import sys
import json
import os

SAS_CONFIG_FILE = "/etc/clearwater/sas.json"

SIGNALING_CFG_DIR = "/etc/clearwater-socket-factory/signaling.d"
MANAGEMENT_CFG_DIR = "/etc/clearwater-socket-factory/management.d"

os.makedirs(SIGNALING_CFG_DIR)
os.makedirs(MANAGEMENT_CFG_DIR)

sas_use_signaling_namespace = sys.argv[1]
if sas_use_signaling_namespace is "Y":
    file_to_write = SIGNALING_CFG_DIR + "/clearwater-infrastructure"
    os.remove(MANAGEMENT_CFG_DIR + "/clearwater-infrastructure")
else:
    file_to_write = MANAGEMENT_CFG_DIR + "/clearwater-infrastructure"
    os.remove(SIGNALING_CFG_DIR + "/clearwater-infrastructure")

if os.path.isfile(SAS_CONFIG_FILE):
    with open(SAS_CONFIG_FILE, 'r') as config_file:
        sas_json = json.load(config_file)
        sas_servers_list = sas_json["sas_servers"]
    if sas_servers_list:
        with open(file_to_write, 'w') as whitelist_file:
            for sas_server_dict in sas_servers_list:
                whitelist_file.write(sas_server_dict['ip'] + '\n')
    else:
        os.remove(SIGNALING_CFG_DIR + "/clearwater-infrastructure")
        os.remove(MANAGEMENT_CFG_DIR + "/clearwater-infrastructure")
else:
    raise IOError("File is missing or inaccessible: %s", SAS_CONFIG_FILE)
