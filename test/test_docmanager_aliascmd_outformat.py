import os
import pytest
import shlex
from docmanager.action import Actions
from docmanager.cli import parsecli
from docmanager.display import getrenderer

data = [ 
    ('json', '{"myfiles": "analyze -f", "amazing_alias": "get example.xml", "my": "alias", "alias_format_test1": "alias1", "alias_format_test2": "alias2"}\n' ),
    ('xml', '<!DOCTYPE docmanager>\n<docmanager>\n  <aliases>\n    <alias name="myfiles">analyze -f</alias>\n    <alias name="amazing_alias">get example.xml</alias>\n    <alias name="my">alias</alias>\n    <alias name="alias_format_test1">alias1</alias>\n    <alias name="alias_format_test2">alias2</alias>\n  </aliases>\n</docmanager>\n\n'),
    ('table', '+--------------------+-----------------+\n| Alias              | Command         |\n+--------------------+-----------------+\n| myfiles            | analyze -f      |\n| amazing_alias      | get example.xml |\n| my                 | alias           |\n| alias_format_test1 | alias1          |\n| alias_format_test2 | alias2          |\n+--------------------+-----------------+\n')
]

@pytest.mark.parametrize("format_type,expected", data)
def test_docmanager_aliascmd_outformat(format_type, expected, capsys):
    """Tests the 'alias' command
    """

    # set default values
    testdir = os.path.dirname(__file__)
    configfile = os.path.join(testdir, "testfiles/dm-test.conf")
    cmd = "alias --own {} set alias_format_test1 alias1".format(configfile)
    Actions(parsecli(shlex.split(cmd))).parse()
    cmd = "alias --own {} set alias_format_test2 alias2".format(configfile)
    Actions(parsecli(shlex.split(cmd))).parse()

    # list all available aliases
    cmd = "alias --own {} --format {} list".format(configfile, format_type)
    args = parsecli(shlex.split(cmd))
    a = Actions(parsecli(shlex.split(cmd)))
    res = a.parse()
    renderer = getrenderer(format_type)
    renderer(res, args=a.args)

    # read output
    out, err = capsys.readouterr()

    # compare
    assert out == expected
