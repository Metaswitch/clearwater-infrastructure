#!/bin/bash

# @file check-option-locations.sh
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

#
# ATTENTION
#
# All variables in the file are in uppercase to avoid clashes with real options
# in the config files.
#

# List all the options that definitely shouldn't be shared between nodes.
NON_SHARED_OPTIONS="local_ip public_ip public_hostname node_idx etcd_cluster etcd_cluster_key"

# Load the shared config
SHARED_CONFIG_FILE=/etc/clearwater/shared_config
source $SHARED_CONFIG_FILE

# Check each non-shared option in turn, and check its not present in our
# environment.
RC=0
for OPT in $NON_SHARED_OPTIONS; do
  # The `${!OPT}` use bash indirection - it checks the variable who name is
  # stored as the value of `OPT`
  if [[ -n ${!OPT} ]]; then
    echo "ERROR: $OPT is present in $SHARED_CONFIG_FILE"
    RC=1
  fi
done

exit $RC
