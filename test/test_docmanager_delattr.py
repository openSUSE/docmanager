#!/usr/bin/python3

import shlex
from docmanager.cli import parsecli
from docmanager.action import Actions
from docmanager.xmlhandler import XmlHandler

# XmlHandler function check
def test_docmanager_delattr0(tmp_valid_xml):
    ustr = 'Uf4C56WL'
    handler = XmlHandler(tmp_valid_xml.strpath)
    handler.set({"myprop": None})
    handler.set_attr("myprop", {ustr: 'blub'})
    handler.write()

    with open(tmp_valid_xml.strpath, 'r') as f:
        content = f.read()
    
    assert ustr+"=\"blub\"" in content, 'Attribute {}=blub could not be created.'.format(ustr)

    handler.del_attr("myprop", [ustr])
    handler.write()

    content = None
    with open(tmp_valid_xml.strpath, 'r') as f:
        content = f.read()

    assert ustr+"=\"blub\"" not in content, 'Attribute {}=blub could not be deleted.'.format(ustr)

# call by cli interface
def test_docmanager_delattr1(tmp_valid_xml):
    ustr = "Uf4C56WL"

    handler = XmlHandler(tmp_valid_xml.strpath)
    handler.set({"myprop": None})
    handler.write()

    clicmd = "set-attr -p myprop -a {}=blub {}".format(ustr, tmp_valid_xml.strpath)
    a = Actions(parsecli(shlex.split(clicmd)))
    a.parse()

    with open(tmp_valid_xml.strpath, 'r') as f:
        content = f.read()
    
    assert ustr+"=\"blub\"" in content, 'Attribute {}=blub could not be created.'.format(ustr)

    clicmd = "del-attr -p myprop -a {} {}".format(ustr, tmp_valid_xml.strpath)
    a = Actions(parsecli(shlex.split(clicmd)))
    a.parse()

    with open(tmp_valid_xml.strpath, 'r') as f:
        content = f.read()
    
    assert ustr+"=\"blub\"" not in content, 'Attribute {}=blub could not be deleted.'.format(ustr)

# sub properties
def test_docmanager_delattr2(tmp_valid_xml):
    ustr = 'Uf4C56WL'
    handler = XmlHandler(tmp_valid_xml.strpath)
    handler.set({"a/b/c": None})
    handler.set_attr("a/b/c", {ustr: 'blub'})
    handler.write()

    with open(tmp_valid_xml.strpath, 'r') as f:
        content = f.read()
    
    assert "dm:c "+ustr+"=\"blub\"" in content, 'Attribute {}=blub could not be created.'.format(ustr)

    handler.del_attr("a/b/c", [ustr])
    handler.write()

    with open(tmp_valid_xml.strpath, 'r') as f:
        content = f.read()
    
    assert "dm:c "+ustr+"=\"blub\"" not in content, 'Attribute {}=blub could not be deleted.'.format(ustr)
