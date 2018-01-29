ROOT ?= $(abspath $(shell pwd)/../)
ENV_DIR ?= ${ROOT}/_env
PYTHON_BIN := python

SETUPTOOLS_VERSION=30
FLAKE8_INCLUDE_DIR = .

# This is first so that it sets the default target to build the wheels

all: wheelhouses

include ../build-infra/python.mk

cw_infrastructure_SETUP = setup.py
cw_infrastructure_REQUIREMENTS = requirements.txt requirements-test.txt
cw_infrastructure_TEST_SETUP = setup.py
cw_infrastructure_SOURCES = $(wildcard cw_infrastructure/*.py)
cw_infrastructure_WHEELHOUSE = ../.wheelhouse
cw_infrastructure_BUILD_DIRS=T
$(eval $(call python_component,cw_infrastructure))
