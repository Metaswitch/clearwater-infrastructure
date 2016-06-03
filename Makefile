# Makefile for Clearwater infrastructure packages

# this should come first so make does the right thing by default
.PHONY: all
all: build

PYZMQ_DIR := ${PWD}/clearwater-infrastructure/PyZMQ
CW_SOCK_FACT_DIR := ${PWD}/clearwater-socket-factory

PKG_COMPONENT := clearwater-infrastructure
PKG_MAJOR_VERSION ?= 1.0
PKG_NAMES := clearwater-infrastructure clearwater-memcached clearwater-secure-connections clearwater-tcp-scalability clearwater-snmpd clearwater-diags-monitor clearwater-auto-config-aws clearwater-auto-config-docker clearwater-auto-config-generic clearwater-log-cleanup clearwater-auto-upgrade clearwater-socket-factory clearwater-radius-auth

.PHONY: build
build: pyzmq_build clearwater_socket_factory_build

.PHONY: clean
clean: pyzmq_clean clearwater_socket_factory_clean

.PHONY: pyzmq_build
pyzmq_build:
	make -C ${PYZMQ_DIR}

.PHONY: pyzmq_clean
pyzmq_clean:
	make -C ${PYZMQ_DIR} clean

.PHONY: clearwater_socket_factory_build
clearwater_socket_factory_build:
	make -C ${CW_SOCK_FACT_DIR}

.PHONY: clearwater_socket_factory_clean
clearwater_socket_factory_clean:
	make -C ${CW_SOCK_FACT_DIR} clean

include build-infra/cw-deb.mk
.PHONY: deb
deb: build deb-only

include build-infra/cw-rpm.mk
.PHONY: rpm
rpm: build rpm-only
