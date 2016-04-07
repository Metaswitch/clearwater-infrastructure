#!/bin/sh

# @file clearwater-auto-config-docker.init.d
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
# Provides:          clearwater-auto-config-docker
# Required-Start:    $network $local_fs
# Required-Stop:
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: clearwater-auto-config-docker
# Description:       clearwater-auto-config-docker
# X-Start-Before:    clearwater-infrastructure bono sprout homer homestead ellis restund
### END INIT INFO

# Changes in this command should be replicated in clearwater-auto-config-*.init.d
do_auto_config()
{
  local_config=/etc/clearwater/local_config
  shared_config=/etc/clearwater/shared_config

  if [ -f /etc/clearwater/force_ipv6 ]
  then
    # The sed expression finds the first IPv6
    ip=$(hostname -I | sed -e 's/\(^\|^[0-9. ]* \)\([0-9A-Fa-f:]*\)\( .*$\|$\)/\2/g')
  else
    # The sed expression finds the first IPv4 address in the space-separate list of IPv4 and IPv6 addresses.
    # If there are no IPv4 addresses it finds the first IPv6 address.
    ip=$(hostname -I | sed -e 's/\(^\|^[0-9A-Fa-f: ]* \)\([0-9.][0-9.]*\)\( .*$\|$\)/\2/g' -e 's/\(^\)\(^[0-9A-Fa-f:]*\)\( .*$\|$\)/\2/g')
  fi

  # Add square brackets around the address iff it is an IPv6 address
  bracketed_ip=$(python /usr/share/clearwater/clearwater-auto-config-docker/bin/bracket_ipv6_address.py $ip)

  sed -e 's/^local_ip=.*$/local_ip='$ip'/g
          s/^public_ip=.*$/public_ip='$ip'/g
          s/^public_hostname=.*$/public_hostname='$ip'/g' -i $local_config

  if [ -n "$ETCD_PROXY" ]
  then
    # Set up etcd proxy configuration from environment.  Shared configuration
    # should be uploaded and shared manually.
    sed -e '/^etcd_cluster=.*/d
            /^etcd_proxy=.*/d' -i $local_config
    echo "etcd_proxy=$ETCD_PROXY" >> $local_config

    # Remove the default shared configuration file.
    rm -f $shared_config
  else
    # Set up shared configuration on each node.
    if [ -z "$ZONE" ]
    then
      # Assume the domain is example.com, and use the Docker internal DNS for service discovery.
      # See https://docs.docker.com/engine/userguide/networking/configure-dns/ for details.
      sprout_hostname=sprout
      hs_hostname=homestead:8888
      hs_provisioning_hostname=homestead:8889
      xdms_hostname=homer:7888
      upstream_hostname=sprout
      ralf_hostname=ralf:10888
      home_domain="example.com"
    else
      # Configure relative to the base zone and rely on externally configured DNS entries.
      sprout_hostname=sprout.$ZONE
      hs_hostname=hs.$ZONE:8888
      hs_provisioning_hostname=hs.$ZONE:8889
      xdms_hostname=homer.$ZONE:7888
      upstream_hostname=sprout.$ZONE
      ralf_hostname=ralf.$ZONE:10888
      home_domain=$ZONE
    fi

    sed -e 's/^home_domain=.*$/home_domain='$home_domain'/g
            s/^sprout_hostname=.*$/sprout_hostname='$sprout_hostname'/g
            s/^xdms_hostname=.*$/xdms_hostname='$xdms_hostname'/g
            s/^hs_hostname=.*$/hs_hostname='$hs_hostname'/g
            s/^hs_provisioning_hostname=.*$/hs_provisioning_hostname='$hs_provisioning_hostname'/g
            s/^upstream_hostname=.*$/upstream_hostname='$upstream_hostname'/g
            s/^ralf_hostname=.*$/ralf_hostname='$ralf_hostname'/g
            s/^email_recovery_sender=.*$/email_recovery_sender=clearwater@'$home_domain'/g' -i $shared_config

    # Extract DNS servers from resolv.conf and comma-separate them.
    nameserver=`grep nameserver /etc/resolv.conf | cut -d ' ' -f 2`
    nameserver=`echo $nameserver | tr ' ' ','`
    if [ -n "$nameserver" ]
    then
      sed -e '/^signaling_dns_server=.*/d' -i $shared_config
      echo "signaling_dns_server=$nameserver" >> $shared_config
    fi
  fi

  # Sprout will replace the cluster-settings file with something appropriate when it starts
  rm -f /etc/clearwater/cluster_settings

  # Set up DNS for the S-CSCF
  grep -v ' #+scscf.aio$' /etc/hosts > /tmp/hosts.$$
  echo $ip scscf.$sprout_hostname '#+scscf.aio'>> /tmp/hosts.$$
  mv /tmp/hosts.$$ /etc/hosts

  service dnsmasq restart
}

case "$1" in
  start|restart|reload|force-reload)
    do_auto_config
    exit 0
  ;;

  status|stop)
    exit 0
  ;;

  *)
    echo "Usage: $SCRIPTNAME {start|stop|status|restart|force-reload}" >&2
    exit 3
  ;;
esac

:

