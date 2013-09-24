Clearwater Configuration Infrastructure
=======================================

This document briefly describes how the Clearwater configuration
infrastructure works. This function is contained within the
clearwater-infrastructure package.

The basic process is as follows.

-   Early in the boot cycle, `/etc/init.d/clearwater-infrastructure` is
    run.
-   This updates any Debian packages where "Project Clearwater Maintainers" are
    listed in the maintainer field.
-   This calls `/usr/share/clearwater/bin/aws_config.sh`, which queries
    AWS via 169.254.169.254 (a magic IP address that returns information
    about EC2 instances).
-   It then generates a file called `/etc/clearwater/config`.
-   `/etc/clearwater/config` can be sourced by other scripts to determine
    configuration options. These are as follows (not all are required):
    -   `local_ip` - internal IP address
    -   `public_ip` - external IP address
    -   `public_hostname` - external DNS name (not user-friendly)
    -   `home_domain` - home SIP domain name (configured from deployment
        descriptor)
    -   `sprout_hostname` - hostname of the sprout cluster, or
         single sprout node if applicable (configured from deployment
         descriptor)
    -   `hs_hostname` - hostname of the homestead cluster, or single
        homestead node if applicable (configured from deployment
        descriptor)
    -   `xdms_hostname` - hostname of the homer cluster, or single
        homer node if applicable (configured from deployment descriptor)
    -   `splunk_hostname` - hostname of the splunk instance (configured
        from deployment descriptor)
    -   `mmonit_ip` - internal IP of M/Monit server (configured from
        deployment descriptor)
    -   `smtp_smarthost` - SMTP smarthost to use for sending emails
    -   `smtp_username` - SMTP username to use for sending emails
    -   `smtp_password` - SMTP password to use for sending emails
    -   `email_recovery_sender` - sender email to use in emails we send
    -   &lt;any other environment variables defined by the deployment
        descriptor provided in the user data\>

-   Finally, `/etc/init.d/clearwater-infrastructure` calls any scripts in
    `/etc/clearwater/scripts`. These scripts read `/etc/clearwater/config`
    and update config files around the system. For example,
    `/etc/clearwater/scripts/hostname` determines a sensible hostname for
    the node and updates `/etc/hostname` with it.

Components should not query AWS's 169.254.169.254 IP address directly.
In future, we might support other cloud providers with other ways of
retrieving this information. The aim is to be able to replace
`aws_config.sh` with a different cloud provider's script and everything
else be unaffected.

Development
===========

The files in this repository can be compiled into a Debian package by the
'make deb' command.
