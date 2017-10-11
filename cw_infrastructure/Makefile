ROOT ?= $(abspath $(shell pwd)/../)
ENV_DIR ?= ${ROOT}/_env
PYTHON_BIN := python

SETUPTOOLS_VERSION=30

TEST_SETUP_PY = setup.py
FLAKE8_INCLUDE_DIR = .

# This is first so that it sets the default target to install the wheels

all: ${ENV_DIR}/.wheels-installed

include ../build-infra/python.mk

cw_infrastructure_SETUP = setup.py
cw_infrastructure_REQUIREMENTS = requirements.txt
cw_infrastructure_SOURCES = $(wildcard bin/* cwc_management/*.py)
cw_infrastructure_WHEELHOUSE = ../.wheelhouse
cw_infrastructure_BUILD_DIRS=T
$(eval $(call python_component,cw_infrastructure))
