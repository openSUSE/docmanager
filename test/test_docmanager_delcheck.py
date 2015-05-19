#!/usr/bin/python3

import pytest
from conftest import compare_pytest_version
from docmanager import main
import shlex

@pytest.mark.skipif(compare_pytest_version((2,6,4)),
                    reason="Need 2.6.4 to execute this test")
def test_docmanager_delcheck(capsys, tmp_valid_xml):
    """This test checks, if we can delete a property in an xml file"""
    
    clicmd = "set -p hello=world {}".format(tmp_valid_xml)
    a = main(shlex.split(clicmd))
    out, err = capsys.readouterr()
    
    clicmd = "get -p hello {}".format(tmp_valid_xml)
    a = main(shlex.split(clicmd))
    out, err = capsys.readouterr()
    out = out.strip().split("=")
    assert out[-1] == "world", \
       "Expected 'world' but got '{}'".format(out[:-1])
    
    clicmd = "del -p hello {}".format(tmp_valid_xml)
    a = main(shlex.split(clicmd))
    out, err = capsys.readouterr()
    
#    clicmd = "get -p hello {}".format(tmp_valid_xml)
#    a = main(shlex.split(clicmd))
#    out, err = capsys.readouterr()
#
#    assert out[:-1] == '', "Expected empty output but got: {!r}".format(out)