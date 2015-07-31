#!/usr/bin/python3

import pytest
import shlex
from docmanager.action import Actions
from docmanager.cli import parsecli

def test_analyze_defaultoutput_0(testdir, tmpdir, capsys):
    """ Test the analyze default output """
    
    xmlset = [ "analyze_output-1.xml" ]

    xmlfiles = [ testdir / base for base in xmlset ]
    for xmlfile in xmlfiles:
        xmlfile.copy(tmpdir)
    xmlfiles = [ str(tmpdir / base) for base in xmlset ]

    clicmd = 'analyze -qf "{{emptytest}} {{emptytest2}}" -do "-" {}'.format(" ".join(xmlfiles))
    a = Actions(parsecli(shlex.split(clicmd)))
    a.parse()
    out, err = capsys.readouterr()
    
    expected_output = "- -\n"

    assert not err
    assert expected_output == out
