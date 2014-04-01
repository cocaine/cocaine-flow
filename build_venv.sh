#!/bin/bash

PYPY_VERSION="2.2.1"

CURDIR=$(pwd)
ENV_DIR=${CURDIR}/flow_env
echo $ENV_DIR

if [ $(uname) == Darwin ]; then
    DIST=osx64
else
    DIST=linux64
fi
ARCHIVE="pypy-${PYPY_VERSION}-${DIST}.tar.bz2"

# Download PyPy distributin into tempdir
cd $TMPDIR
echo -n "Downloading PyPy...."
STATUS=$(curl -s -w "%{http_code}" -LO https://bitbucket.org/pypy/pypy/downloads/${ARCHIVE})
if [ $STATUS -ne 200 ]; then
    echo "ERROR"
    exit 1
else
    echo "OK"
fi

echo -n "Extracting PyPy..."
tar -xf $ARCHIVE
if [ $? -ne 0 ]; then
    echo "ERROR"
    exit 1
else
    echo "OK"
fi

PYPYEXEC=${TMPDIR}pypy-${PYPY_VERSION}-${DIST}/bin/pypy
if [ ! -x $PYPYEXEC ]; then
    echo "pypy is missing"
    exit 1
fi
cd $CURDIR

# Prepare virtual env
mkdir -p $ENV_DIR
cd $ENV_DIR
echo "Creating virtualenv"
virtualenv --no-site-packages -p $PYPYEXEC pypy-env

echo "Activate virtualenv"
source ${ENV_DIR}/pypy-env/bin/activate
