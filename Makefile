# Makefile for Clearwater infrastructure packages

# this should come first so make does the right thing by default
all: deb

DEB_COMPONENT := clearwater-infrastructure
DEB_MAJOR_VERSION := 1.0${DEB_VERSION_QUALIFIER}
DEB_NAMES := clearwater-infrastructure clearwater-memcached clearwater-memcached-extra clearwater-secure-connections clearwater-tcp-scalability clearwater-snmpd clearwater-diags-monitor clearwater-auto-config-aws clearwater-auto-config-generic clearwater-log-cleanup clearwater-auto-upgrade clearwater-icinga
DEB_ARCH := all

include build-infra/cw-deb.mk

.PHONY: deb
deb: deb-only

.PHONY: all deb-only deb
