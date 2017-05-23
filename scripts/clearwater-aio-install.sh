#!/bin/bash
#
# Copyright (C) Metaswitch Networks 2017
# If license terms are provided to you in a COPYING file in the root directory
# of the source code repository by which you are accessing this code, then
# the license outlined in that COPYING file applies to your use.
# Otherwise no rights are granted except for those provided to you by
# Metaswitch Networks in a separate written agreement.

# This installs the Clearwater packages onto an AIO node. It sets up which
# repo to pull the packages from, and creates numbers on Ellis. This is
# used by the OVF install, AIO install through Chef, and the AMI creation
set -e

if [[ $EUID -ne 0 ]]
then
  echo "You must run this script with root permissions"
  exit 1
fi

if [[ $# -lt 1 || $# -gt 5 ]]
then
  echo "Usage: clearwater-aio-install [auto_config_package] <install_repo> <updates_repo> <number_start> <number_count>"
  exit 1
fi

auto_package=$1
install_repo=$2
updates_repo=$3
number_start=$4
number_count=$5

[ -n "$install_repo" ] || install_repo=http://repo.cw-ngv.com/stable
[ -n "$updates_repo" ] || updates_repo=http://repo.cw-ngv.com/stable
[ -n "$number_start" ] || number_start=6505550000
[ -n "$number_count" ] || number_count=1000

# Set up the repo
echo deb $install_repo binary/ > /etc/apt/sources.list.d/clearwater.list
curl -L http://repo.cw-ngv.com/repo_key | sudo apt-key add -
apt-get update

# Install the initial clearwater packages
export DEBIAN_FRONTEND=noninteractive
apt-get install -y --force-yes $auto_package clearwater-management clearwater-cassandra < /dev/null

# Install the remaining clearwater packages
apt-get install -y --force-yes ellis-node bono-node restund sprout-node homer-node homestead-node clearwater-prov-tools < /dev/null

# Create numbers on Ellis
export PATH=/usr/share/clearwater/ellis/env/bin:$PATH
python /usr/share/clearwater/ellis/src/metaswitch/ellis/tools/create_numbers.py --start $number_start --count $number_count

# Now switch over to using the repo we expect to get updates from.
echo deb $updates_repo binary/ > /etc/apt/sources.list.d/clearwater.list
