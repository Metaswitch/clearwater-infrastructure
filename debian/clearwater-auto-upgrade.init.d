#!/bin/sh

# @file clearwater-auto-upgrade.init.d
#
# Copyright (C) Metaswitch Networks 2017
# If license terms are provided to you in a COPYING file in the root directory
# of the source code repository by which you are accessing this code, then
# the license outlined in that COPYING file applies to your use.
# Otherwise no rights are granted except for those provided to you by
# Metaswitch Networks in a separate written agreement.

### BEGIN INIT INFO
# Provides:          clearwater-auto-upgrade
# Required-Start:    $network $local_fs
# Required-Stop:
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Clearwater auto upgrader
# Description:       Enables automatic upgrade of Clearwater software
# X-Start-Before:    clearwater-infrastructure bono sprout homer homestead ellis restund
### END INIT INFO

# PATH should only include /usr/* if it runs after the mountnfs.sh script
PATH=/sbin:/usr/sbin:/bin:/usr/bin
NAME=clearwater-auto-upgrade             # Introduce the short server's name here

# Read configuration variable file if it is present
[ -r /etc/default/$NAME ] && . /etc/default/$NAME

# Load the VERBOSE setting and other rcS variables
[ -r /lib/init/vars.sh ] && . /lib/init/vars.sh

do_upgrade()
{
        # Upgrade any installed Metaswitch-maintained packages
        if which yum > /dev/null 2>&1 ; then
                if ! ps $(cat /var/run/yum.pid) > /dev/null
                then
                    clearwater-upgrade -y
                fi
        else
                if ! fuser -s /var/lib/dpkg/lock
                then
                    export DEBIAN_FRONTEND=noninteractive
                    clearwater-upgrade -y --force-yes
                fi
        fi

        return 0
}

case "$1" in
  start|restart|reload|force-reload)
        do_upgrade
        exit 0
        ;;
  stop)
        exit 0
        ;;
  status)
        exit 0
        ;;
  *)
        #echo "Usage: $SCRIPTNAME {start|stop|restart|reload|force-reload}" >&2
        echo "Usage: $SCRIPTNAME {start|stop|status|restart|force-reload}" >&2
        exit 3
        ;;
esac

:
