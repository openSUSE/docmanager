#!/usr/bin/python3

from docmanager.xmlhandler import XmlHandler

def test_XmlHandler_is_set(tmp_valid_xml):
    """Checks XmlHandler.is_set method

    :param py.path.local tmp_valid_xml: Fixture, pointing to a temporary XML file
    """
    xml = XmlHandler(tmp_valid_xml.strpath)
    assert xml, "No XmlHandler could be instantiated"
    assert not xml.is_set("foo", "nix"), "Tag 'foo' shouldn't be here"