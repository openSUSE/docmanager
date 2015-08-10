#!/usr/bin/python3

import pytest
import sys
from docmanager import __version__
from docmanager.cli import parsecli

def test_version():
    """Check if version is available and set"""
    assert __version__

def test_version_from_cli(capsys):
    """Checks if option --version creates a correct version"""
    # Source: http://pytest.org/latest/capture.html?highlight=capsys#accessing-captured-output-from-a-test-function
    #with pytest.raises(SystemExit):
    try:
        parser = parsecli(["--version"])
    except SystemExit as e:
        pass

    out, err = capsys.readouterr()
    
    # for some reason, the version number string from argparse
    # will be printed to stderr and not to stdout
    if (sys.version_info.major, sys.version_info.minor) != (3, 3):
        assert out.split()[-1] == __version__
    else:
        assert err.split()[-1] == __version__

