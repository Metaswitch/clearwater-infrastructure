#! /usr/bin/python

# @file ent_log.py
#
# Project Clearwater - IMS in the Cloud
# Copyright (C) 2014  Metaswitch Networks Ltd
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
  'CL_ETCD_POLL_FAILED': (
    CL_SCRIPT_ID + 4,
    syslog.LOG_ERR,
    'clearwater-etcd has become unresponsive.',
    'A regular monitoring check has not received a response from clearwater-etcd.',
    'Shared config management and datastore cluster management are no longer available.',
    'Monit will automatically restart unresponsive processes. '
      'This should resolve the issue without the need for further action.'
  ),




}

if len(sys.argv) >= 3:
  if sys.argv[2] in PDLogs:
    syslog.openlog(sys.argv[1], 1, syslog.LOG_LOCAL6)

    log = PDLogs[sys.argv[2]]

    if len(sys.argv) >= 4:
      msg = log[2] % tuple(sys.argv[3:])
    else:
      msg = log[2]

    syslog.syslog(log[1], '%d - Description: %s @@Cause: %s @@Effect: %s @@Action: %s' %
      (log[0], msg, log[3], log[4], log[5]))

