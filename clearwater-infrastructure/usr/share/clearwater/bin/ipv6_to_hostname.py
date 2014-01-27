# @file ipv6_to_hostname.py
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

import socket
import binascii
import sys
import os

# The scripts takes an IPv6 address as string and converts it to an ip6.arpa
# hostname.  This is done
if len(sys.argv) == 2:
    ip_address = sys.argv[1]
else:
    # Don't print out a usage string as the calling script may try to use this
    # as a hostname.
    sys.exit(0)

# Convert the IP address into a 128 bit binary representation.  This does not
# include the colons, but does include all of the zero padding.  If the string
# passed in is not a valid IPv6 address inet_pton will throw an exception.
try:
    binary_address = socket.inet_pton(socket.AF_INET6, ip_address)
except socket.error:
    sys.exit(0)

# Generate an ASCII representation of the binary IP address.
ascii_address = binascii.b2a_hex(binary_address)

# Step backwards through the ASCII representation, building up a hostname made
# up of the individual nibbles separated by dots.
hostname_string = ""
for nibble in reversed(ascii_address):
    hostname_string += nibble + "."

# Append the standard  reversed IPv6 address domain name.
hostname_string += "ip6.arpa"

# Print out the hostname for use by the calling script.
print (hostname_string)
