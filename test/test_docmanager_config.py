
import configparser
from docmanager.config import docmanagerconfig
from docmanager.exceptions import DMConfigFileNotFound
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
    """Test for config file
    """
    testdir = os.path.dirname(__file__)
    configfile = os.path.join(testdir, "testfiles/dm-test.conf")
    cmd = "--config {} get -p x foo.xml".format(configfile)
    args = parsecli(shlex.split(cmd), error_on_config=True)

    assert os.path.exists(configfile)
    assert args.configfile == configfile
    assert args.config.sections()


def test_docmanager_wrongconfigfile():
    """Test for config file which is not found
    """
    testdir = os.path.dirname(__file__)
    configfile = os.path.join(testdir, "/SOME/PATH/config-does-not-exist")
    cmd = "--config {} get -p x foo.xml".format(configfile)

    assert not os.path.exists(configfile)
    with pytest.raises(DMConfigFileNotFound):
        args = parsecli(shlex.split(cmd), error_on_config=True)


def test_docmanager_allconfigfiles():
    """Test for standard config files
    """
    cmd = "get -p x foo.xml"
    args = parsecli(shlex.split(cmd))
    assert args
    assert args.config
    assert args.config.configfiles
    assert args.config.usedconfigfile