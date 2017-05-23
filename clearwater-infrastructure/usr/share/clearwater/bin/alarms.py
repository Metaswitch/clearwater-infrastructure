# @file alarms.py
#
# Copyright (C) Metaswitch Networks 2017
# If license terms are provided to you in a COPYING file in the root directory
# of the source code repository by which you are accessing this code, then
# the license outlined in that COPYING file applies to your use.
# Otherwise no rights are granted except for those provided to you by
# Metaswitch Networks in a separate written agreement.


# This module provides a method for transporting alarm requests to a net-
# snmp alarm sub-agent for further handling. If the agent is unavailable,
# the request will timeout after 2 seconds and be dropped.


import re
import zmq
import sys
import syslog
import os.path
from subprocess import call


def sendrequest(request):
  try:
    context = zmq.Context.instance()

    client = context.socket(zmq.REQ)
    client.connect("ipc:///var/run/clearwater/alarms")

    poller = zmq.Poller()
    poller.register(client, zmq.POLLIN)

    for reqelem in request[0:-1]:
      client.send(reqelem, zmq.SNDMORE)

    client.send(request[-1])

    socks = dict(poller.poll(2000))

    if client in socks:
      message = client.recv()
    else:
      syslog.syslog(syslog.LOG_ERR, "dropped request: '%s'" % " ".join(request))

    context.destroy(100)

  except Exception as e:
    syslog.syslog(syslog.LOG_ERR, str(e))

