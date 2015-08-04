import shlex
from docmanager.action import Actions
from docmanager.cli import parsecli
from docmanager.core import ReturnCodes

def test_docmanager_configcmd_0(tmpdir, capsys):
    """Call the DocManager 'config' sub command and modify the config file
    """
    configdir = tmpdir.mkdir(".config")
    configfile = configdir / "config"
    configfile.write_text("", encoding="utf-8")

    cmd = "config -o {} test1.test2 \"test3\"".format(configfile.strpath)
    a = Actions(parsecli(shlex.split(cmd)))
    a.parse()

    content = None
    with open(configfile.strpath, 'r') as f:
        content = f.read()

    result = "[test1]\ntest2 = test3\n\n"
    assert content == result

    try:
        cmd = "config -o {} test1.test2".format(configfile.strpath)
        a = Actions(parsecli(shlex.split(cmd)))
        a.parse()
    except SystemExit:
        pass

    out, err = capsys.readouterr()
    assert out == "test3\n"

def test_docmanager_configcmd_1(tmpdir):
    """Call the DocManager 'config' sub command with an invalid syntax and check the exit code
    """
    configdir = tmpdir.mkdir(".config")
    configfile = configdir / "config"
    configfile.write_text("", encoding="utf-8")

    code = -1
    try:
        cmd = "config -o {} test1test2 \"test3\"".format(configfile.strpath)
        a = Actions(parsecli(shlex.split(cmd)))
        a.parse()
    except SystemExit as e:
        code = e.code

    assert code == ReturnCodes.E_INVALID_CONFIG_PROPERTY_SYNTAX
