#!/usr/bin/python3

import pytest
from docmanager.xmlhandler import XmlHandler
from lxml.etree import XMLSyntaxError

def test_brokenxml(tmp_broken_xml):
    """Checks the behavior of the XML handler if an exception will be
       thrown when an invalid XML file is given

    :param py.path.local tmp_broken_xml: Fixture, pointing to a temporary
                                         XML file
    """
    with pytest.raises(XMLSyntaxError):
        handler = XmlHandler(tmp_broken_xml.strpath)