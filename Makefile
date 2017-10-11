# Makefile for Clearwater infrastructure packages

# this should come first so make does the right thing by default
.PHONY: all
all: build

ROOT ?= ${PWD}
PYZMQ_DIR := ${PWD}/clearwater-infrastructure/PyZMQ
SRC_DIR := ${PWD}/src
CW_SOCK_FACT_DIR := ${PWD}/clearwater-socket-factory

SETUPTOOLS_VERSION=30

ENV_DIR := $(shell pwd)/_env
ENV_PYTHON := ${ENV_DIR}/bin/python
ENV_PIP := ${ENV_DIR}/bin/pip
PYTHON_BIN := $(shell which python)

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

.PHONY: build clean analysis test verify style
build: pyzmq_build clearwater_infrastructure_build clearwater_socket_factory_build cw_infrastructure

clean: pyzmq_clean clearwater_infrastructure_clean clearwater_socket_factory_clean cw_infrastructure_clean

analysis: clearwater_infrastructure_analysis cw_infrastructure_analysis

test: cw_infrastructure_test

verify: cw_infrastructure_verify

style: cw_infrastructure_style

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

ENV_DIR := $(shell pwd)/_env
BANDIT_EXCLUDE_LIST = _env,modules/,debian,clearwater-infrastructure/PyZMQ/_env,clearwater-infrastructure/PyZMQ/eggs

include build-infra/python.mk

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

.PHONY: cw_infrastructure cw_infrastructure_test cw_infrastructure_verify cw_infrastructure_style cw_infrastructure_clean cwc_management_analysis
cw_infrastructure:
		${MAKE} -C cw_infrastructure ${ENV_DIR}/.wheels-installed

cw_infrastructure_test:
		${MAKE} -C cw_infrastructure test

cw_infrastructure_verify:
		${MAKE} -C cw_infrastructure verify

cw_infrastructure_style:
		${MAKE} -C cw_infrastructure style

cw_infrastructure_clean:
		${MAKE} -C cw_infrastructure clean

cw_infrastructure_analysis:
		${MAKE} -C cw_infrastructure analysis
