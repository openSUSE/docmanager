#!/usr/bin/python3

import pytest
import shlex

from docmanager.cli import parsecli
from docmanager.action import Actions
from docmanager.core import DefaultDocManagerProperties, NS
from docmanager.xmlhandler import XmlHandler
from docmanager.xmlutil import localname

def test_docmanager_delcheck(tmp_valid_xml):
    ustr = 'Uf4C56WL'
    handler = XmlHandler(tmp_valid_xml.strpath)
    handler.set({ustr: 'blub'})
    handler.delete(ustr)
    handler.write()

    with open(tmp_valid_xml.strpath, 'r') as f:
        content = f.read()
    
    assert ustr not in content, 'It seems that the content could not be deleted. Something seems to be wrong in the delete method of the XmlHandler.'

def test_docmanager_delcheck2(tmp_valid_xml):
    handler = XmlHandler(tmp_valid_xml.strpath)
    handler.init_default_props(False)
    dm = handler.tree.find("//dm:docmanager", namespaces=NS)
    dmset = set(localname(e.tag) for e in list(dm.iterchildren()) )
    assert dmset == set(DefaultDocManagerProperties)

def test_docmanager_delcheck3(tmp_valid_xml):
    ustr = 'ArnLTVMp'
    handler = XmlHandler(tmp_valid_xml.strpath)
    handler.set({'a/test/with/more/props/{}'.format(ustr): 'blub'})
    handler.delete('a/test/with/more/props/{}'.format(ustr))
    handler.write()

    with open(tmp_valid_xml.strpath, 'r') as f:
        content = f.read()
    
    assert ustr not in content, 'It seems that the content could not be deleted. Something seems to be wrong in the delete method of the XmlHandler.'
