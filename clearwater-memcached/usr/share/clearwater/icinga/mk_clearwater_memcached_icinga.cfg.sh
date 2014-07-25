. /etc/clearwater/config
cat << EOF
define command{
        command_name    restart-memcached
        command_line    /usr/lib/nagios/plugins/clearwater-abort \$SERVICESTATE$ \$SERVICESTATETYPE$ \$SERVICEATTEMPT$ /var/run/memcached.pid 30
        }


define service{
        use                             cw-service         ; Name of service template to use
        host_name                       local_ip
        service_description             Memcached port open
        check_command                   check_tcp_port!11211
        event_handler                   restart-memcached
        }

EOF
