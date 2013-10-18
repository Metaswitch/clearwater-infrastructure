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

#include <ctime>
#include <pthread.h>
#include <atomic>

#include "custom_handler.hpp"
#include "oid.hpp"
#include "oidtree.hpp"
#include "nodedata.hpp"
#include "zmq_listener.hpp"

OIDTree tree;
std::atomic_long last_seen_time;
const int TIMEOUT_THRESHOLD = 15;
static pthread_t zmq_thread;

void* start_stats (void* arg) {
  ZMQListener listener;
  return listener.listen_thread(arg);
}

/** Initialize the bonoLatencyTable table by defining its contents and how it's structured */
void
initialize_handler(void)
{
  netsnmp_handler_registration *my_handler;
  last_seen_time.store(time(NULL));
  static oid* root;
  snmp_clone_mem((void**)&root,
                 (void*)(node_data.root_oid.get_ptr()),
                 (sizeof(oid) * node_data.root_oid.get_len()));

    my_handler = netsnmp_create_handler_registration(node_data.name.c_str(),
                                                     clearwater_handler,
                                                     root,
                                                     node_data.root_oid.get_len(),
                                                     HANDLER_CAN_RONLY);


    if (!my_handler) {
        snmp_log(LOG_ERR, "malloc failed in initialize_table_bonoLatencyTable");
        return; /** Serious error. */
    }

    DEBUGMSGTL(("initialize_table_bonoLatencyTable",
                "Registering table bonoLatencyTable as a table iterator\n"));
    netsnmp_register_handler(my_handler);
    pthread_create(&zmq_thread, NULL, start_stats, NULL);

}

/** handles requests for the bonoLatencyTable table, if anything else needs to be done */
int
clearwater_handler(
    netsnmp_mib_handler               *handler,
    netsnmp_handler_registration      *reginfo,
    netsnmp_agent_request_info        *reqinfo,
    netsnmp_request_info              *requests) {

    netsnmp_request_info *request;
    netsnmp_variable_list *var;

    for(request = requests; request; request = request->next)
    {
      bool failed = ((long)time(NULL) - last_seen_time) > TIMEOUT_THRESHOLD;
      if (failed) {
        return SNMP_ERR_GENERR;
      }
      OID this_oid(requests->requestvb->name, requests->requestvb->name_length);
      int outval;
      unsigned int retval;
      OID outoid;

      var = request->requestvb;
      if (request->processed != 0)
        continue;

      switch(reqinfo->mode) {
      case MODE_GET:
        if (tree.get(this_oid, outval))
        {
          retval = outval;
          snmp_set_var_typed_value(var, ASN_UNSIGNED,
                                   (u_char*)&retval,
                                   sizeof(retval));

        }
        break;
      case MODE_GETNEXT:
        if (tree.get_next(this_oid, outoid, outval))
        {
          retval = outval;
          snmp_set_var_objid(var,
                             outoid.get_ptr(),
                             outoid.get_len());
          snmp_set_var_typed_value(var, ASN_UNSIGNED,
                                   (u_char*)&retval,
                                   sizeof(retval));

        }
        break;

      default:
        snmp_log(LOG_ERR, "problem encountered in bonoLatencyTable_handler: unsupported mode\n");
      }
    }

    return SNMP_ERR_NOERROR;
}
