#!/usr/bin/python3

import pytest
from docmanager import main
from docmanager.core import ReturnCodes
import shlex

def test_exitcodes_0(tmp_broken_xml):
    """ call docmanager without params """
    try:
        parser = main([])
    except SystemExit as e:
        assert e.code == ReturnCodes.E_CALL_WITHOUT_PARAMS, \
            "Expected exit code {} but got {}.".format(ReturnCodes.E_CALL_WITHOUT_PARAMS,
                                                       e.code)

def test_exitcodes_1(tmp_broken_xml):
    """ parse broken xml file in get """
    try:
        clicmd = "get {}".format(tmp_broken_xml)
        a = main(shlex.split(clicmd))
    except SystemExit as e:
        assert e.code == ReturnCodes.E_XML_PARSE_ERROR, \
            "Expected exit code {} but got {}.".format(ReturnCodes.E_XML_PARSE_ERROR,
                                                       e.code)

def test_exitcodes_2(tmp_invalid_db5_file):
    """ check for an invalid DocBook 5 file """
    try:
        clicmd = "get {}".format(tmp_invalid_db5_file)
        a = main(shlex.split(clicmd))
    except SystemExit as e:
        assert e.code == ReturnCodes.E_INVALID_XML_DOCUMENT, \
            "Expected exit code {} but got {}.".format(ReturnCodes.E_INVALID_XML_DOCUMENT,
                                                       e.code)