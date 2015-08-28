#!/usr/bin/python3

import os
import pytest
import shlex
from docmanager.action import Actions
from docmanager.cli import parsecli
from docmanager.display import getrenderer
from docmanager.xmlhandler import XmlHandler

data = [ 
    ('json', '{"[REPLACE_FILENAME]": {"myprop": {"Uf4C56WL": "blub"}}}\n' ),
    ('xml', '<!DOCTYPE docmanager>\n<docmanager>\n  <files>\n    <file name="[REPLACE_FILENAME]">\n      <property name="myprop">\n        <attribute name="Uf4C56WL">blub</attribute>\n      </property>\n    </file>\n  </files>\n</docmanager>\n\n'),
    ('table', 'File: [REPLACE_FILENAME]\n+----------+-----------+-------+\n| Property | Attribute | Value |\n+----------+-----------+-------+\n|  myprop  |  Uf4C56WL |  blub |\n+----------+-----------+-------+\n'),

    # test case for the default text output
    ('', '[REPLACE_FILENAME][myprop] -> Uf4C56WL=blub\n')
]

@pytest.mark.parametrize("format_type,expected", data)
def test_docmanager_getattr0(format_type, expected, tmp_valid_xml, capsys):
    ustr = 'Uf4C56WL'
    handler = XmlHandler(tmp_valid_xml.strpath)
    handler.set({"myprop": None})
    handler.set_attr("myprop", {ustr: 'blub'})
    handler.write()

    if format_type:
        clicmd = "get-attr -p myprop -a {} --format {} {}".format(ustr, format_type, tmp_valid_xml.strpath)
    else:
        clicmd = "get-attr -p myprop -a {} {}".format(ustr, tmp_valid_xml.strpath)
    a = Actions(parsecli(shlex.split(clicmd)))
    res = a.parse()
    renderer = getrenderer(format_type)
    renderer(res, args=a.args)

    out, err = capsys.readouterr()

    expected = expected.replace("[REPLACE_FILENAME]", tmp_valid_xml.strpath)

    assert out == expected
