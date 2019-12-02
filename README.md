Project Clearwater is backed by Metaswitch Networks.  We have discontinued active support for this project as of 1st December 2019.  The mailing list archive is available in GitHub.  All of the documentation and source code remains available for the community in GitHub.  Metaswitch’s Clearwater Core product, built on Project Clearwater, remains an active and successful commercial offering.  Please contact clearwater@metaswitch.com for more information.

Clearwater Infrastructure
=========================

Overview
--------

Clearwater Infrastructure is the infrastructure package for
Clearwater. It manages automatic configuration and upgrade, and
installs a number of dependencies.

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

* clearwater-radius-auth: RADIUS authentication package. More details are [here](http://clearwater.readthedocs.io/en/latest/Radius_Authentication.html).
