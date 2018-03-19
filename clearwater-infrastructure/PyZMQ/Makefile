ENV_DIR := ${shell pwd}/_env
PYTHON_BIN := /usr/bin/python2.7

# The build has been seen to fail on Mac OSX when trying to build on i386. Enable this to build for x86_64 only
X86_64_ONLY=0

.DEFAULT_GOAL = build

.PHONY: build

PIP_VERSION := 9.0.1
BUILDOUT_VERSION := 2.11.0
SETUPTOOLS_VERSION := 38

MARKER_FILE := ${ENV_DIR}/.pip_${PIP_VERSION}_buildout_${BUILDOUT_VERSION}_setuptools_${SETUPTOOLS_VERSION}

build: ${MARKER_FILE} buildout.cfg
ifeq (${X86_64_ONLY},1)
	ARCHFLAGS="-arch x86_64" ${ENV_DIR}/bin/buildout -N
else
	ARCHFLAGS="-arch i386 -arch x86_64" ${ENV_DIR}/bin/buildout -N
endif

${MARKER_FILE}:
	rm -rf _env
	virtualenv --no-site-packages --python=${PYTHON_BIN} ${ENV_DIR}
	mkdir -p .buildout_downloads/dist
	${ENV_DIR}/bin/pip install --upgrade "pip==${PIP_VERSION}" "setuptools==${SETUPTOOLS_VERSION}"
	${ENV_DIR}/bin/pip install "zc.buildout==${BUILDOUT_VERSION}"
	touch $@

.PHONY: clean
clean:
	rm -rf bin eggs develop-eggs parts .installed.cfg .buildout_downloads
	rm -rf ${ENV_DIR}

