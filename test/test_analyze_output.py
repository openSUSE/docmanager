#!/usr/bin/python3

import pytest
import shlex
from docmanager.action import Actions
from docmanager.cli import parsecli

def test_analyze_sort_0(testdir, tmpdir, capsys):
    """ Test the analyze output """

    xmlset = list()

    i = 1
    while i <= 3:
        xmlset.append("analyze_output-{}.xml".format(i))
        i += 1
    
    xmlfiles = [ testdir / base for base in xmlset ]
    for xmlfile in xmlfiles:
        xmlfile.copy(tmpdir)
    xmlfiles = [ str(tmpdir / base) for base in xmlset ]
    
    clicmd = 'analyze -qf "{{maintainer}} {{status}} {{priority}}" {}'.format(" ".join(xmlfiles))
    a = Actions(parsecli(shlex.split(clicmd)))
    a.parse()
    out, err = capsys.readouterr()
    
    expected_output = "mschnitzer wip 1\ntoms done 10\nfs editing 4\n"

    assert not err
    assert expected_output == out
