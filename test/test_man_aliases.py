#

from configparser import ConfigParser
from lxml import etree
import os
import re
import shlex
import subprocess
from docmanager.core import ReturnCodes
from docmanager.config import BASECONFIG_NAME
from pkg_resources import resource_filename

def test_man_aliases():
    try:
        cmd = shlex.split("git rev-parse --show-toplevel")
        git = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        gitrepo = git.communicate()

        # Not a git repository?
        if git.returncode != 128:
            gitrepo = gitrepo[0].decode("utf-8").strip()
    except FileNotFoundError:
        gitrepo = None

    assert gitrepo

    configfile = resource_filename("docmanager", BASECONFIG_NAME)
    config = ConfigParser()
    x = config.read(configfile)

    # Test if the configfile could be read
    assert x
    # Test, if configfile contains an 'alias' section
    assert config['alias']

    keys = set(config['alias'].keys())

    root = etree.parse(os.path.join(gitrepo, 'man/xml/docmanager.configfiles.xml'))
    vl = root.xpath("//*[@id='dm.configfiles.sec.alias']")

    assert vl
    vl = vl[0]
    # Check for <varlistentry>s without @id attribute
    assert not vl.xpath("varlistentry[not(@id)]")

    manpagealias = { i.attrib.get('id')  for i in vl.xpath("listitem/variablelist/varlistentry") }
    assert keys == manpagealias
