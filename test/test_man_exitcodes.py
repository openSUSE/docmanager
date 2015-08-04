#

from lxml import etree
import os
import re
import shlex
import subprocess
from docmanager.core import ReturnCodes

def test_man_exitcodes_0():
    """Test if all exit codes are documented
    """
    gitrepo = None

    try:
        cmd = shlex.split("git rev-parse --show-toplevel")
        git = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        gitrepo = git.communicate()

        # Not a git repository?
        if git.returncode != 128:
            gitrepo = gitrepo[0].decode("utf-8").strip()
    except FileNotFoundError:
        gitrepo = None

    if gitrepo:
        content = None
        with open('{}/man/xml/docmanager.exitcodes.xml'.format(gitrepo), 'r') as f:
            content = f.readlines()

        for i in dir(ReturnCodes):
            if i.find('E_') == 0:
                v = ReturnCodes.__getattribute__(ReturnCodes, i)
                found = False

                for x in content:
                    if '<term>{}</term>\n'.format(v) in x:
                        found = True
                        break

                assert found == True, "Exit Code {} is not documented in man page!".format(v)

def test_man_exitcodes_1():
    """Test if there are exit codes documented, which are no longer in core.py
    """
    gitrepo = None

    try:
        cmd = shlex.split("git rev-parse --show-toplevel")
        git = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        gitrepo = git.communicate()

        # Not a git repository?
        if git.returncode != 128:
            gitrepo = gitrepo[0].decode("utf-8").strip()
    except FileNotFoundError:
        gitrepo = None

    if gitrepo:
        content = None
        with open('{}/man/xml/docmanager.exitcodes.xml'.format(gitrepo), 'r') as f:
            content = f.readlines()

        c = re.compile('\<term\>([0-9]+)\<\/term\>')

        for i in content:
            result = c.findall(i)
            if result:
                code = result[0]

                bla = list()
                for x in dir(ReturnCodes):
                    if x.find('E_') == 0:
                        v = ReturnCodes.__getattribute__(ReturnCodes, x)
                        bla.append(v)
                        found = False

                        if v == int(code):
                            found = True
                            break

                assert found == True, "Exit Code {} is documented but does not exist!".format(code)


def test_man_exitcodes_3():
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

    root = etree.parse(os.path.join(gitrepo, 'man/xml/docmanager.exitcodes.xml'))
    vl = root.xpath("/variablelist[@id='dm.exitcodes']")
    assert vl
    vl = vl[0]
    # Check for <varlistentry>s without @id attribute
    assert not vl.xpath("varlistentry[not(@id)]")
    # Create dictionary: @id: int(<text from term>)
    manpagecodes = {i.attrib['id']: int(i.find("term").text) for i in vl.iterchildren() }
    dmcodes = { i: getattr(ReturnCodes, i) for i in ReturnCodes.__dict__ \
                if not i.startswith("__") }
    # Compare both dictionaries
    assert manpagecodes == dmcodes
