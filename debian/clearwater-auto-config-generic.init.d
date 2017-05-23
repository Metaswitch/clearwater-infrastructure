#!/bin/sh

# @file clearwater-auto-config-generic.init.d
#
# Copyright (C) Metaswitch Networks 2017
# If license terms are provided to you in a COPYING file in the root directory
# of the source code repository by which you are accessing this code, then
# the license outlined in that COPYING file applies to your use.
# Otherwise no rights are granted except for those provided to you by
# Metaswitch Networks in a separate written agreement.

### BEGIN INIT INFO
# Provides:          clearwater-auto-config-generic
# Required-Start:    $network $local_fs
# Required-Stop:
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: clearwater-auto-config-generic
# Description:       clearwater-auto-config-generic
# X-Start-Before:    clearwater-infrastructure bono sprout homer homestead ellis restund
### END INIT INFO

# Changes in this command should be replicated in clearwater-auto-config-*.init.d
do_auto_config()
{
  local_config=/etc/clearwater/local_config
  shared_config=/etc/clearwater/shared_config
  aio_hostname=cw-aio

  if [ -f /etc/clearwater/force_ipv6 ]
  then
    # The sed expression finds the first IPv6
    ip=$(hostname -I | sed -e 's/\(^\|^[0-9. ]* \)\([0-9A-Fa-f:]*\)\( .*$\|$\)/\2/g')
  else
    # The sed expression finds the first IPv4 address in the space-separate list of IPv4 and IPv6 addresses.
    # If there are no IPv4 addresses it finds the first IPv6 address.
    ip=$(hostname -I | sed -e 's/\(^\|^[0-9A-Fa-f: ]* \)\([0-9.][0-9.]*\)\( .*$\|$\)/\2/g' -e 's/\(^\)\(^[0-9A-Fa-f:]*\)\( .*$\|$\)/\2/g')
  fi

  sed -e 's/^local_ip=.*$/local_ip='$ip'/g
          s/^public_ip=.*$/public_ip='$ip'/g
          s/^etcd_cluster=.*$/etcd_cluster='$ip'/g
          s/^public_hostname=.*$/public_hostname='$aio_hostname'/g' -i $local_config

  # Add square brackets around the address iff it is an IPv6 address
  bracketed_ip=$(/usr/share/clearwater/clearwater-auto-config-generic/bin/bracket-ipv6-address $ip)

  sed -e 's/^sprout_hostname=.*$/sprout_hostname='$aio_hostname'/g
          s/^xdms_hostname=.*$/xdms_hostname='$bracketed_ip':7888/g
          s/^hs_hostname=.*$/hs_hostname='$bracketed_ip':8888/g
          s/^hs_provisioning_hostname=.*$/hs_provisioning_hostname='$bracketed_ip':8889/g
          s/^sprout_registration_store=.*$/sprout_registration_store='$bracketed_ip'/g
          s/^upstream_hostname=.*$/upstream_hostname=scscf.'$aio_hostname'/g' -i $shared_config

  # Sprout will replace the cluster-settings file with something appropriate when it starts
  rm -f /etc/clearwater/cluster_settings

  # Set up DNS for the S-CSCF
  grep -v ' #+clearwater-aio$' /etc/hosts > /tmp/hosts.$$
  echo $ip $aio_hostname '#+clearwater-aio'>> /tmp/hosts.$$
  echo $ip scscf.$aio_hostname '#+clearwater-aio'>> /tmp/hosts.$$
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

