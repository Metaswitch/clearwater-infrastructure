/**
 * @file ipv6-to-hostname.cpp
 *
 * Copyright (C) Metaswitch Networks 2016
 * If license terms are provided to you in a COPYING file in the root directory
 * of the source code repository by which you are accessing this code, then
 * the license outlined in that COPYING file applies to your use.
 * Otherwise no rights are granted except for those provided to you by
 * Metaswitch Networks in a separate written agreement.
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
