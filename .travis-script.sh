#!/bin/bash
#
# Execute this script after tox or py.test has been finished.

function check_exitcode {
    if [[ $1 -ne 0 ]]; then
        exit $1
    fi
}

function travisfoldstart {
 if [[ $TRAVIS != '' ]]; then
     echo "travis_fold:start:$1"
 fi
}

function travisfoldend {
  if [[ $TRAVIS != '' ]]; then
      echo "travis_fold:end:$1"
  fi
}


travisfoldstart setup.py_install
echo "--- Executing setup.py install ---"
./setup.py install
mkdir -p ~/.config/docmanager/
cp -vi src/docmanager/docmanager.conf ~/.config/docmanager/
check_exitcode $?
travisfoldend setup.py_install

# travisfoldend install

# itravisfoldstart git
git remote add upstream git://github.com/openSUSE/docmanager.git
check_exitcode $?
# travisfoldend git

travisfoldstart git.test_data
echo "--- Fetching test-data... ---"
git fetch upstream test-data
check_exitcode $?
git checkout test-data
travisfoldend git.test_data

travisfoldstart doc_sle
echo "--- Doc SLE ---"
cd doc-sle
docmanager init *.xml
check_exitcode $?
travisfoldend doc_sle

travisfoldstart doc_sleha
echo "--- Doc SLEHA ---"
cd ../doc-sleha
docmanager init *.xml
check_exitcode $?
travisfoldend doc_sleha

travisfoldstart doc_cloud
echo "--- Doc Cloud ---"
cd ../doc-cloud
docmanager init *.xml
check_exitcode $?
travisfoldend doc_cloud
