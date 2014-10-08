#! /usr/bin/python2.7

# @file clear_alarms.py
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


# This script is used to clear all currently active SNMP alarms issued by a
# specified issuer. It takes a single parameter which identifies the issuer
# whose alarms are to be cleared. For example:
#
#   clear_alarms.py "monit"


import sys
import syslog
import alarms


if len(sys.argv) != 2:
  syslog.syslog(syslog.LOG_ERR, "unexpected parameter count: %d, cmd: %s" % (len(sys.argv), " ".join(sys.argv[:])))
  sys.exit(0)

alarms.sendrequest(["clear-alarms", sys.argv[1]])

sys.exit(0)
