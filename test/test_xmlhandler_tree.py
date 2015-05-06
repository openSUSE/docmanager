#!/usr/bin/python3

from docmanager.xmlhandler import XmlHandler

NS = {
        "d":"http://docbook.org/ns/docbook",
        "dm":"urn:x-suse:ns:docmanager"
     }

def test_XmlHandler_tree(tmp_valid_xml):
    """Checks tree property of XmlHandler class

    :param py.path.local tmp_valid_xml: Fixture, pointing to a temporary XML file
    """
    xml = XmlHandler(tmp_valid_xml.strpath)
    assert xml, "No XmlHandler could be instantiated"
    assert xml.tree