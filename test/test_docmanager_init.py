#!/usr/bin/python3

import pytest
import shlex
from argparse import Namespace
from docmanager.action import Actions
from docmanager.cli import parsecli
from docmanager.core import DEFAULT_DM_PROPERTIES
from docmanager.xmlhandler import XmlHandler

def test_docmanager_init_0(tmp_valid_xml):
    """ Test the init sub command without force """

    tmpfile = tmp_valid_xml.strpath
    
    clicmd = 'init {}'.format(tmpfile)
    a = Actions(parsecli(shlex.split(clicmd)))
    a.parse()

    handler = XmlHandler(tmpfile)
    for i in DEFAULT_DM_PROPERTIES:
        assert handler.is_prop_set(i) == True, "property {} is not set.".format(i)

@pytest.mark.parametrize("option,value", [
    ('maintainer', 'SUSE'),
    ('status', 'editing'),
    ('deadline', '2015-05-11'),
    ('priority', '2'),
    ('translation', 'no'),
    ('languages', 'en,de'),
    ('release', 'SLES'),
    ('release', 'SUSE Linux Enterprise Server 12'),
#    ('repository', 'https://github.com/openSUSE/docmanager'),
    ('bugtracker/url', 'https://github.com')
])
def test_docmanager_init_1(tmp_valid_xml, option, value):
    """ Test the init sub command with pre defined values """

    tmpfile = tmp_valid_xml.strpath

    ropt = option.replace("/", "-");

    clicmd = "init --{} \"{}\" {}".format(ropt, value, tmpfile)
    a = Actions(parsecli(shlex.split(clicmd)))
    a.parse()

    handler = XmlHandler(tmpfile)

    ret = handler.get(option)
    assert ret[option] == value, "The file was initialized without the pre defined value for the option '{}'.".format(option)
