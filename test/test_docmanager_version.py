#!/usr/bin/python3

import pytest
from docmanager import __version__
from docmanager import parsecli

def test_version():
    """Check if version is available and set"""
    assert __version__

def test_version_from_cli(capsys):
    """Checks if option --version creates a correct version"""
    # Source: http://pytest.org/latest/capture.html?highlight=capsys#accessing-captured-output-from-a-test-function
    with pytest.raises(SystemExit):
        parser = parsecli(["testdm", "--version"])
        out, err = capsys.readouterr()
        assert err.split()[-1] == __version__
