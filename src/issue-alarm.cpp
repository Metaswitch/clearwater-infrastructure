/**
 * @file issue-alarm.cpp
 *
 * Copyright (C) Metaswitch Networks
 * If license terms are provided to you in a COPYING file in the root directory
 * of the source code repository by which you are accessing this code, then
 * the license outlined in that COPYING file applies to your use.
 * Otherwise no rights are granted except for those provided to you by
 * Metaswitch Networks in a separate written agreement.
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
  void* ctx = NULL;
  void* sck = NULL;

  // Check that we have the right number of arguments.
  if (argc != 3)
  {
    fprintf(stderr, "Usage : issue-alarm <alarm issuer name> <alarm identifier>\n");
    syslog(LOG_ERR, "unexpected parameter count: %d", argc);

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

  // We always return success. This is because we don't mandate that the alarms
  // agent is installed, and we don't want the monit uptime scripts to fail
  // when they can't issue alarms.
  return 0;
}
