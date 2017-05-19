#! /usr/bin/python

# @file ent_log.py
#
# Copyright (C) Metaswitch Networks
# If license terms are provided to you in a COPYING file in the root directory
# of the source code repository by which you are accessing this code, then
# the license outlined in that COPYING file applies to your use.
# Otherwise no rights are granted except for those provided to you by
# Metaswitch Networks in a separate written agreement.


# This script is used to issue an ENT log. It takes two mandatory parameters,
# followed by a variable number of optional message variable parameters. The
# first parameter specifies the issuing entity. The second identfies the log
# template to be used. Optional parameters are used to fill the printf style
# variables used in the message string of the log template.
#
# For example:
#
#   ent_log.py namespace CL_SIG_NS_MISMATCH $signaling_namespace


import sys
import syslog

CL_SCRIPT_ID = 6000

# PDLogs is a map of log tuples, indexed by a log template identifier. The
# log tuple takes the following form (to align with the C++ equivalent in
# cpp-common/inculde/craft_ent_definitions.h).
#
# (Template ID,
#  Severity,
#  Message,
#  Cause,
#  Effect,
#  Action
# )

PDLogs = {
  'CL_SIG_NS_MISMATCH': (
    CL_SCRIPT_ID + 1,
    syslog.LOG_ERR,
    'Fatal - Clearwater signaling network namespace (%s) does not exist.',
    'The signaling network namespace (signaling_namespace) defined in /etc/clearwater/config '
    'does not exist in the kernel (ip netns list).',
    'Call processing is not available.',
    'Create the network namespace in the kernel, or adjust the value of signaling_namespace '
    'in /etc/clearwater/config to match the desired network namespace if it exists.'
  ),
  'CL_ETCD_STARTED': (
    CL_SCRIPT_ID + 2,
    syslog.LOG_NOTICE,
    'clearwater-etcd has started.',
    'The application is starting.',
    'Normal.',
    'None.'
  ),
  'CL_ETCD_EXITED': (
    CL_SCRIPT_ID + 3,
    syslog.LOG_ERR,
    'clearwater-etcd is exiting.',
    'The application is exiting.',
    'Shared config management and datastore cluster management are no longer available.',
    'This occurs normally when the application is stopped. Wait for monit to restart the application.'
  ),

}

if len(sys.argv) >= 3:
  if sys.argv[2] in PDLogs:
    syslog.openlog(sys.argv[1], 1, syslog.LOG_LOCAL7)

    log = PDLogs[sys.argv[2]]

    if len(sys.argv) >= 4:
      msg = log[2] % tuple(sys.argv[3:])
    else:
      msg = log[2]

    syslog.syslog(log[1], '%d - Description: %s @@Cause: %s @@Effect: %s @@Action: %s' %
      (log[0], msg, log[3], log[4], log[5]))

