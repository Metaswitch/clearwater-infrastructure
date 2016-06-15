/**
 * @file ipv6-to-hostname.cpp
 *
 * Project Clearwater - IMS in the Cloud
 * Copyright (C) 2016  Metaswitch Networks Ltd
 *
 * This program is free software: you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the
 * Free Software Foundation, either version 3 of the License, or (at your
 * option) any later version, along with the "Special Exception" for use of
 * the program along with SSL, set forth below. This program is distributed
 * in the hope that it will be useful, but WITHOUT ANY WARRANTY;
 * without even the implied warranty of MERCHANTABILITY or FITNESS FOR
 * A PARTICULAR PURPOSE.  See the GNU General Public License for more
 * details. You should have received a copy of the GNU General Public
 * License along with this program.  If not, see
 * <http://www.gnu.org/licenses/>.
 *
 * The author can be reached by email at clearwater@metaswitch.com or by
 * post at Metaswitch Networks Ltd, 100 Church St, Enfield EN2 6BQ, UK
 *
 * Special Exception
 * Metaswitch Networks Ltd  grants you permission to copy, modify,
 * propagate, and distribute a work formed by combining OpenSSL with The
 * Software, or a work derivative of such a combination, even if such
 * copying, modification, propagation, or distribution would otherwise
 * violate the terms of the GPL. You must comply with the GPL in all
 * respects for all of the code used other than OpenSSL.
 * "OpenSSL" means OpenSSL toolkit software distributed by the OpenSSL
 * Project and licensed under the OpenSSL Licenses, or a work based on such
 * software and licensed under the OpenSSL Licenses.
 * "OpenSSL Licenses" means the OpenSSL License and Original SSLeay License
 * under which the OpenSSL Project distributes the OpenSSL toolkit software,
 * as those licenses appear in the file LICENSE-OPENSSL.
 */

// This tool takes an IP address as a string and converts it to an ip6.arpa
// hostname.
//
// Writing this in C++ might seem like overkill.  However,
// - parsing using a regular expression (and sed) is surprisingly complicated
// - there is a bug in Python that makes it hang on occasion
// - this code is very rarely changed, so maintainability is not a big concern.

#include <stdio.h>
#include <arpa/inet.h>

int main(int argc, char **argv)
{
  struct in6_addr addr;

  // Check that we have the right parameters.
  if (argc != 2)
  {
    fprintf(stderr, "Usage : ipv6-to-hostname <IP address>\n");
    return 2;
  }

  // Parse it.
  if (!inet_pton(AF_INET6, argv[1], &addr))
  {
    fprintf(stderr, "Invalid IPv6 address %s\n", argv[1]);
    return 1;
  }

  // Print it out in hex in reverse order, followed by "ip6.arpa".
  for (int ii = 7; ii >= 0; ii--)
  {
    // The address is stored as 16 chars in network order, but we want to
    // print as 8 16-bit "groups" (in host order), so we need to byte-swap it.
    uint16_t group = htons(((uint16_t*)addr.s6_addr)[ii]);
    printf("%x.", group);
  }
  printf("ip6.arpa\n");

  return 0;
}
