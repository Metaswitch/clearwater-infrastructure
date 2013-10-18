/**
* Project Clearwater - IMS in the Cloud
* Copyright (C) 2013 Metaswitch Networks Ltd
*
* This program is free software: you can redistribute it and/or modify it
* under the terms of the GNU General Public License as published by the
* Free Software Foundation, either version 3 of the License, or (at your
* option) any later version, along with the "Special Exception" for use of
* the program along with SSL, set forth below. This program is distributed
* in the hope that it will be useful, but WITHOUT ANY WARRANTY;
* without even the implied warranty of MERCHANTABILITY or FITNESS FOR
* A PARTICULAR PURPOSE. See the GNU General Public License for more
* details. You should have received a copy of the GNU General Public
* License along with this program. If not, see
* <http://www.gnu.org/licenses/>.
*
* The author can be reached by email at clearwater@metaswitch.com or by
* post at Metaswitch Networks Ltd, 100 Church St, Enfield EN2 6BQ, UK
*
* Special Exception
* Metaswitch Networks Ltd grants you permission to copy, modify,
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

#include <boost/algorithm/string.hpp>
#include <iostream>
#include <cstdlib>
#include "oid.hpp"

OID::OID(oid* oids_ptr, int len) {
  int i;
  for (i = 0; i < len; i++) {
    oids_.push_back(*(oids_ptr+i));
  }
}


OID::OID(std::string oidstr)
{
  std::vector<std::string> result;
  boost::split(result, oidstr, boost::is_any_of("."));
  for (std::vector<std::string>::iterator it = result.begin() ; it != result.end(); ++it) {
    if (!it->empty()) { // Ignore an initial dot
      oids_.push_back(atoi(it->c_str()));
    }
  }
}


const oid* OID::get_ptr() const {
  return &oids_[0];
}

int OID::get_len() const {
  return oids_.size();
}

bool OID::equals(OID other_oid) {
  return (netsnmp_oid_equals(get_ptr(), get_len(),
                             other_oid.get_ptr(), other_oid.get_len()) == 0);
}

bool OID::subtree_contains(OID other_oid) {
  return (snmp_oidtree_compare(get_ptr(), get_len(),
                             other_oid.get_ptr(), other_oid.get_len()) == 0);
}

void OID::print_state() const {
  std::cout << "oids_ contains:";
  for (std::vector<oid>::const_iterator it = oids_.begin() ; it != oids_.end(); ++it)
  {
    std::cout << ' ' << *it;
  };
  std::cout << '\n';
}

void OID::append(std::string more)
{
  std::vector<std::string> result;
  boost::split(result, more, boost::is_any_of("."));
  for (std::vector<std::string>::iterator it = result.begin() ; it != result.end(); ++it) {
    oids_.push_back(atoi(it->c_str()));
  }
}

