#! /usr/bin/python2.7

# @file clear_alarms.py
#
# Copyright (C) Metaswitch Networks
# If license terms are provided to you in a COPYING file in the root directory
# of the source code repository by which you are accessing this code, then
# the license outlined in that COPYING file applies to your use.
# Otherwise no rights are granted except for those provided to you by
# Metaswitch Networks in a separate written agreement.


# This script is used to clear all currently active SNMP alarms issued by a
# specified issuer. It takes a single parameter which identifies the issuer
# whose alarms are to be cleared. For example:
#
#   clear_alarms.py "monit"


import sys
import syslog
import alarms


if len(sys.argv) == 2:
  alarms.sendrequest(["clear-alarms", sys.argv[1]])
else:
  syslog.syslog(syslog.LOG_ERR, "unexpected parameter count: %d, cmd: %s" % (len(sys.argv), " ".join(sys.argv[:])))

sys.exit(0)
