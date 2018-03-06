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

def create_directory(path_to_create):
    if not os.path.exists(path_to_create):
        os.makedirs(path_to_create)

def delete_file(path_to_delete):
    if os.path.exists(path_to_delete):
        os.remove(path_to_delete)

def main(sas_use_signaling_namespace):
    create_directory(SIGNALING_CFG_DIR)
    create_directory(MANAGEMENT_CFG_DIR)

    # Ready the whitelist file to write to for the specfied namespace, and delete the
    # un-needed namespace whitelist file.
    if sas_use_signaling_namespace is "Y":
        file_to_write = SIGNALING_CFG_DIR + "/clearwater-infrastructure"
        delete_file(MANAGEMENT_CFG_DIR + "/clearwater-infrastructure")
    else:
        file_to_write = MANAGEMENT_CFG_DIR + "/clearwater-infrastructure"
        delete_file(SIGNALING_CFG_DIR + "/clearwater-infrastructure")

    # Print the list of SAS IPs in sas.json, each on a new line.
    if os.path.isfile(SAS_CONFIG_FILE):
        with open(SAS_CONFIG_FILE, 'r') as config_file:
            sas_json = json.load(config_file)
            sas_servers_list = sas_json["sas_servers"]
        if sas_servers_list:
            with open(file_to_write, 'w') as whitelist_file:
                for sas_server_dict in sas_servers_list:
                    whitelist_file.write(sas_server_dict['ip'] + '\n')
        # Delete the whitelist files if no SAS IPs are configured.
        else:
            delete_file(SIGNALING_CFG_DIR + "/clearwater-infrastructure")
            delete_file(MANAGEMENT_CFG_DIR + "/clearwater-infrastructure")
    else:
        raise IOError("File is missing or inaccessible: %s", SAS_CONFIG_FILE)

if __name__ == "__main__":  # pragma: no cover
    main(sys.argv[1])
