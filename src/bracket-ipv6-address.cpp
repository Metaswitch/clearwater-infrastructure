/**
 * @file bracket-ipv6-address.cpp
 *
 * Copyright (C) Metaswitch Networks
 * If license terms are provided to you in a COPYING file in the root directory
 * of the source code repository by which you are accessing this code, then
 * the license outlined in that COPYING file applies to your use.
 * Otherwise no rights are granted except for those provided to you by
 * Metaswitch Networks in a separate written agreement.
 */

// This tool takes an IP address as a string.  If the IP address is IPv4 it
// returns it unchanged.  If it is IPv6 it returns it with square brackets.
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
    fprintf(stderr, "Usage : bracket-ipv6-address <IP address>\n");
    return 2;
  }

  // Try to parse it.
  if (inet_pton(AF_INET6, argv[1], &addr))
  {
    // It's an IPv6 address - surround it with square brackets.
    printf("[%s]\n", argv[1]);
  }
  else
  {
    // Not an IPv6 address - return as-is.
    printf("%s\n", argv[1]);
  }

  return 0;
}
