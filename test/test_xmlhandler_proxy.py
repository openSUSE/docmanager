#

import io

import pytest
from docmanager.xmlhandler import Proxy, XMLProxyHandler, XmlHandler
from docmanager.xmlutil import prolog, root_sourceline

def test_dummy_proxy():
    """
    """
    class Foo:
        def __init__(self, a=0, b=0):
            self.a = a
            self.b = b
        def add(self):
            return a+b

    a, b = 1, 2
    proxy = Proxy(Foo, a, b)
    #print(dir(proxy))
    #print(proxy._Proxy__args)
    #print(proxy._Proxy__kwargs)
    assert proxy.a == a
    assert proxy.b == b


@pytest.mark.parametrize("base,expected", [
  ("file_with_entity.xml",           6),
  ("docmanager_overwrite_test.xml",  4),
  ("invalid_db5_file.xml",           1),
  ("missing_info_element.xml",       4),
])
def test_root_sourceline(testdir, tmpdir, base, expected):
    """Check if root_sourceline() does behave correctly
    """
    xmlfile = testdir.join(base)
    xmlfile.copy(tmpdir)
    xmlfile = tmpdir.join(base)
    rootline, column = root_sourceline(xmlfile.strpath)

    assert rootline == expected


@pytest.mark.parametrize("base,expected", [
  ("file_with_entity.xml",           (6, 1)),
  ("docmanager_overwrite_test.xml",  (4, 1)),
  ("invalid_db5_file.xml",           (1, 1)),
  ("missing_info_element.xml",       (4, 1)),
])
def test_prolog(testdir, tmpdir, base, expected):
    """Check if prolog) does behave correctly
    """
    xmlfile = testdir.join(base)
    xmlfile.copy(tmpdir)
    xmlfile = tmpdir.join(base)
    length, sourceline, header = prolog(xmlfile.strpath)
    assert length
    assert sourceline
    assert header


# @pytest.skip
def _test_xmlproxy(testdir, tmpdir):
    """
    """
    base = "file_with_entity.xml"
    xmlfile = testdir.join(base)
    xmlfile.copy(tmpdir)
    xmlfile = tmpdir.join(base)

    proxy = XMLProxyHandler(XmlHandler, xmlfile.strpath)
    assert proxy
    # assert proxy._XMLProxyHandler__buffer
