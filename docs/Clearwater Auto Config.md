Clearwater Auto Configuration
=============================

This document briefly describes how the Clearwater automatic configuration
process works. This function is used when deploying an All-In-One node using 
[Chef](http://clearwater.readthedocs.org/en/latest/Creating_a_deployment_with_Chef/index.html#creating-an-all-in-one-aio-node), 
a deployment using [Docker](https://github.com/Metaswitch/clearwater-docker/blob/master/README.md), 
and building an [OVF](http://clearwater.readthedocs.org/en/latest/All_in_one_OVF_Installation/index.html)

Also, AIO nodes can be saved as [Amazon AMIs](http://clearwater.readthedocs.org/en/latest/All_in_one_EC2_AMI_Installation/index.html), 
from which new systems can be launched. Such newly launched instances behave 
much as if the original system (the one that was saved as an AMI) had been 
rebooted, but coming back up with different local and public IP addresses, 
and a new domain.

The basic process is as follows.

-   Early in the boot cycle, the `clearwater-auto-config-<aws|docker|generic>`
    package is installed. 
-   On startup, this creates/updates the configuration files `/etc/clearwater`
    with the correct IP addresses and domain name. On AWS, it does this by
    querying AWS via 169.254.169.254 (a magic IP address that returns information 
    about EC2 instances); for the other systems the init.d scripts just call
    `hostname`. 
-   Subsequently, `/etc/init.d/clearwater-infrastructure` runs.  This propogates 
    the configuration now in `/etc/clearwater/` such that the various Clearwater 
    components will pick them up when they get started.
