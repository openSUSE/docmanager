#!/usr/bin/python3

import pytest
import shlex

from docmanager import parsecli
from docmanager.action import Actions
from docmanager.core import DefaultDocManagerProperties, NS
from docmanager.xmlhandler import XmlHandler
from docmanager.xmlutil import localname


#@pytest.mark.skipif(compare_pytest_version((2,6,4)),
#                    reason="Need 2.6.4 to execute this test")
def __test_docmanager_delcheck(capsys, tmp_valid_xml):
    """This test checks, if we can delete a property in an xml file"""
    expected="world"
    clicmd = shlex.split("set -p hello={} {}".format(expected, tmp_valid_xml))
    a = Actions(parsecli(clicmd))
    out, err = capsys.readouterr()
    
    clicmd = shlex.split("get -p hello {}".format(tmp_valid_xml))
    a = Actions(parsecli(clicmd))
    out, err = capsys.readouterr()
    
    assert out[:-1] == expected, "Expected \"get\" output is not \"world\". What I got: \"{}\"".format(out[:-1])
    
    clicmd = shlex.split("del -p {} {}".format(expected, tmp_valid_xml))
    a = Actions(parsecli(clicmd))
    out, err = capsys.readouterr()
    
    clicmd = shlex.split("get -p {} {}".format(expected, tmp_valid_xml))
    a = Actions(parsecli(clicmd))
    out, err = capsys.readouterr()
    
    assert out[:-1] == "", "Expected empty output but got: {}".format(out[:-1])


def test_docmanager_delcheck2(tmp_valid_xml):
    handler = XmlHandler(tmp_valid_xml.strpath)
    handler.init_default_props(False)
    dm = handler.tree.find("//dm:docmanager", namespaces=NS)
    dmset = set(localname(e.tag) for e in list(dm.iterchildren()) )
    assert dmset == set(DefaultDocManagerProperties)
