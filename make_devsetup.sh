#!/bin/bash

#
# this make file sets up the test environment for DocManager
#

SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ENVFOLDER="$SCRIPTDIR/env"

if [ -d $ENVFOLDER ]; then
	echo "There is already an environment folder in the root folder of the project."
	exit 1
fi

cd $SCRIPTDIR
pyvenv env
source env/bin/activate
pip install --upgrade pip setuptools
pip install -r test_requirements.txt
python3 setup.py install
