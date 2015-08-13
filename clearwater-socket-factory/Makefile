.PHONY: all
all: clearwater_socket_factory test_client

clearwater_socket_factory: clearwater_socket_factory.cpp
	g++ -o clearwater_socket_factory clearwater_socket_factory.cpp

test_client: test_client.c
	g++ -o test_client test_client.c

.PHONY: clean
clean:
	rm -f clearwater_socket_factory test_client
