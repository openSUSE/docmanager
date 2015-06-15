#!/usr/bin/python3

import pytest
from docmanager.cli import parsecli
from docmanager.action import Actions
from docmanager.core import ReturnCodes

@pytest.mark.parametrize("option,correct,wrong", [
    #('maintainer', 'SUSE', ''),
    ('status', 'proofing', 'bla'),
    ('deadline', '2015-05-22', 'bla'),
    ('priority', 2, 11),
    ('translation', 'yes', 'bla'),
    ('languages', 'en_US,en,de', 'bla')
])
def test_docmanager_inputformatcheck(option, correct, wrong, tmp_valid_xml, capsys):
    """ Test the input format """
    
    tmp_file = tmp_valid_xml.strpath
    
    # check with a wrong input format
    code = -1
    
    try:
        clicmd = 'set --{} {} {}'.format(option, wrong, tmp_file)
        a = Actions(parsecli(clicmd.split()))
    except SystemExit as e:
        code = e.code
        
    assert code == ReturnCodes.E_WRONG_INPUT_FORMAT, "Wrong exit code. Expected {} but got {}.".format(ReturnCodes.E_WRONG_INPUT_FORMAT, code)
    
    #  check with the correct input format
    code = 0
    
    try:
        clicmd = 'set --{} {} {}'.format(option, correct, tmp_file)
        a = Actions(parsecli(clicmd.split()))
    except SystemExit as e:
        code = e.code
        
    assert 0 == code, "Wrong exit code. Expected 0 but got {}.".format(code)
