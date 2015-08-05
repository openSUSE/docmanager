import os
import shlex
from docmanager.action import Actions
from docmanager.cli import parsecli

def test_docmanager_aliascmd_0(capsys):
    """Tests the 'alias' command
    """
    testdir = os.path.dirname(__file__)
    configfile = os.path.join(testdir, "testfiles/dm-test.conf")
    cmd = "alias --own {} set my alias".format(configfile)
    Actions(parsecli(shlex.split(cmd))).parse()

    cmd = "alias --own {} get my".format(configfile)
    args = parsecli(shlex.split(cmd))
    Actions(parsecli(shlex.split(cmd))).parse()

    out, err = capsys.readouterr()

    assert out == "alias\n"

def test_docmanager_aliascmd_1(capsys):
    """Tests the 'alias' command
    """
    testdir = os.path.dirname(__file__)
    configfile = os.path.join(testdir, "testfiles/dm-test.conf")
    cmd = "alias --own {} get abcblabla".format(configfile)
    Actions(parsecli(shlex.split(cmd))).parse()

    out, err = capsys.readouterr()

    assert out == ""

def test_docmanager_aliascmd_2(capsys):
    """Tests the 'alias' command
    """
    testdir = os.path.dirname(__file__)
    configfile = os.path.join(testdir, "testfiles/dm-test.conf")
    cmd = "alias --own {} set new_test yeah".format(configfile)
    Actions(parsecli(shlex.split(cmd))).parse()

    cmd = "alias --own {} get new_test".format(configfile)
    Actions(parsecli(shlex.split(cmd))).parse()
    out, err = capsys.readouterr()
    assert out == "yeah\n"

    cmd = "alias --own {} del new_test".format(configfile)
    Actions(parsecli(shlex.split(cmd))).parse()

    cmd = "alias --own {} get new_test".format(configfile)
    Actions(parsecli(shlex.split(cmd))).parse()
    out, err = capsys.readouterr()
    assert out == ""
