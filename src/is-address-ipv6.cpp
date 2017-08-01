/**
 * @file is-address-ipv6.cpp
 *
 * Copyright (C) Metaswitch Networks 2016
 * If license terms are provided to you in a COPYING file in the root directory
 * of the source code repository by which you are accessing this code, then
 * the license outlined in that COPYING file applies to your use.
 * Otherwise no rights are granted except for those provided to you by
 * Metaswitch Networks in a separate written agreement.
 */

// This tool takes a string, and returns 0 if it is an IPv6 address or 1 if not.
//
// Note that per RFC 2373, an IPv6 address does not contain square
// brackets, and this script will return 1 if such an IPv6 address is given.
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
    fprintf(stderr, "Usage : is-address-ipv6 <IP address>\n");
    return 2;
  }

  // Try to parse it.
  if (inet_pton(AF_INET6, argv[1], &addr))
  {
    // It's an IPv6 address - return 0 (success in shell-land).
    return 0;
  }
  else
  {
    // Not an IPv6 address - return 1 (failure in shell-land).
    return 1;
  }
}
