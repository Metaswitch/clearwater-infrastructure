# Clearwater Socket Factory

The `clearwater-socket-factory` is a service that runs in the system's default network namespace. It allows processes running in a different namespace to establish TCP connections from the default namespace.

When traffic separation is enabled on a Clearwater node the default namespace is used for management traffic. This service is used by processes in the signalling namespace (such as Sprout) to obtain connections to the Metaswitch Service Assurance Server (which lives in the management network).

For security reasons, the socket factory is only allowed to connect to a restricted set of hosts (currently only one is supported). This is to prevent an unprivileged process (such as Sprout) from requesting connections to arbitrary hosts in the default namespace.

## Interface

`clearwater-socket-factory` runs as a daemon process. Clients communicate with it over a named UNIX socket.

To request a new TCP connection from the factory a client should do the following:

* Create a new UNIX socket and connect to `/tmp/clearwater_mgmt_namespace_socket`.
* Create a target string of the form `<host>:<port>` and send this in the UNIX socket using `send`.  `<host>` may be an IPv4 address, or a hostname that resolves to one or more IPv4 addresses.
* The daemon will now establish a TCP connection to the specified target and sends a message over the UNIX socket containing the TCP socket in the control data.
* The client receives this message and iterates though the control headers on the message until it finds one containing a socket (where the level is `SOL_SOCKET` and the type is `SCM_RIGHTS`).
* The client can treat the received socket as it would any normal connected TCP socket.

See the [example client](clearwater-socket-factory/test_client.c) for more details.

### Error Conditions

If the daemon is asked to connect to a host other than the configured "allowed host" it assumes that the allowed host must have changed. It exits immediately so that it can be restarted and pick up the new value.

If the daemon encounters any other errors it will indicate this to the client by either:

* Closing the connection to client.
* Sending the client a message containing an invalid (negative) file descriptor.

## Limitations

* TCP is the only transport protocol supported.
* IPv6 is not supported. The factory will fail requests to connect to an IPv6 address, and all DNS lookups from within the factory return IPv4 addresses only.

