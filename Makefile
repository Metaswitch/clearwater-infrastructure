# Makefile for Clearwater infrastructure packages

# this should come first so make does the right thing by default
.PHONY: all
all: build

ROOT ?= ${PWD}
PYZMQ_DIR := ${PWD}/clearwater-infrastructure/PyZMQ
SRC_DIR := ${PWD}/src
CW_SOCK_FACT_DIR := ${PWD}/clearwater-socket-factory

PKG_COMPONENT := clearwater-infrastructure
PKG_MAJOR_VERSION ?= 1.0
PKG_NAMES := clearwater-infrastructure clearwater-memcached clearwater-secure-connections clearwater-tcp-scalability clearwater-snmpd clearwater-diags-monitor clearwater-auto-config-aws clearwater-auto-config-docker clearwater-auto-config-generic clearwater-log-cleanup clearwater-auto-upgrade clearwater-socket-factory clearwater-radius-auth vellum vellum-dbg dime dime-dbg
# Override the list of PKG_NAMES for RPM to exclude clearwater-memcached.
# We don't yet have a build of that.
RPM_NAMES := $(subst clearwater-memcached,,$(PKG_NAMES))

# Also exclude vellum and dime
RPM_NAMES := $(subst vellum-dbg,,$(RPM_NAMES))
RPM_NAMES := $(subst vellum,,$(RPM_NAMES))
RPM_NAMES := $(subst dime-dbg,,$(RPM_NAMES))
RPM_NAMES := $(subst dime,,$(RPM_NAMES))

.PHONY: build
build: pyzmq_build clearwater_infrastructure_build clearwater_socket_factory_build

.PHONY: clean
clean: pyzmq_clean clearwater_infrastructure_clean clearwater_socket_factory_clean

.PHONY: pyzmq_build
pyzmq_build:
	make -C ${PYZMQ_DIR}

.PHONY: pyzmq_clean
pyzmq_clean:
	make -C ${PYZMQ_DIR} clean

.PHONY: clearwater_infrastructure_build
clearwater_infrastructure_build:
	make -C ${SRC_DIR}

.PHONY: clearwater_infrastructure_clean
clearwater_infrastructure_clean:
	make -C ${SRC_DIR} clean

.PHONY: clearwater_socket_factory_build
clearwater_socket_factory_build:
	make -C ${CW_SOCK_FACT_DIR}

.PHONY: clearwater_socket_factory_clean
clearwater_socket_factory_clean:
	make -C ${CW_SOCK_FACT_DIR} clean

BANDIT_EXCLUDE_LIST = modules/,debian,clearwater-infrastructure/PyZMQ/_env,clearwater-infrastructure/PyZMQ/eggs
include build-infra/cw-deb.mk
include build-infra/python.mk
.PHONY: deb
deb: build deb-only

include build-infra/cw-rpm.mk
.PHONY: rpm
rpm: build rpm-only
