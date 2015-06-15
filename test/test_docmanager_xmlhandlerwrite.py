#!/usr/bin/python3

import pytest
import shlex
from docmanager.action import Actions
from docmanager.cli import parsecli
from docmanager.core import DefaultDocManagerProperties
from docmanager.xmlhandler import XmlHandler

IDS =['set_with_one_prop', 'set_with_two_props', 'init']
COMMANDS = [
    ('set -p firstprop=123 {}', ['firstprop']),
    ('set -p firstprop=123 -p secondprop=123 {}', ['firstprop', 'secondprop']),
    ('init {}', DefaultDocManagerProperties)
]

@pytest.mark.parametrize("command,expected",
                         COMMANDS,
                         ids=IDS
                        )
def test_docmanager_xmlhandlerwrite(command,expected,tmp_valid_xml):
    """Check if the write() function of the XmlHandler will be called properly
    by the Actions class
    """

    testfile = tmp_valid_xml.strpath
    clicmd = command.format(testfile)
    a = Actions(parsecli(shlex.split(clicmd)))
    a.parse()

    content = ""

    with open(testfile, 'r') as f:
        content = f.read()
    
    for i in expected:
        assert i in content
