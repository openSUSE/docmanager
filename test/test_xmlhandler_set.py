#!/usr/bin/env python3

from docmanager.logmanager import log
from docmanager.xmlhandler import XmlHandler
from lxml import etree
from docmanager.core import NS


def test_XmlHandler_set(tmp_valid_xml):
    """Checks if docmanager element is available

    :param py.path.local tmp_valid_xml: Fixture, pointing to a temporary XML file
    """
    xml = XmlHandler(tmp_valid_xml.strpath)
    assert xml, "No XmlHandler could be instantiated"
    xml.set({"foo": "2"})
    xml.write()
    dm = xml.tree.find("//dm:docmanager", namespaces=NS)
    assert len(dm), "expected child elements in docmanager"

    # Let's test the written XML file
    tree = etree.parse(tmp_valid_xml.strpath)
    dm = tree.find("//dm:docmanager", namespaces=NS)
    assert len(dm), "expected child elements in docmanager"


def test_file_without_info(testdir, tmpdir):
    """Checks if XML file contains NO <info> element

    :param py.path.local testdir: Path to test directory
    :param tmpdir: temporary directory
    """
    base = "valid_xml_file_without_info.xml"
    xmlfile = testdir / base
    assert xmlfile.exists(), "temp XML file '%s' does not exist" % base
    xmlfile.copy(tmpdir)
    xmlfile = tmpdir / base
    xml = XmlHandler(xmlfile.strpath)
    root = xml.root
    assert root is not None
    i = xml.tree.find("//d:info", namespaces=NS)
    assert i is not None
