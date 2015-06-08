Clearwater Configuration Infrastructure
=======================================

This document briefly describes how the Clearwater configuration
infrastructure works. This function is contained within the
clearwater-infrastructure package.

The basic process is as follows.

-   Before clearwater-infrastructure is installed, the node needs to have set 
    up the configuration files in `/etc/clearwater`. These are created in 
    different ways depending on the type of install: see the installation methods
    [page](http://clearwater.readthedocs.org/en/latest/Installation_Instructions/index.html)
    for more details. 
-   If the node is an All-In-One node, then it should install the 
    clearwater-auto-config-aws/generic/docker package before installing 
    clearwater-infrastructure. This will set up the configuration automatically 
    (more details [here](https://github.com/Metaswitch/clearwater-infrastructure/blob/master/docs/Clearwater%20Auto%20Config.md))
-   The clearwater-infrastructure install creates the file 
    `/etc/clearwater/config`, which contains the configuration from 
    `local_config`, `shared_config` and `user_settings`.
-   On startup, clearwater-infrastructure calls any scripts in
    `/usr/share/clearwater/infrastructure/scripts`. These scripts read the 
    configuration files in `/etc/clearwater` and updates the node. For 
    example, `/usr/share/clearwater/infrastructure/scripts/hostname` determines
    a sensible hostname for the node and updates `/etc/hostname` with it.

Development
===========

The files in this repository can be compiled into a Debian package by the
'make deb' command.
