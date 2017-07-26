#!/bin/sh

# @file clearwater-auto-config-aws.init.d
#
# Copyright (C) Metaswitch Networks 2017
# If license terms are provided to you in a COPYING file in the root directory
# of the source code repository by which you are accessing this code, then
# the license outlined in that COPYING file applies to your use.
# Otherwise no rights are granted except for those provided to you by
# Metaswitch Networks in a separate written agreement.

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

. /usr/share/clearwater-auto-config/bin/init-functions

# Changes in this command should be replicated in clearwater-auto-config-*.init.d
do_auto_config()
{
  local_ip=$(wget -qO - http://169.254.169.254/latest/meta-data/local-ipv4)
  public_ip=$(wget -qO - http://169.254.169.254/latest/meta-data/public-ipv4)
  public_hostname=$(wget -qO - http://169.254.169.254/latest/meta-data/public-hostname)

  write_config \
    $local_ip \
    $public_ip \
    $public_hostname \
    $public_hostname \
    $public_hostname
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

