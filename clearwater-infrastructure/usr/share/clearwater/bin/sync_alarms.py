#! /usr/bin/python2.7

# @file sync_alarms.py
#
# Copyright (C) Metaswitch Networks 2017
# If license terms are provided to you in a COPYING file in the root directory
# of the source code repository by which you are accessing this code, then
# the license outlined in that COPYING file applies to your use.
# Otherwise no rights are granted except for those provided to you by
# Metaswitch Networks in a separate written agreement.


# This script is intended to be used by an external management system to
# synchronize SNMP alarm state. When invoked without any parameters it
# will trigger a clear for all known alarms on this node, followed by a
# re-issue of all currently active alarms. When invoked with the --noclear
# option it will only re-issue all currently active alarms.


import sys
import syslog
import alarms


if len(sys.argv) == 1:
  alarms.sendrequest(["sync-alarms"])
else:
  syslog.syslog(syslog.LOG_ERR, "unexpected parameter count: %d, cmd: %s" % (len(sys.argv), " ".join(sys.argv[:])))

sys.exit(0)
