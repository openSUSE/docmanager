#!/usr/bin/python3

import pytest
from argparse import Namespace
from conftest import compare_pytest_version
from docmanager.action import Actions
from docmanager.cli import parsecli
import shlex

@pytest.mark.xfail
@pytest.mark.skipif(compare_pytest_version((2,6,4)),
                    reason="Need 2.6.4 to execute this test")
@pytest.mark.parametrize("option,value", [
    # set section
    ('maintainer', 'SUSE'),
    ('status', 'editing'),
    ('deadline', '2015-05-11'),
    ('priority', '2'),
    ('translation', 'no'),
    ('languages', 'en,de'),
])
def test_docmanager_predefprops(option, value, tmp_valid_xml, capsys):
    """Check predefined property actions"""
    # write test
    clicmd = shlex.split('set --{} {} {}'.format(option, value, tmp_valid_xml))
    a = Actions(parsecli(clicmd))

    # read test
    clicmd = shlex.split('get -p {} {}'.format(option, tmp_valid_xml))
    a = Actions(parsecli(clicmd))
    out, err = capsys.readouterr()

    expected = value
    assert out[:-1] == expected, "get test: Expected output '{}' " \
                                 "but got '{}'.".format(expected, out[:-1])
