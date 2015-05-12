#!/usr/bin/python3

import pytest
from docmanager.action import Actions
from docmanager import parsecli

def test_docmanager_delcheck(capsys, tmp_valid_xml):
    """This test checks, if we can delete a property in an xml file"""
    
    clicmd = "set -p hello=world {}".format(tmp_valid_xml)
    a = Actions(parsecli(clicmd.split()))
    out, err = capsys.readouterr()
    
    clicmd = "get -p hello {}".format(tmp_valid_xml)
    a = Actions(parsecli(clicmd.split()))
    out, err = capsys.readouterr()
    
    assert out[:-1] == "world", "Expected \"get\" output is not \"world\". What I got: \"{}\"".format(out[:-1])
    
    clicmd = "del -p hello {}".format(tmp_valid_xml)
    a = Actions(parsecli(clicmd.split()))
    out, err = capsys.readouterr()
    
    clicmd = "get -p hello {}".format(tmp_valid_xml)
    a = Actions(parsecli(clicmd.split()))
    out, err = capsys.readouterr()
    
    assert out[:-1] == "", "Expected empty output but got: {}".format(out[:-1])