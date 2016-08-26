#!/usr/bin/python3
'''SNMP tools classes to be used as an alternative to the PySNMP library'''
import logging
import os
import subprocess


logger = logging.getLogger(__name__)


class SNMP(object):
    def __init__(self, community, host):
        self.community = community
        self.host = host

    def get(self, oid):
        raise NotImplementedError("An abstract method was called.")


class SubProcessSNMP(SNMP):
    def get(self, oid):
        logger.debug('performing snmpget operation on: %s', oid)
        with open(os.devnull, 'w') as FNULL:
            rtn_string = subprocess.check_output('snmpget -v2c -c ' + ' '.join([self.community, self.host, oid]), stderr=FNULL, shell=True).decode('UTF-8')
        logger.debug('splitting returned information: %s', rtn_string)
        rtn_value = rtn_string.split(': ')[1]
        rtn_value = rtn_value.strip()
        if rtn_value.isnumeric():
            rtn_value = float(rtn_value)
        return rtn_value
