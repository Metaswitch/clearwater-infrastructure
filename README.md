Clearwater Infrastructure
=========================

Overview
--------

Clearwater Infrastructure is the infrastructure package for
Clearwater. It manages automatic configuration and upgrade, and
installs a number of dependencies.

Project Clearwater is an open-source IMS core, developed by [Metaswitch Networks](http://www.metaswitch.com) and released under the [GNU GPLv3](http://www.projectclearwater.org/download/license/). You can find more information about it on [our website](http://www.projectclearwater.org/) or [our wiki](https://github.com/Metaswitch/clearwater-docs/wiki).

Packages
--------

It contains the following packages:

* clearwater-infrastructure: common infrastructure for all Clearwater
  servers.

* clearwater-memcached: memcached configuration.

* clearwater-memcached-extra: redundant memcached configuration.

* clearwater-tcp-scalability: TCP scalability improvements.

* clearwater-secure-connections: secure connections between regions.

* clearwater-snmpd: SNMP service for CPU, RAM, and I/O statistics.

* clearwater-diags-monitor: optional service to monitor for crash dumps.

* clearwater-auto-config: optional service to create /etc/clearwater/config 
  automatically.  Used on all-in-one (AIO) nodes.

Further info
------------
* [Changelog](CHANGELOG.md)
