# Clearwater Socket Factory

The Clearwater Socket Factory` comprises two services, `clearwater-socket-factory-mgmt` and `clearwater-socket-factory-sig` that run as root in the management and signaling network namespaces respectively (both run in the default namespace if traffic separation is not enabled). They allow processes running in one namespace to establish TCP connections from the other namespace.

For example, when traffic separation is enabled on a Clearwater node the default namespace is used for management traffic. `clearwater-socket-factory-mgmt` is used by processes in the signalling namespace (such as Sprout) to obtain connections to the Metaswitch Service Assurance Server (which lives in the management network).

For security reasons, the socket factory is only allowed to connect to a restricted set of hosts in each namespace. This is to prevent an unprivileged process (such as Sprout) from requesting connections to arbitrary hosts in other namespaces.

## Interface

`clearwater-socket-factory-mgmt` and `clearwater-socket-factory-sig` run as daemon processes. Clients communicate with it over named UNIX sockets. There is a different named UNIX socket for each of the namespaces a process might try to connect into. Currently these are just management and signaling.

To request a new TCP connection from the factory a client should do the following:

* Create a new UNIX socket and connect to `/tmp/clearwater_management_namespace_socket` or `/tmp/clearwater_signaling_namespace_socket`.
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

`clearwater-socket-factory-mgmt` and `clearwater-socket-factory-sig` run a common executable `clearwater_socket_factory` (`clearwater-socket-factory-sig` runs its instance in the signaling namespace) which has 2 configuration options:

* `namespace` - either `signaling` or `management`.
* `allowed-hosts` - this is a comma separated lists of hosts in that network namespace that that instance of `clearwater_socket_factory` is allowed to provide sockets for.

`clearwater-socket-factory-mgmt` and `clearwater-socket-factory-sig` have upstart scripts which are constructed when the Debian package is installed. When deployed with these upstart script, the processes will continually respawn when they exit.

## Limitations

* TCP is the only transport protocol supported.
* IPv6 is not supported. The factory will fail requests to connect to an IPv6 address, and all DNS lookups from within the factory return IPv4 addresses only.

