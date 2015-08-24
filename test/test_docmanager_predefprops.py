#!/usr/bin/python3

import pytest
import shlex
from argparse import Namespace
from conftest import compare_pytest_version
from docmanager.action import Actions
from docmanager.cli import parsecli
from docmanager.display import getrenderer

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
    ('release', 'SLES'),
    ('release', 'SUSE Linux Enterprise Server 12'),
#    ('repository', 'https://github.com/openSUSE/docmanager')
])
def test_docmanager_predefprops(option, value, tmp_valid_xml, capsys):
    """Check predefined property actions"""
    # write test
    clicmd = shlex.split('set --{} "{}" {}'.format(option, value, tmp_valid_xml))
    a = Actions(parsecli(clicmd))
    a.parse()
    out, err = capsys.readouterr()

    # read test
    clicmd = shlex.split('get -p "{}" {}'.format(option, tmp_valid_xml))
    a = Actions(parsecli(clicmd))
    res = a.parse()
    renderer = getrenderer('default')
    renderer(res, args=a.args)

    out, err = capsys.readouterr()

    expected = value
    assert out[:-1] == expected, "get test: Expected output '{}' " \
                                 "but got '{}'.".format(expected, out[:-1])
