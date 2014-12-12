.PHONY: all
all: clearwater_socket_factory test_client

clearwater_socket_factory: clearwater_socket_factory.c
	gcc -o clearwater_socket_factory clearwater_socket_factory.c

test_client: test_client.c
	gcc -o test_client test_client.c

.PHONY: clean
clean:
	rm -f clearwater_socket_factory test_client
