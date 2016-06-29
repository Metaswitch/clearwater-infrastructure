# @file init-utils.sh
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

# Utilities to help writing init.d scripts. This should be sourced after any
# helper scripts provided by the linux distribution, as this script will
# provide some functions if the distro does not.

# Some logging functions are not available on centos. Define them here.
type log_daemon_msg >/dev/null 2>&1 || log_daemon_msg() { log_success_msg $@ ; }
type log_end_msg >/dev/null 2>&1 || log_end_msg() { true ; }

# Check if start-stop-daemon is available. Returns 0 if it is, non-0 if not.
have_start_stop_daemon()
{
  which start-stop-daemon >/dev/null 2>&1
}

# Function to stop a daemon.
#
# This function should be used on platforms such as centos where
# start-stop-daemon is not available. Its exit codes map the exit codes from
# start-stop-daemon.
#
# Parameters:
#  1: Path to the daemon's pidfile.
#  2: Signal to send to the daemon. May be specified either as a number or as a
#     signal name (so "6" and "ABRT" are both acceptable).  The signal must be
#     one that will cause the daemon to exit.
#  3: If the daemon has not exited this manty seconds after receiving the
#     signal, it will be killed.
#
# Return codes:
#   0 if daemon has been stopped
#   1 if daemon was already stopped
#   2 if daemon could not be stopped
#   3 if any other error occured
stop_daemon()
{
  if [ $# != 3 ]; then
    echo "$0 called with the wrong number of arguments ($#)"
    echo "Usage: $0 PIDFILE SIGNAL DELAY_BEFORE_KILL"
  fi

  local pidfile=$1
  local signal=$2
  local delay_before_kill=$3

  if [ -f "$pidfile" ]; then
    local pid=$(cat $PIDFILE)

    if checkpid $(cat $PIDFILE); then
      # The daemon is running. Kill it with the apprioriate signal.
      kill -$signal $pid

      # Give the dameon a chance to exit before checking if it is still alive.
      sleep 0.2

      # Wait up to `delay` seconds for the daemon to exit.
      for i in {1..$delay}; do
        if checkpid $pid; then
          sleep 1
        else
          break
        fi
      done

      if checkpid $pid; then
        # Daemon still hasn't exited. Kill it.
        kill -KILL $pid
        sleep 0.2
      fi

      if checkpid $pid; then
        # The daemon *still* hasn't exited. There's nothing more we can try.
        return 2
      else
        # The daemon has exited. Clean up its pidfile (if it hasn't already).
        rm -f $pidfile
        return 0
      fi
    else
      # Daemon is not running.
      return 1
    fi
  else
    # PID file does not exist so assume the daemon is not running
    return 1
  fi
}
