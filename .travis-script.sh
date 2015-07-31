#!/bin/bash

function check_exitcode {
    if [ $1 -ne 0 ]; then
        exit $1
    fi
}

coverage run setup.py test
check_exitcode $?
python3 setup.py install
check_exitcode $?

git remote add upstream git://github.com/openSUSE/docmanager.git
check_exitcode $?
git fetch upstream test-data
check_exitcode $?
git checkout test-data
cd doc-sle
docmanager init *
check_exitcode $?
cd ../doc-sleha
docmanager init *
check_exitcode $?
cd ../doc-cloud
docmanager init *
check_exitcode $?

