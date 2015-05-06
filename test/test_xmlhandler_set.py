#!/usr/bin/python3

from docmanager.xmlhandler import XmlHandler
from lxml import etree

NS = {
        "d":"http://docbook.org/ns/docbook",
        "dm":"urn:x-suse:ns:docmanager"
     }

def test_XmlHandler_set(tmp_valid_xml):
    """Checks if docmanager element is available

    :param py.path.local tmp_valid_xml: Fixture, pointing to a temporary XML file
    """
    xml = XmlHandler(tmp_valid_xml.strpath)
    assert xml, "No XmlHandler could be instantiated"
    xml.set("foo", "2")
    dm = xml.tree.find("//dm:docmanager", namespaces=NS)
    assert len(dm), "expected child elements in docmanager"

    # Let's test the written XML file
    tree = etree.parse(tmp_valid_xml.strpath)
    dm = tree.find("//dm:docmanager", namespaces=NS)
    assert len(dm), "expected child elements in docmanager"