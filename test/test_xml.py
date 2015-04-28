#!/usr/bin/python3

import os.path
import sys
from io import StringIO
import pytest
import py.path
from lxml import etree

from docmanager.xmlhandler import XmlHandler

# os.path.relpath(os.path.abspath("test"))
testdir = py.path.local("test")

NS = {
        "d":"http://docbook.org/ns/docbook",
        "dm":"urn:x-suse:ns:docmanager"
     }

def test_XmlHandler_filename(xmltmpfile):
    """Checks filename property XmlHandler class

    :param py.path.local xmltmpfile: Fixture, pointing to a temporary XML file
    """
    xml = XmlHandler(xmltmpfile.strpath)
    assert xml, "No XmlHandler could be instantiated"
    assert xml.filename == xmltmpfile.strpath


def test_XmlHandler_tree(xmltmpfile):
    """Checks tree property of XmlHandler class

    :param py.path.local xmltmpfile: Fixture, pointing to a temporary XML file
    """
    xml = XmlHandler(xmltmpfile.strpath)
    assert xml, "No XmlHandler could be instantiated"
    assert xml.tree


def test_XmlHandler_docmanager(xmltmpfile):
    """Checks if docmanager element is available

    :param py.path.local xmltmpfile: Fixture, pointing to a temporary XML file
    """
    xml = XmlHandler(xmltmpfile.strpath)
    assert xml, "No XmlHandler could be instantiated"
    tree = xml.tree
    tree.find("//dm:docmanager", namespaces=NS)
    assert tree, "No docmanager element available"


def test_XmlHandler_set(xmltmpfile):
    """Checks if docmanager element is available

    :param py.path.local xmltmpfile: Fixture, pointing to a temporary XML file
    """
    xml = XmlHandler(xmltmpfile.strpath)
    assert xml, "No XmlHandler could be instantiated"
    xml.set("foo", "2")
    dm = xml.tree.find("//dm:docmanager", namespaces=NS)
    assert len(dm), "expected child elements in docmanager"

    # Let's test the written XML file
    tree = etree.parse(xmltmpfile.strpath)
    dm = tree.find("//dm:docmanager", namespaces=NS)
    assert len(dm), "expected child elements in docmanager"


def test_XmlHandler_is_set(xmltmpfile):
    """Checks XmlHandler.is_set method

    :param py.path.local xmltmpfile: Fixture, pointing to a temporary XML file
    """
    xml = XmlHandler(xmltmpfile.strpath)
    assert xml, "No XmlHandler could be instantiated"
    assert not xml.is_set("foo", "nix"), "Tag 'foo' shouldn't be here"
