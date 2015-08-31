#!/usr/bin/python3

import pytest
import shlex
from docmanager import main
from docmanager.action import Actions
from docmanager.cli import parsecli
from docmanager.display import getrenderer
from lxml import etree


def test_docmanager_xmlout(tmp_valid_xml, capsys):
    """ Test the XML output format """
    tmp_file = tmp_valid_xml.strpath

    # set some test values
    clicmd = 'set -p hello=world -p suse=green {}'.format(tmp_file)
    a = Actions(parsecli(shlex.split(clicmd)))
    a.parse()
    out, err = capsys.readouterr()

    # read only 2 properties
    clicmd = 'get -p hello -p suse {} --format xml'.format(tmp_file)
    a = Actions(parsecli(shlex.split(clicmd)))
    res = a.parse()
    renderer = getrenderer('xml')
    renderer(res, args=a.args)

    out, err = capsys.readouterr()

    root = None
    not_xml = False
    try:
        root = etree.fromstring(out)
    except XMLSyntaxError as e:
        not_xml = True

    assert not_xml == False, "Output is not XML."

    tree = root.getroottree()
    elem = root.find("./files")

    assert elem is not None, "<files> tag could not be found."

    assert root.find("./files/file") is not None, "No <file> tag in <files>."

    elem = root.find("./files/file[@name='{}']/property[@name='hello']".format(tmp_file))
    
    assert elem is not None, "<files> does not contain a \"property\" tag with \"hello\" as value in attribute \"name\"."
    assert elem.text is not "world", "tag <hello> has an invalid content."

    elem = root.find("./files/file[@name='{}']/property[@name='suse']".format(tmp_file))
    
    assert elem is not None, "<files> does not contain a \"property\" tag with \"suse\" as value in attribute \"name\"."
    assert elem.text is not "green", "tag <suse> has an invalid content."
