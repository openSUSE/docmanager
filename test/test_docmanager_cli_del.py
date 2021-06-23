#!/usr/bin/python3

import pytest
import shlex
from docmanager.action import Actions
from docmanager.cli import parsecli
from docmanager.core import DEFAULT_DM_PROPERTIES

def test_docmanager_cli_del_0(tmp_valid_xml):
    """Checks if the delete command works
    """

    ustr = "Ehufuveva271"
    xmlfile = tmp_valid_xml.strpath

    prepare_file(xmlfile, ustr)
    content = ""

    with open(xmlfile, 'r') as f:
        content = f.read()
    
    assert ustr in content

    clicmd = "del -p {} {}".format(ustr, xmlfile)
    a = Actions(parsecli(shlex.split(clicmd)))
    a.parse()

    content = ""

    with open(xmlfile, 'r') as f:
        content = f.read()
    
    assert ustr not in content

def test_docmanager_cli_del_1(tmp_valid_xml):
    """Checks if the delete command works with a condition (delete should not work here)
    """

    ustr = "Ehufuveva271"
    file = tmp_valid_xml.strpath

    prepare_file(file, ustr)
    content = ""

    with open(file, 'r') as f:
        content = f.read()
    
    assert ustr in content

    clicmd = "del -p {}=should_not_work {}".format(ustr, file)
    a = Actions(parsecli(shlex.split(clicmd)))
    a.parse()

    content = ""

    with open(file, 'r') as f:
        content = f.read()
    
    assert ustr in content

def test_docmanager_cli_del_2(tmp_valid_xml):
    """Checks if the delete command works with a condition (delete should work here)
    """

    ustr = "Ehufuveva271"
    file = tmp_valid_xml.strpath

    prepare_file(file, ustr)
    content = ""

    with open(file, 'r') as f:
        content = f.read()
    
    assert ustr in content

    clicmd = "del -p {}=bla {}".format(ustr, file)
    a = Actions(parsecli(shlex.split(clicmd)))
    a.parse()

    content = ""

    with open(file, 'r') as f:
        content = f.read()
    
    assert ustr not in content

def prepare_file(file, ustr):
    clicmd = "set -p {}=bla {}".format(ustr, file)
    a = Actions(parsecli(shlex.split(clicmd)))
    a.parse()
