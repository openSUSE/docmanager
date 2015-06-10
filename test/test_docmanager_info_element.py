#!/usr/bin/python3

import pytest
from docmanager.xmlhandler import XmlHandler

def test_missing_info_element(tmp_missing_info_element):
    """Checks if docmanager behaves correctly if a given XML files does not provide an info element

    :param py.path.local tmp_missing_info_element: Fixture, pointing to a temporary XML file"""

    try:
        handler = XmlHandler(tmp_missing_info_element.strpath)
    except SystemExit as e:
        assert e.code == 7, "Expected exit code 7 but got " + str(e.code)
