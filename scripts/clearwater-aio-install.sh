#!/bin/bash
#
# Project Clearwater - IMS in the Cloud
# Copyright (C) 2015  Metaswitch Networks Ltd
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

# This installs the Clearwater packages onto an AIO node. It sets up which
# repo to pull the packages from, and creates numbers on Ellis. This is
# used by the OVF install, AIO install through Chef, and the AMI creation
set -e

if [[ $EUID -ne 0 ]]
then
  echo "You must run this script with root permissions"
  exit 1
fi

if [[ $# -lt 1 || $# -gt 4 ]]
then
  echo "Usage: clearwater-aio-install [auto_config_package] <repo> <number_start> <number_count>"
  exit 1
fi

auto_package=$1
repo=$2
number_start=$3
number_count=$4

[ -n "$repo" ] || repo=http://repo.cw-ngv.com/stable
[ -n "$number_start" ] || number_start=6505550000
[ -n "$number_count" ] || number_count=1000

# Set up the repo
echo deb $repo binary/ > /etc/apt/sources.list.d/clearwater.list
curl -L http://repo.cw-ngv.com/repo_key | sudo apt-key add -
apt-get update

# Install the initial clearwater packages
export DEBIAN_FRONTEND=noninteractive
apt-get install -y --force-yes $auto_package clearwater-management clearwater-cassandra < /dev/null

# Install the remaining clearwater packages
apt-get install -y --force-yes ellis bono restund sprout homer homestead homestead-prov clearwater-prov-tools < /dev/null

# Create numbers on Ellis
export PATH=/usr/share/clearwater/ellis/env/bin:$PATH
python /usr/share/clearwater/ellis/src/metaswitch/ellis/tools/create_numbers.py --start $number_start --count $number_count
