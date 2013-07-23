Clearwater Auto Configuration
=============================

This document briefly describes how the Clearwater automatic configuration
process works.  This function is used when building an all-in-one ("AIO") node
using chef.

Also, AIO nodes can be saved as Amazon AMIs, from which new systems can be
launched. Such newly launched instances behave much as if the original system
(the one that was saved as an AMI) had been rebooted, but coming back up with
different local & public IP addresses, and a new domain.

The basic process is as follows.

-   Early in the boot cycle, `/etc/init.d/clearwater-auto-config` is
    run.
-   This updates a file called `/etc/clearwater/config` with the new IP
    addresses and domain name.  It does this by quering AWS via
    169.254.169.254 (a magic IP address that returns information about EC2
    instances).
-   Subsequently, `/etc/init.d/clearwater-infrastructure` runs.  This updates
    any of the Clearwater Debian packages that have new versions available,
    and propogates the values now in `/etc/clearwater/config` such that the
    various Clearwater components will pick them up when they get started.

Components should not query AWS's 169.254.169.254 IP address directly.
In future, we might support other cloud providers with other ways of
retrieving this information. The aim is to be able to replace
`aws_config.sh` with a different cloud provider's script and everything
else be unaffected.

Development
===========

The files in this repository can be compiled into a Debian package by the
'make deb' command.
