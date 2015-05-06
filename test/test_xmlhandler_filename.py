#!/usr/bin/python3

from docmanager.xmlhandler import XmlHandler

def test_XmlHandler_filename(tmp_valid_xml):
    """Checks filename property XmlHandler class

    :param py.path.local tmp_valid_xml: Fixture, pointing to a temporary XML file
    """
    xml = XmlHandler(tmp_valid_xml.strpath)
    assert xml, "No XmlHandler could be instantiated"
    assert xml.filename == tmp_valid_xml.strpath