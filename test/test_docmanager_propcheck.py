#!/usr/bin/python3

import pytest
import shlex
from docmanager.cli import parsecli

@pytest.mark.parametrize("source,expected", [
    ("get -p hello -p world {}", ['hello', 'world']),
    ("get -p hello,world {}", ['hello', 'world']),
    ("set -p hello=world -p world=hello {}", ['hello=world', 'world=hello']),
    ("set -p hello=world,world=hello {}", ['hello=world', 'world=hello']),
    ("set -p foo='a b' {}", ['foo=a b']),
    ('set -p foo="a b" {}', ['foo=a b']),
    ('set -p foo="a b",bar="c d" {}', ['foo=a b', 'bar=c d']),
    ('set -p foo="a b" -p bar="c d" {}', ['foo=a b', 'bar=c d']),
])
def test_docmanager_propcheck(source, expected, tmp_valid_xml):
    """Check the arguments from the argument parser for the set and get commands"""
    args = parsecli(shlex.split(source.format(tmp_valid_xml)))
    assert args.properties == expected