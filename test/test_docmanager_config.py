
from docmanager.config import docmanagerconfig
from docmanager.cli import parsecli
import os
from py.path import local
import pytest
import shlex


@pytest.mark.parametrize("configstr,expected", [
    ["""[general]""", ['general']],
    ["""[foo]
hallo=True
[bar]""",             ['foo', 'bar']],
])
def test_docmanager_config(tmpdir, configstr, expected):
    """Create own config file and check
    """
    configdir = tmpdir.mkdir(".config")
    configfile = configdir / "config"
    configfile.write_text(configstr, encoding="utf-8")

    config = docmanagerconfig([configfile.strpath], include_etc=False)
    result = config.sections()
    assert result == expected


def test_docmanager_configfile():
    testdir = os.path.dirname(__file__)
    configfile = os.path.join(testdir, "testfiles/dm-test.conf")
    cmd = "--config {} get -p x foo.xml".format(configfile)
    args = parsecli(shlex.split(cmd))

    assert os.path.exists(configfile)
    assert args.configfile == configfile
    assert args.config.sections()
