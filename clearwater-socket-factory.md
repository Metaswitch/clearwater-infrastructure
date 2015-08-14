# Clearwater Socket Factory

The `clearwater-socket-factory` is a service that runs as root in the system's default network namespace. It allows processes running in any namespace to establish TCP connections from any other namespace.

For example, when traffic separation is enabled on a Clearwater node the default namespace is used for management traffic. This service is used by processes in the signalling namespace (such as Sprout) to obtain connections to the Metaswitch Service Assurance Server (which lives in the management network).

For security reasons, the socket factory is only allowed to connect to a restricted set of hosts in each namespace. This is to prevent an unprivileged process (such as Sprout) from requesting connections to arbitrary hosts in other namespaces.

## Interface

`clearwater-socket-factory` runs as a daemon process. Clients communicate with it over named UNIX sockets. There is a different named UNIX socket for each of the namespaces a process might try to connect into. Currently these are just management and signaling.

To request a new TCP connection from the factory a client should do the following:

* Create a new UNIX socket and connect to `/tmp/clearwater_mgmt_namespace_socket` or `/tmp/clearwater_signaling_namespace_socket`.
* Create a target string of the form `<host>:<port>` and send this in the UNIX socket using `send`.  `<host>` may be an IPv4 address, or a hostname that resolves to one or more IPv4 addresses.
* The daemon will now establish a TCP connection to the specified target and sends a message over the UNIX socket containing the TCP socket in the control data.
* The client receives this message and iterates though the control headers on the message until it finds one containing a socket (where the level is `SOL_SOCKET` and the type is `SCM_RIGHTS`).
* The client can treat the received socket as it would any normal connected TCP socket.

See the [example client](clearwater-socket-factory/test_client.cpp) for more details.

### Error Conditions

If the daemon is asked to connect to a host other than the configured "allowed hosts" it assumes that the allowed host must have changed. It exits immediately so that it can be restarted and pick up the new value.

If the daemon encounters any other errors it will indicate this to the client by either:

* Closing the connection to client.
* Sending the client a message containing an invalid (negative) file descriptor.

### Configuration

`clearwater-socket-factory` has 3 configuration options:

* signaling-namespace - this is the name of the signaling namespace.
* management-allowed-hosts - this is a comma separated lists of hosts in the management network that clearwater-socket-factory is allowed to provide sockets for.
* signaling-allowed-hosts - this is a comma separated lists of hosts in the signaling network that clearwater-socket-factory is allowed to provide sockets for.

`clearwater-socket-factory` has an upstart script which is built into its Debian package. When deployed with this upstart script, the process will continually respawn when it exits. The upstart script reads signaling_namespace in /etc/clearwater/config to use as the signaling-namespace option, and it builds up lists of allowed hosts by reading each line of each file in /etc/clearwater-socket-factory/signaling.d and /etc/clearwater-socket-factory/management.d to use as the signaling-allowed-hosts and management-allowed-hosts options. If these directories don't exist, or are empty, the whitelist is empty.

## Limitations

* TCP is the only transport protocol supported.
* IPv6 is not supported. The factory will fail requests to connect to an IPv6 address, and all DNS lookups from within the factory return IPv4 addresses only.

