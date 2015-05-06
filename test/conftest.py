#
# Copyright (c) 2015 SUSE Linux GmbH
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of version 3 of the GNU General Public License as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, contact SUSE LLC.
#
# To contact SUSE about this file by physical or electronic mail,
# you may find current contact information at www.suse.com

import sys
import os

import pytest
import py.path
from lxml import etree

testdir = py.path.local(py.path.local(__file__).dirname)

# Add current directory; this makes it possible to import all
# docmanager related files
sys.path.append('.')


# ------------------------------------------------------
# Markers
#
reason = 'Fails on Travis or else there is no network connection to GitHub.'

travis = os.environ.get('TRAVIS', False)
skipif_travis = pytest.mark.skipif(travis, reason=reason)

no_network = os.environ.get('DM_NO_NETWORK_TESTS', False)
skipif_no_network = pytest.mark.skipif(no_network, reason=reason)


# ------------------------------------------------------
# Fixtures
#

@pytest.fixture(params=["testfiles/valid_xml_file.xml"])
def tmp_valid_xml(request, tmpdir):
    """Copies XML file to temporary directory

    :param pytest.fixture tmpdir: temporary directory fixture
    :param request: XML filename as parameter
    """
    xmlfile=testdir / request.param
    assert xmlfile.exists(), "temp XML file does not exist"
    xmlfile.copy(tmpdir)
    return tmpdir.listdir(sort=xmlfile.basename)[0]

@pytest.fixture(params=["testfiles/docmanager_overwrite_test.xml"])
def tmp_docmanager_overwrite(request, tmpdir):
    """Copies XML file to temporary directory

    :param pytest.fixture tmpdir: temporary directory fixture
    :param request: XML filename as parameter
    """
    xmlfile=testdir / request.param
    assert xmlfile.exists(), "temp XML file does not exist"
    xmlfile.copy(tmpdir)
    return tmpdir.listdir(sort=xmlfile.basename)[0]

@pytest.fixture(params=["testfiles/broken_xml_file.xml"])
def tmp_broken_xml(request, tmpdir):
    """Copies XML file to temporary directory

    :param pytest.fixture tmpdir: temporary directory fixture
    :param request: XML filename as parameter
    """
    xmlfile=testdir / request.param
    assert xmlfile.exists(), "temp XML file does not exist"
    xmlfile.copy(tmpdir)
    return tmpdir.listdir(sort=xmlfile.basename)[0]