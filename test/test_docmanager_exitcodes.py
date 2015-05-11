#!/usr/bin/python3

import pytest
from docmanager import parsecli
from docmanager.core import ReturnCodes

def test_exitcodes():
    """Check for specific exit codes"""
    try:
        parser = parsecli([])
    except SystemExit as e:
        assert e.code == ReturnCodes.E_CALL_WITHOUT_PARAMS, "Expected exit code {} but got {}.".format(ReturnCodes.E_CALL_WITHOUT_PARAMS, e.code)