# Makefile for Clearwater infrastructure packages

# this should come first so make does the right thing by default
.PHONY: all
all: build

ROOT ?= ${PWD}
PYZMQ_DIR := ${PWD}/clearwater-infrastructure/PyZMQ
SRC_DIR := ${PWD}/src
CW_SOCK_FACT_DIR := ${PWD}/clearwater-socket-factory

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

.PHONY: build
build: pyzmq_build clearwater_infrastructure_build clearwater_socket_factory_build wheelhouse

.PHONY: clean
clean: pyzmq_clean clearwater_infrastructure_clean clearwater_socket_factory_clean
	-rm -r .wheelhouse ${ENV_DIR} build

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

include build-infra/cw-deb.mk
.PHONY: deb
deb: build deb-only

include build-infra/cw-rpm.mk
.PHONY: rpm
rpm: build rpm-only

verify: ${ENV_DIR_PY}/bin/flake8
	${ENV_DIR}/bin/flake8 --select=E10,E11,E9,F cw_infrastructure

style: ${ENV_DIR_PY}/bin/flake8
	${ENV_DIR}/bin/flake8 --select=E,W,C,N --max-line-length=100 cw_infrastructure

.PHONY: wheelhouse
wheelhouse: .wheelhouse/.sentinel

.wheelhouse/.sentinel: ${ENV_PYTHON} ${ENV_PIP} cw_infrastructure/setup.py $(wildcard cw_infrastructure/cw_infrastructure/*.py)
	${ENV_DIR}/bin/pip wheel -w .wheelhouse cw_infrastructure/
	@touch $@

${ENV_DIR_PY}/bin/flake8: ${ENV_PIP}
	${ENV_DIR}/bin/pip install flake8

${ENV_PIP} ${ENV_PYTHON}:
	-rm -rf ${ENV_DIR}
	virtualenv --python=${PYTHON_BIN} ${ENV_DIR}
	${ENV_DIR}/bin/pip install pip wheel setuptools --upgrade
