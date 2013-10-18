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

#include "zmq_listener.hpp"
#include "zmq_message_handler.hpp"
#include "nodedata.hpp"
#include "globals.hpp"
#include <string>
#include <vector>
#include <ctime>

ZMQListener::ZMQListener() {
  _message_handler = ZMQMessageHandler();
}

bool ZMQListener::connect_and_subscribe()
{
  // Create the context.
  _ctx = zmq_ctx_new();
  if (_ctx == NULL)
  {
    perror("zmq_ctx_new");
    return false;
  }

  // Create the socket and connect it to the host.
  _sck = zmq_socket(_ctx, ZMQ_SUB);
  if (_sck == NULL)
  {
    perror("zmq_socket");
    return false;
  }
  std::string ep = std::string("tcp://localhost:") + node_data.port;
  if (zmq_connect(_sck, ep.c_str()) != 0)
  {
    perror("zmq_connect");
    return false;
  }

  for (std::vector<std::string>::iterator it = node_data.stats.begin();
       it != node_data.stats.end();
       it++) {
    // Subscribe to the specified statistic.
    if (zmq_setsockopt(_sck, ZMQ_SUBSCRIBE, it->c_str(), strlen(it->c_str())) != 0)
    {
      perror("zmq_setsockopt");
      return false;
    }
  }

  return true;
}

// Thread to listen for ZMQ publishes for a given host/port/statistic
// name, then update the statistics structs with that information.
void* ZMQListener::listen_thread(void* args)
{
  if (!connect_and_subscribe()) {
    return NULL;
  };
  // Main loop of the thread - listen for ZMQ publish messages. Once a
  // whole block of data has been read, call the appropriate handler
  // function to populate data->struct_ptr with the stats received.
  while (1) {
    // Spin round until we've got all the messages in this block.
    int64_t more = 0;
    size_t more_sz = sizeof(more);
    std::vector<std::string> msgs;

    do
    {
      zmq_msg_t msg;
      if (zmq_msg_init(&msg) != 0)
      {
        perror("zmq_msg_init");
        return NULL;
      }
      if (zmq_msg_recv(&msg, _sck, 0) == -1)
      {
        perror("zmq_msg_recv");
        return NULL;
      }
      msgs.push_back(std::string((char*)zmq_msg_data(&msg), zmq_msg_size(&msg)));
      if (zmq_getsockopt(_sck, ZMQ_RCVMORE, &more, &more_sz) != 0)
      {
        perror("zmq_getsockopt");
        return NULL;
      }
      zmq_msg_close(&msg);
    }
    while (more);
    last_seen_time.store(time(NULL));
    _message_handler.handle(msgs);
    }
};

ZMQListener::~ZMQListener() {

  // Close the socket.
  if (zmq_close(_sck) != 0)
  {
    perror("zmq_close");
  }
  _sck = NULL;

  // Destroy the context.
  if (zmq_ctx_destroy(_ctx) != 0)
  {
    perror("zmq_ctx_destroy");
  }
  _ctx = NULL;
}
