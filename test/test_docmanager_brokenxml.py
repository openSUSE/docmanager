#!/usr/bin/python3

import pytest
from docmanager.exceptions import DMXmlParseError
from docmanager.xmlhandler import XmlHandler
from xml.sax._exceptions import SAXParseException

def test_brokenxml(tmp_broken_xml):
    """Checks the behavior of the XML handler if an exception will be
       thrown when an invalid XML file is given

    :param py.path.local tmp_broken_xml: Fixture, pointing to a temporary
                                         XML file
    """
    handler = None

    try:
        handler = XmlHandler(tmp_broken_xml.strpath)
    except DMXmlParseError:
        pass

    assert handler is None
