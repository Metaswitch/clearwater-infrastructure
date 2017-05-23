#!/bin/bash

# @file poll_memcached.sh
#
# Copyright (C) Metaswitch Networks 2017
# If license terms are provided to you in a COPYING file in the root directory
# of the source code repository by which you are accessing this code, then
# the license outlined in that COPYING file applies to your use.
# Otherwise no rights are granted except for those provided to you by
# Metaswitch Networks in a separate written agreement.

# This script polls a memcached process and check whether it is healthy by checking
# that the port is open.

# Grab our configuration - we just use the local IP address.
. /etc/clearwater/config
[ -z "$signaling_namespace" ] || namespace_prefix="ip netns exec $signaling_namespace"
PORT=11211

# Do the poll - connect, issue a version command and check that it looks correct.
$namespace_prefix nc -v -w 2 $local_ip $PORT <<< "version" 2> /tmp/poll_memcached.sh.nc.stderr.$$ | tee /tmp/poll_memcached.sh.nc.stdout.$$ | head -1 | egrep -q "^VERSION "
rc=$?

# Check the return code and log if appropriate
if [ $rc != 0 ] ; then
  echo memcached poll failed to $local_ip $PORT >&2
  cat /tmp/poll_memcached.sh.nc.stderr.$$       >&2
  cat /tmp/poll_memcached.sh.nc.stdout.$$       >&2
fi
rm -f /tmp/poll_memcached.sh.nc.stderr.$$ /tmp/poll_memcached.sh.nc.stdout.$$

# Return the return code from the nc command (0 if connected, 1 if not).
exit $rc
