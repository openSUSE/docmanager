#!/usr/bin/python3

import sys
import pytest

from docmanager import __version__
from docmanager import ArgParser


def test_version():
    """Check if version is available and set"""
    assert __version__

def test_version_from_cli(capsys):
    """Checks if option --version creates a correct version"""
    # Source: http://pytest.org/latest/capture.html?highlight=capsys#accessing-captured-output-from-a-test-function
    with pytest.raises(SystemExit):
        parser = ArgParser(["testdm", "--version"])
        out, err = capsys.readouterr()
        assert err.split()[-1] == __version__
