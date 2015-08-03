import os
import pytest
import shlex
from docmanager.config import docmanagerconfig
from docmanager.cli import parsecli
from py.path import local

def test_alias_feature_0(capsys):
    """Tests the alias feature
    """
    testdir = os.path.dirname(__file__)
    configfile = os.path.join(testdir, "testfiles/dm-test.conf")
    cmd = "--config {} amazing_alias".format(configfile)
    args = parsecli(shlex.split(cmd))

    assert args.configfile == configfile
    assert args.files == ['example.xml']
