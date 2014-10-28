# Makefile for Clearwater infrastructure packages

# this should come first so make does the right thing by default
all: build 

PYZMQ_DIR := ${PWD}/clearwater-infrastructure/PyZMQ

DEB_COMPONENT := clearwater-infrastructure
DEB_MAJOR_VERSION := 1.0${DEB_VERSION_QUALIFIER}
DEB_NAMES := clearwater-infrastructure clearwater-memcached clearwater-memcached-extra clearwater-secure-connections clearwater-tcp-scalability clearwater-snmpd clearwater-diags-monitor clearwater-auto-config-aws clearwater-auto-config-generic clearwater-log-cleanup clearwater-auto-upgrade
DEB_ARCH := all

build:
	make -C ${PYZMQ_DIR}

clean:
	make -C ${PYZMQ_DIR} clean

include build-infra/cw-deb.mk

.PHONY: deb
deb: build deb-only

.PHONY: all build clean deb deb-only
