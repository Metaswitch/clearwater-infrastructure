.PHONY: all
all: clearwater_socket_factory test_client_mgmt test_client_sig

clearwater_socket_factory: clearwater_socket_factory.cpp
	g++ -o clearwater_socket_factory clearwater_socket_factory.cpp

test_client_mgmt: test_client.cpp
	g++ -o $@ $^

test_client_sig: test_client.cpp
	g++ -DSOCKET_PATH=\"/tmp/clearwater_signaling_namespace_socket\" -o $@ $^

.PHONY: clean
clean:
	rm -f clearwater_socket_factory test_client_sig test_client_mgmt
