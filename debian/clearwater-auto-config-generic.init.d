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

. /usr/share/clearwater-auto-config/bin/init-functions

# Changes in this command should be replicated in clearwater-auto-config-*.init.d
do_auto_config()
{
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

  # Add square brackets around the address iff it is an IPv6 address
  bracketed_ip=$(/usr/share/clearwater/clearwater-auto-config-generic/bin/bracket-ipv6-address $ip)

  # Call through to update the config using the generic function
  write_config $ip $ip $aio_hostname $bracketed_ip "scscf.$aio_hostname"
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

