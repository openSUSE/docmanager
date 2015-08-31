#!/usr/bin/python3

from docmanager.xmlhandler import XmlHandler

def test_XmlHandler_findelem(tmp_valid_xml):
    """Unit test for find_elem
    """
    
    xml = XmlHandler(tmp_valid_xml.strpath)
    xml.set({"a/b/c": None})
    
    assert xml.find_elem("a/b/c") is not None
    assert xml.find_elem("a") is not None
    assert xml.find_elem("b") is None
