#!/usr/bin/python3

import pytest
from argparse import Namespace
from conftest import compare_pytest_version
from docmanager.action import Actions
from docmanager.cli import parsecli

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
    clicmd = 'set --{} {} {}'.format(option, value, tmp_valid_xml)
    a = Actions(parsecli(clicmd.split()))
    out, err = capsys.readouterr()

    expected = 'Set value for property "{}" to "{}".'.format(option, value)
    assert out[:-1] == expected, "set test: Expected output '{}' but got '{}'.".format(expected, out[:-1])

    # read test
    clicmd = 'get -p {} {}'.format(option, tmp_valid_xml)
    a = Actions(parsecli(clicmd.split()))
    out, err = capsys.readouterr()

    expected = value
    assert out[:-1] == expected, "get test: Expected output '{}' but got '{}'.".format(expected, out[:-1])
