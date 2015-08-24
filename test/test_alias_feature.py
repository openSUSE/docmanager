import os
import pytest
import shlex
from docmanager.config import docmanagerconfig
from docmanager.cli import parsecli
from py.path import local

def test_alias_feature_0():
    """Tests the alias feature
    """
    testdir = os.path.dirname(__file__)
    configfile = os.path.join(testdir, "testfiles/dm-test.conf")
    cmd = "--config {} amazing_alias".format(configfile)
    args = parsecli(shlex.split(cmd))

    assert args.configfile == configfile
    assert args.files == ['test/testfiles/valid_xml_file.xml']


@pytest.mark.parametrize("configstr,expected", [
    ["""[alias]
foo = bar
""", [('foo', 'bar')]
    ],
])
def test_alias_read(tmpdir, configstr, expected):
    configdir = tmpdir.mkdir(".config")
    configfile = configdir / "config"
    configfile.write_text(configstr, encoding="utf-8")

    config = docmanagerconfig([configfile.strpath], include_etc=False)
    result = list(config['alias'].items())
    assert result == expected


@pytest.mark.parametrize("configstr1,configstr2,expected", [
    ["[alias]\nfoo = a",  "[alias]\nfoo = b", "b"],
    ["[x]\nfoo = a",      "[alias]\nfoo = b", "b"],
    ["# only a comment",  "[alias]\nfoo = b", "b"],
    ["[alias]\nfoo = b",  "# only a comment", "b"],
    ["[alias]\nfoo = aa\nbar = aa",
     "[alias]\nfoo = b",
     "b"
    ],
    ["[alias]\nfoo = aa\nbar = aa\n[abc]",
     "[alias]\nfoo = b\n[abc]\n# ---",
     "b"
    ],
])
def test_alias_multipleconfigs(tmpdir, configstr1, configstr2, expected):
    configdir = tmpdir.mkdir(".config")
    configfile1 = configdir / "config1"
    configfile2 = configdir / "config2"
    configfile1.write_text(configstr1, encoding="utf-8")
    configfile2.write_text(configstr2, encoding="utf-8")

    config = docmanagerconfig([configfile1.strpath, configfile2.strpath],
                              include_etc=False)
    assert config['alias']['foo'] == expected
