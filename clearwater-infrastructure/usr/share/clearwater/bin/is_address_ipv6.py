#! /usr/bin/python

# @file is_address_ipv6.py
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
#

import sys
import socket

# This script takes an input string and attempts to parse it as an IPv6 address.
# Return 1 if the string is a valid IPv6 address and 0 otherwise.

def main (ip_address):

    # Attempt to convert the IP address into a 128 bit binary representation.
    # If the string parses successfully return '1'.  If the string passed in
    # is not a valid IPv6 address inet_pton will throw an exception.  Handle
    # the exception and return 0.
    try:
        binary_address = socket.inet_pton(socket.AF_INET6, ip_address)
        return(1)
    except socket.error:
        return(0)

if __name__ == "__main__":
    if len(sys.argv) == 2:
        rc = main(sys.argv[1])
        sys.exit(rc)
    else:
        sys.exit(0)

