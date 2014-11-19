ENV_DIR := ${shell pwd}/_env
PYTHON_BIN := /usr/bin/python2.7

# The build has been seen to fail on Mac OSX when trying to build on i386. Enable this to build for x86_64 only
X86_64_ONLY=0

.DEFAULT_GOAL = build

.PHONY: build
build: bin/buildout buildout.cfg
ifeq (${X86_64_ONLY},1)
	ARCHFLAGS="-arch x86_64" ./bin/buildout -N
else
	ARCHFLAGS="-arch i386 -arch x86_64" ./bin/buildout -N
endif

bin/buildout: ${ENV_DIR}/bin/python
	mkdir -p .buildout_downloads/dist
	${ENV_DIR}/bin/easy_install "setuptools>0.7"
	${ENV_DIR}/bin/easy_install distribute
	${ENV_DIR}/bin/easy_install zc.buildout
	mkdir -p bin/
	ln -s ${ENV_DIR}/bin/buildout bin/

${ENV_DIR}/bin/python:
	virtualenv --no-site-packages --setuptools --python=${PYTHON_BIN} ${ENV_DIR}

.PHONY: clean
clean: 
	rm -rf bin eggs develop-eggs parts .installed.cfg .buildout_downloads
	rm -rf ${ENV_DIR}

