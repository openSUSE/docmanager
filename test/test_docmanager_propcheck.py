#!/usr/bin/python3

import pytest
from docmanager import parsecli

@pytest.mark.parametrize("input,expected", [
    ("get -p hello -p world {}", ['hello', 'world']),
    ("get -p hello,world {}", ['hello', 'world']),
    ("set -p hello=world -p world=hello {}", ['hello=world', 'world=hello']),
    ("set -p hello=world,world=hello {}", ['hello=world', 'world=hello']),
])

def test_docmanager_propcheck(input, expected, tmp_valid_xml):
    """Check the arguments from the argument parser for the set and get commands"""
    args = parsecli(input.format(tmp_valid_xml).split())
    assert args.arguments == expected