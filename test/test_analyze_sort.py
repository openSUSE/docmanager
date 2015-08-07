#!/usr/bin/python3

import pytest
import shlex
from docmanager.action import Actions
from docmanager.cli import parsecli

def test_analyze_sort_0(testdir, tmpdir, capsys):
    """ Test the analyze sort feature """

    xmlset = list()

    i = 1
    while i <= 3:
        xmlset.append("analyze_sort-{}.xml".format(i))
        i += 1
    
    xmlfiles = [ testdir / base for base in xmlset ]
    for xmlfile in xmlfiles:
        xmlfile.copy(tmpdir)
    xmlfiles = [ str(tmpdir / base) for base in xmlset ]
    
    clicmd = 'analyze -qf "{{maintainer}}" -s "maintainer" {}'.format(" ".join(xmlfiles))
    a = Actions(parsecli(shlex.split(clicmd)))
    a.parse()
    out, err = capsys.readouterr()
    
    expected_output = "a\nb\nc\n"

    assert not err
    assert expected_output == out

def test_analyze_sort_1(testdir, tmpdir, capsys):
    """ Test the analyze sort feature (numeric input) """

    xmlset = list()

    i = 1
    while i <= 3:
        xmlset.append("analyze_sort-{}.xml".format(i))
        i += 1
    
    xmlfiles = [ testdir / base for base in xmlset ]
    for xmlfile in xmlfiles:
        xmlfile.copy(tmpdir)
    xmlfiles = [ str(tmpdir / base) for base in xmlset ]
    
    clicmd = 'analyze -qf "{{priority}}" -s "priority" {}'.format(" ".join(xmlfiles))
    a = Actions(parsecli(shlex.split(clicmd)))
    a.parse()
    out, err = capsys.readouterr()
    
    expected_output = "1\n2\n10\n"

    assert not err
    assert expected_output == out
