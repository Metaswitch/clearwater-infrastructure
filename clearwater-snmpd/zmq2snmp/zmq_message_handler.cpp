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

#include "zmq_message_handler.hpp"
#include "nodedata.hpp"
#include "globals.hpp"
#include <cstdlib>

void ZMQMessageHandler::handle(std::vector<std::string> msgs) {
  if ((msgs.size() > 2) && (msgs[1].compare("OK") == 0)) {
    StatType type = node_data.stat_to_type[msgs[0]];
    OIDMap returnmap;
    switch (type) {
      case STAT_PER_IP_COUNT:
        returnmap = handle_ip_count_stats(msgs);
        break;
      case STAT_LATENCY:
        returnmap = handle_latency_stats(msgs);
        break;
      case STAT_SINGLE_NUMBER:
        returnmap = handle_single_number_stat(msgs);
        break;
      case STAT_UNKNOWN:
      default:
        fprintf(stderr, "Statistic %s is unknown\n", msgs[0].c_str());
    }
    OID this_oid = node_data.stat_to_root_oid[msgs[0]];
    tree.replace_subtree(this_oid, returnmap);
  }
}

OIDMap ZMQMessageHandler::handle_ip_count_stats(std::vector<std::string> msgs) {
  // Messages are in [ip_address, count, ip_address, count] pairs
  OIDMap returnmap;
  for (std::vector<std::string>::iterator it = (msgs.begin() + 2);
       it != msgs.end();
       it++) {
    OID this_oid = node_data.stat_to_root_oid[msgs[0]];
    std::string ip_address = *it;
    int connections_to_this_ip = atoi((++it)->c_str());
    this_oid.append(ip_address);

    returnmap[this_oid] = connections_to_this_ip;
  }
  return returnmap;
}

OIDMap ZMQMessageHandler::handle_single_number_stat(std::vector<std::string> msgs) {
  OIDMap returnmap;
  OID this_oid = node_data.stat_to_root_oid[msgs[0]];
  this_oid.append("0"); // Indicates a scalar value in SNMP
  returnmap[this_oid] = atoi(msgs[2].c_str());
  return returnmap;
}

OIDMap ZMQMessageHandler::handle_latency_stats(std::vector<std::string> msgs) {
  OIDMap returnmap;
  OID root_oid = node_data.stat_to_root_oid[msgs[0]];
  OID average_oid = root_oid;
  average_oid.append("1");
  OID variance_oid = root_oid;
  variance_oid.append("2");
  OID lwm_oid = root_oid;
  lwm_oid.append("3");
  OID hwm_oid = root_oid;
  hwm_oid.append("4");
  returnmap[average_oid] = atoi(msgs[2].c_str());
  returnmap[variance_oid] = atoi(msgs[3].c_str());
  returnmap[lwm_oid] = atoi(msgs[4].c_str());
  returnmap[hwm_oid] = atoi(msgs[5].c_str());
  return returnmap;
}
