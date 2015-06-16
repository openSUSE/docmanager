#!/usr/bin/python3

import random
from docmanager.xmlhandler import XmlHandler

def test_overwrite(tmp_docmanager_overwrite):
    """Checks if it's possible to overwrite the value of a property
       in an XML document

    :param py.path.local tmp_docmanager_overwrite: Fixture, pointing to a
                                                   temporary  XML file
    """

    handler = XmlHandler(tmp_docmanager_overwrite.strpath)
    handler.set({"hello": "world"})

    assert handler.get("hello") == { "hello": "world" }, \
        'Could not override old value of property "hello" in file test.override.xml'
