# @file init-utils.sh
#
# Copyright (C) Metaswitch Networks 2016
# If license terms are provided to you in a COPYING file in the root directory
# of the source code repository by which you are accessing this code, then
# the license outlined in that COPYING file applies to your use.
# Otherwise no rights are granted except for those provided to you by
# Metaswitch Networks in a separate written agreement.

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
