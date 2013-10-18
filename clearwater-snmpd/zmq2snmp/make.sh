# TODO: replace with actual Makefile

g++ `net-snmp-config --cflags` -Wall -std=c++0x -g -O0 -fPIC -shared -o bono_handler.so custom_handler.cpp oid.cpp oidtree.cpp bonodata.cpp zmq_listener.cpp zmq_message_handler.cpp `net-snmp-config --libs` -lzmq -lpthread
g++ `net-snmp-config --cflags` -Wall -std=c++0x -g -O0 -fPIC -shared -o sprout_handler.so custom_handler.cpp oid.cpp oidtree.cpp sproutdata.cpp zmq_listener.cpp zmq_message_handler.cpp `net-snmp-config --libs` -lzmq -lpthread
