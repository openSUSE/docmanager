#!/usr/bin/env python3

import pytest
from docmanager.filehandler import Files

def test_file_not_found():
    """Check a filename which cannot be found
    """
    with pytest.raises(SystemExit):
        f = Files(["__filename_not_found__"])
