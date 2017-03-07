#!/bin/sh

# @file clearwater-auto-config-aws.init.d
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

### BEGIN INIT INFO
# Provides:          clearwater-auto-config-aws
# Required-Start:    $network $local_fs
# Required-Stop:
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: clearwater-auto-config-aws
# Description:       clearwater-auto-config-aws
# X-Start-Before:    clearwater-infrastructure bono sprout homer homestead ellis restund
### END INIT INFO

# Changes in this command should be replicated in clearwater-auto-config-*.init.d
do_auto_config()
{
  mkdir -p /etc/clearwater

  local_config=/etc/clearwater/local_config
  shared_config=/etc/clearwater/shared_config

  local_ip=$(wget -qO - http://169.254.169.254/latest/meta-data/local-ipv4)
  public_ip=$(wget -qO - http://169.254.169.254/latest/meta-data/public-ipv4)
  public_hostname=$(wget -qO - http://169.254.169.254/latest/meta-data/public-hostname)

  sed -e 's/^local_ip=.*$/local_ip='$local_ip'/g
          s/^public_ip=.*$/public_ip='$public_ip'/g
          s/^etcd_cluster=.*$/etcd_cluster='$local_ip'/g
          s/^public_hostname=.*$/public_hostname='$public_hostname'/g' -i $local_config

  sed -e 's/^sprout_hostname=.*$/sprout_hostname='$public_hostname'/g
          s/^xdms_hostname=.*$/xdms_hostname='$public_hostname':7888/g
          s/^hs_hostname=.*$/hs_hostname='$public_hostname':8888/g
          s/^hs_provisioning_hostname=.*$/hs_provisioning_hostname='$public_hostname':8889/g
          s/^sprout_registration_store=.*$/sprout_registration_store='$public_hostname'/g
          s/^upstream_hostname=.*$/upstream_hostname='$public_hostname'/g' -i $shared_config

  # Sprout will replace the cluster-settings file with something appropriate when it starts
  rm -f /etc/clearwater/cluster_settings

  # Set up DNS for the S-CSCF
  grep -v ' #+scscf.aio$' /etc/hosts > /tmp/hosts.$$
  echo $local_ip scscf.$public_hostname '#+scscf.aio'>> /tmp/hosts.$$
  mv /tmp/hosts.$$ /etc/hosts

  service dnsmasq restart
}

case "$1" in
  start|restart|reload|force-reload)
    do_auto_config
    exit 0
  ;;

  status)
    exit 0
  ;;

  stop)
    echo "Remove any chef PEM files"
    find /etc/chef/*.pem -exec rm -f {} \; || true
    exit 0
  ;;

  *)
    echo "Usage: $SCRIPTNAME {start|stop|status|restart|force-reload}" >&2
    exit 3
  ;;
esac

:

