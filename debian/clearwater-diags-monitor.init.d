#!/bin/sh

# @file clearwater-diags-monitor.init.d
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
# Provides:          clearwater-diags-monitor
# Required-Start:    $network $local_fs
# Required-Stop:
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Clearwater infrastructure
# Description:       Determines and applies local configuration
# X-Start-Before:    memcached bono sprout restund
### END INIT INFO

# PATH should only include /usr/* if it runs after the mountnfs.sh script
PATH=/sbin:/usr/sbin:/bin:/usr/bin
DESC=clearwater-diags-monitor             # Introduce a short description here
NAME=clearwater-diags-monitor             # Introduce the short server's name here
SCRIPTNAME=/etc/init.d/$NAME
PIDFILE=/var/run/clearwater_diags_monitor.pid
DAEMON=/usr/share/clearwater/bin/clearwater_diags_monitor

# Exit if the package is not installed
[ -x $DAEMON ] || exit 0

# Read configuration variable file if it is present
[ -r /etc/default/$NAME ] && . /etc/default/$NAME

# Load the VERBOSE setting and other rcS variables
[ -r /lib/init/vars.sh ] && . /lib/init/vars.sh

# Define LSB log_* functions.
# Depend on lsb-base (>= 3.0-6) to ensure that this file is present.
. /lib/lsb/init-functions
type log_daemon_msg >/dev/null 2>&1 || log_daemon_msg() { log_success_msg $@ ; }
type log_end_msg >/dev/null 2>&1 || log_end_msg() { true ; }

# Include /etc/init.d/functions if available.
[ -r /etc/init.d/functions ] && . /etc/init.d/functions

#
# Function that starts the daemon/service
#
do_start()
{
        # Fix up the core pattern before starting.
        cat /etc/clearwater/diags-monitor/core_pattern > /proc/sys/kernel/core_pattern

        # Ensure sysstat is running (so SAR can be used to gather usgae stats).
        service sysstat start

        # Start running the diags monitor.
        # Return
        #   0 if daemon has been started
        #   1 if daemon was already running
        #   2 if daemon could not be started
        if which start-stop-daemon > /dev/null 2>&1 ; then
                start-stop-daemon --start --quiet --pidfile $PIDFILE --exec $DAEMON --test > /dev/null \
                        || return 1
                start-stop-daemon --start --quiet --background --make-pidfile --pidfile $PIDFILE --nicelevel 19 --iosched idle --exec $DAEMON \
                        || return 2
        else
                [ ! -f $PIDFILE ] || checkpid $(cat $PIDFILE) || return 1
                ionice -n 3 nice -n 19 daemonize -p $PIDFILE $DAEMON || return 2
        fi

        return 0
}

#
# Function that stops the daemon/service
#
do_stop()
{
        # Stop running the diags monitor.
        # Return
        #   0 if daemon has been stopped
        #   1 if daemon was already stopped
        #   2 if daemon could not be stopped
        #   other if a failure occurred
        if which start-stop-daemon > /dev/null 2>&1 ; then
                start-stop-daemon --stop --quiet --retry=TERM/30/KILL/5 --pidfile $PIDFILE
        else
                [ ! -f $PIDFILE ] || killproc -p $(cat $PIDFILE) -d 30
                rm -f $PIDFILE
                pkill -f $DAEMON
        fi
        return $?
}

#
# Function that sends a SIGHUP to the daemon/service
#
do_reload() {
        # Nothing to do
        return 0
}

case "$1" in
  start)
    [ "$VERBOSE" != no ] && log_daemon_msg "Starting $DESC " "$NAME"
    do_start
    case "$?" in
                0|1) [ "$VERBOSE" != no ] && log_end_msg 0 ;;
                2) [ "$VERBOSE" != no ] && log_end_msg 1 ;;
        esac
  ;;
  stop)
        [ "$VERBOSE" != no ] && log_daemon_msg "Stopping $DESC" "$NAME"
        do_stop
        case "$?" in
                0|1) [ "$VERBOSE" != no ] && log_end_msg 0 ;;
                2) [ "$VERBOSE" != no ] && log_end_msg 1 ;;
        esac
        ;;
  status)
       status_of_proc "$DAEMON" "$NAME" && exit 0 || exit $?
       ;;
  reload|force-reload)
        log_daemon_msg "Reloading $DESC" "$NAME"
        do_reload
        log_end_msg $?
        ;;
  restart)
        log_daemon_msg "Restarting $DESC" "$NAME"
        do_stop
        case "$?" in
          0|1)
                do_start
                case "$?" in
                        0) log_end_msg 0 ;;
                        1) log_end_msg 1 ;; # Old process is still running
                        *) log_end_msg 1 ;; # Failed to start
                esac
                ;;
          *)
                # Failed to stop
                log_end_msg 1
                ;;
        esac
        ;;
  *)
        #echo "Usage: $SCRIPTNAME {start|stop|restart|reload|force-reload}" >&2
        echo "Usage: $SCRIPTNAME {start|stop|status|restart|force-reload}" >&2
        exit 3
        ;;
esac

:
