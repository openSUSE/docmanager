#!/usr/bin/python3

import pytest
from argparse import Namespace
from conftest import compare_pytest_version
from docmanager import main
import shlex

@pytest.mark.skipif(compare_pytest_version((2,6,4)),
                    reason="Need 2.6.4 to execute this test")
@pytest.mark.parametrize("option,value", [
    # set section
    ('maintainer', 'SUSE'),
    ('status', 'ok'),
    ('deadline', '11-05-2015'),
    ('priority', 'high'),
    ('translation', 'DE'),
    ('languages', 'EN'),
])
def test_docmanager_predefprops(option, value, tmp_valid_xml, capsys):
    """Check predefined property actions"""
    # write test
    clicmd = 'set --{} {} {}'.format(option, value, tmp_valid_xml)
    a = main(shlex.split(clicmd))
    out, err = capsys.readouterr()

    expected = 'Set value for property "{}" to "{}".'.format(option, value)
    assert out[:-1] == expected, \
        "set test: Expected output '{}' but got '{}'.".format(expected, out[:-1])

    # read test
    clicmd = 'get -p {} {}'.format(option, tmp_valid_xml)
    a = main(shlex.split(clicmd))
    out, err = capsys.readouterr()

    expected = value
    assert out[:-1] == expected, \
        "get test: Expected output '{}' but got '{}'.".format(expected, out[:-1])