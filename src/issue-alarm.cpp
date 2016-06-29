/**
 * @file issue-alarm.cpp
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

// This tool is used to issue an SNMP alarm.  It takes two parameters: the
// name of the alarm issuer and the alarm identifier.  For example:
//     issue-alarm "monit" "1000.3"
//
// Note the alarm identifier uses ituAlarmPerceivedSeverity. We can
// translate this to alarmModelState using the function AlarmTableDef::state.
// This mapping is described in RFC 3877 section 5.4
// https://tools.ietf.org/html/rfc3877#section-5.4

#include <stdio.h>
#include <string.h>
#include <string>
#include <zmq.h>
#include <syslog.h>

int main(int argc, char **argv)
{
  int rc = 1; // Assume failure
  void* ctx = NULL;
  void* sck = NULL;

  // Check that we have the right number of arguments.
  if (argc != 3)
  {
    fprintf(stderr, "Usage : issue-alarm <alarm issuer name> <alarm identifier>\n");
    syslog(LOG_ERR, "unexpected parameter count: %d", argc);

    // Return 0 (success) for backwards-compatibility.
    rc = 0;
    goto EXIT;
  }

  // Enter a block so that we can declare new variables and still goto EXIT to
  // clear up.
  {
    // Parse command-line arguments.
    char* alarm_issuer = argv[1];
    char* alarm_identifier = argv[2];
  
    // Create the context.
    ctx = zmq_ctx_new();
    if (ctx == NULL)
    {
      perror("zmq_ctx_new");
      syslog(LOG_ERR, "zmq_ctx_new: %m");
      goto EXIT;
    }
  
    // Create the socket.
    sck = zmq_socket(ctx, ZMQ_REQ);
    if (sck == NULL)
    {
      perror("zmq_socket");
      syslog(LOG_ERR, "zmq_socket: %m");
      goto EXIT;
    }
  
    // Configure no linger period so a graceful shutdown will be immediate. It
    // is OK for any pending messages to be dropped as a result of a shutdown.
    int linger = 0;
    if (zmq_setsockopt(sck, ZMQ_LINGER, &linger, sizeof(linger)) == -1)
    {
      perror("zmq_setsockopt(ZMQ_LINGER)");
      syslog(LOG_ERR, "zmq_setsockopt(ZMQ_LINGER): %m");
      goto EXIT;
    }
  
    // Set send and receive timeouts of 500ms.
    int sndtimeo = 500;
    if (zmq_setsockopt(sck, ZMQ_SNDTIMEO, &sndtimeo, sizeof(sndtimeo)) == -1)
    {
      perror("zmq_setsockopt(ZMQ_SNDTIMEO)");
      syslog(LOG_ERR, "zmq_setsockopt(ZMQ_SNDTIMEO): %m");
      goto EXIT;
    }
    int rcvtimeo = 500;
    if (zmq_setsockopt(sck, ZMQ_RCVTIMEO, &rcvtimeo, sizeof(rcvtimeo)) == -1)
    {
      perror("zmq_setsockopt(ZMQ_RCVTIMEO)");
      syslog(LOG_ERR, "zmq_setsockopt(ZMQ_RCVTIMEO): %m");
      goto EXIT;
    }
  
    // Connect to the alarm service.
    if (zmq_connect(sck, "ipc:///var/run/clearwater/alarms") != 0)
    {
      perror("zmq_connect");
      syslog(LOG_ERR, "zmq_connect: %m");
      goto EXIT;
    }
  
    // Send the issue alarm message.
    if ((zmq_send(sck, "issue-alarm", strlen("issue-alarm"), ZMQ_SNDMORE) == -1) ||
        (zmq_send(sck, alarm_issuer, strlen(alarm_issuer), ZMQ_SNDMORE) == -1) ||
        (zmq_send(sck, alarm_identifier, strlen(alarm_identifier), 0) == -1))
    {
      perror("zmq_send");
      syslog(LOG_ERR, "zmq_send: %m");
      goto EXIT;
    }
  
    // Receive a response.  No need to read it.
    zmq_msg_t msg;
    if (zmq_msg_init(&msg) != 0)
    {
      perror("zmq_msg_init");
      syslog(LOG_ERR, "zmq_msg_init: %m");
      goto EXIT;
    }
    if (zmq_msg_recv(&msg, sck, 0) == -1)
    {
      perror("zmq_msg_recv");
      syslog(LOG_ERR, "zmq_msg_recv: %m");
      goto EXIT;
    }
    zmq_msg_close(&msg);
  
    // Success!
    rc = 0;
  }

EXIT:

  // Close the socket.
  if ((sck != NULL) &&
      (zmq_close(sck) != 0))
  {
    perror("zmq_close");
    syslog(LOG_ERR, "zmq_close: %m");
  }
  sck = NULL;

  // Destroy the context.
  if ((ctx != NULL) &&
      (zmq_ctx_destroy(ctx) != 0))
  {
    perror("zmq_ctx_destroy");
    syslog(LOG_ERR, "zmq_ctx_destroy: %m");
  }
  ctx = NULL;

  return rc;
}
