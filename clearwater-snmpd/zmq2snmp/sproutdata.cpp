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

#include "nodedata.hpp"
#include "custom_handler.hpp"

NodeData::NodeData() {
  name = "sprout_handler";
  port = "6666";
  root_oid = OID("1.2.826.0.1.1578918.9.3");
  stats = {"latency_us",
           "hss_latency_us",
           "hss_digest_latency_us",
           "hss_subscription_latency_us",
           "xdm_latency_us",
           "connected_homers",
           "connected_homesteads"};
  stat_to_type = {{"latency_us", STAT_LATENCY},
                  {"hss_latency_us", STAT_LATENCY},
                  {"hss_digest_latency_us", STAT_LATENCY},
                  {"hss_subscription_latency_us", STAT_LATENCY},
                  {"xdm_latency_us", STAT_LATENCY},
                  {"connected_homers", STAT_PER_IP_COUNT},
                  {"connected_homesteads", STAT_PER_IP_COUNT}};
  stat_to_root_oid = {{"latency_us", OID("1.2.826.0.1.1578918.9.3.1")},
                      {"hss_latency_us", OID("1.2.826.0.1.1578918.9.3.3.2")},
                      {"hss_digest_latency_us", OID("1.2.826.0.1.1578918.9.3.3.3")},
                      {"hss_subscription_latency_us", OID("1.2.826.0.1.1578918.9.3.3.4")},
                      {"xdm_latency_us", OID("1.2.826.0.1.1578918.9.3.2.2")},
                      {"connected_homers", OID("1.2.826.0.1.1578918.9.3.3.1")},
                      {"connected_homesteads", OID("1.2.826.0.1.1578918.9.3.2.1")}};
};

NodeData node_data;

extern "C" {
  // SNMPd looks for an init_<module_name> function in this library
  void init_sprout_handler() {
    initialize_handler();
  }
}
