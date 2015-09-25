Clearwater Infrastructure
=========================

Overview
--------

Clearwater Infrastructure is the infrastructure package for
Clearwater. It manages automatic configuration and upgrade, and
installs a number of dependencies.

Project Clearwater is an open-source IMS core, developed by [Metaswitch Networks](http://www.metaswitch.com) and released under the [GNU GPLv3](http://www.projectclearwater.org/download/license/). You can find more information about it on [our website](http://www.projectclearwater.org/) or [our wiki](http://clearwater.readthedocs.org/en/latest/).

Packages
--------

It contains the following packages:

* clearwater-infrastructure: common infrastructure for all Clearwater
  servers.

* clearwater-memcached: memcached configuration.

* clearwater-tcp-scalability: TCP scalability improvements.

* clearwater-secure-connections: secure connections between regions.

* clearwater-snmpd: SNMP service for CPU, RAM, and I/O statistics.

* clearwater-diags-monitor: service that monitors for crashes / exceptions / hangs and collects relevant diags.  More details are [here](clearwater-diags-monitor.md)

* clearwater-auto-config: optional service to create /etc/clearwater/config
  automatically.  Used on all-in-one (AIO) nodes.

* clearwater-socket-factory: service that allows other processes to obtain sockets from the factory's network namespace. More details are [here](clearwater-socket-factory.md)

Further info
------------
* [Changelog](CHANGELOG.md)
