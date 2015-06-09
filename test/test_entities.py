#

import pytest

from io import StringIO
from docmanager.xmlutil import preserve_entities, recover_entities, \
                               isXML, \
                               replaceinstream

START="[[["
END="]]]"

@pytest.mark.parametrize("text, expected", [
  ("a &welt; b",        "a {s}welt{e} b"),
  ("a &we-lt; b",        "a {s}we-lt{e} b"),
  ("a &#xa0; b",        "a &#xa0; b"),
  ("a &w.e.lt; b",      "a {s}w.e.lt{e} b"),
  ("a &w_e.lt; b",      "a {s}w_e.lt{e} b"),
  ("a &XaX0; b",        "a {s}XaX0{e} b"),
  ("a &ab1; b &cde; c", "a {s}ab1{e} b {s}cde{e} c"),
])
def test_preserve_entities(text, expected):
    """Checks preserving of entities in text"""
    result = preserve_entities(text)
    assert result == expected.format(s=START, e=END)


@pytest.mark.parametrize("text, expected", [
  ("a {s}welt{e} b",            "a &welt; b"),
  ("a {s}we-lt{e} b",            "a &we-lt; b"),
  ("a &#xa0; b",                "a &#xa0; b", ),
  ("a {s}w.e.lt{e} b",          "a &w.e.lt; b"),
  ("a {s}w_e.lt{e} b",          "a &w_e.lt; b"),
  ("a {s}XaX0{e} b",            "a &XaX0; b", ),
  ("a {s}ab1{e} b {s}cde{e} c", "a &ab1; b &cde; c",),
])
def test_restore_entities(text, expected):
    """Checks restoring entities in text"""
    result = recover_entities(text.format(s=START, e=END))
    assert result == expected


@pytest.mark.parametrize("textio, expected", [
  (StringIO("a &welt; b"),        "a {s}welt{e} b"),
  (StringIO("a &we-lt; b"),        "a {s}we-lt{e} b"),
  (StringIO("a &#xa0; b"),        "a &#xa0; b"),
  (StringIO("a &w.e.lt; b"),      "a {s}w.e.lt{e} b"),
  (StringIO("a &w_e.lt; b"),      "a {s}w_e.lt{e} b"),
  (StringIO("a &XaX0; b"),        "a {s}XaX0{e} b"),
  (StringIO("a &ab1; b &cde; c"), "a {s}ab1{e} b {s}cde{e} c"),
])
def test_replaceinstream_preserve(textio, expected):
    """Checks preserving entities from a StringIO object"""
    result = replaceinstream(textio, preserve_entities)
    assert result.getvalue() == expected.format(s=START, e=END)


@pytest.mark.parametrize("text, expected", [
  ("a {s}welt{e} b",            "a &welt; b"),
  ("a {s}we-lt{e} b",            "a &we-lt; b"),
  ("a &#xa0; b",                "a &#xa0; b", ),
  ("a {s}w.e.lt{e} b",          "a &w.e.lt; b"),
  ("a {s}w_e.lt{e} b",          "a &w_e.lt; b"),
  ("a {s}XaX0{e} b",            "a &XaX0; b", ),
  ("a {s}ab1{e} b {s}cde{e} c", "a &ab1; b &cde; c",),
])
def test_replaceinstream_recover(text, expected):
    """Checks restoring entities from a StringIO object"""
    textio = StringIO(text.format(s=START, e=END))
    result = replaceinstream(textio, recover_entities)
    assert result.getvalue() == expected


@pytest.mark.parametrize("text, expected", [
  ("<?xml version='1.0'",   True),
  ("  <?xml version='1.0'", True),
  ("<!-- hello -->",        True),
  ("<!DOCTYPE book",        True),
  ("  <!DOCTYPE article",   True),
  ("<article id='5.0'",     True),
  ("<d:article id='5.0'",   True),
  ("<dmMgr:foofoo x='a'",   True),
  ("a/b/c",                 False),
  ("xml/foo.xml",           False),
  (".hello/foo",            False),
])
def test_isxml(text, expected):
    result = isXML(text)
    assert result == expected
