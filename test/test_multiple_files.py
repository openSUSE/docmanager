#

import pytest
from argparse import Namespace

from docmanager.action import Actions
from docmanager import parsecli


def repeat(iterable, n=1):
    """Generator for repeating each object in iterable n times

    :param iterable iterable: An iterable object like lists, tuple, etc.
    :param int n:  repeat n times
    """
    for i in iterable:
        for j in range(n):
            yield i


@pytest.mark.parametrize("props,xmlset,expected", [
  (["status"], ["test-dm-status-1.xml", "test-dm-status-2.xml"], ["a", "b"]),
  (["foo"], ["test-dm-status-1.xml", "test-dm-status-2.xml"],    []),
  (["status", "abc"], ["test-dm-status-1.xml", "test-dm-status-2.xml"], ["A", "a", "B", "b"]),
])
def test_multiple_files(props, xmlset, expected, testdir, tmpdir, capsys):
    """Checks multiple files to get the correct result

    :param list props:    properties to check
    :param list xmlset:   relative XML filenames
    :param list expected: expected result
    :param py.path.local testdir: Path to test directory (fixture)
    :param py.path.local tmpdir: temporary directory (fixture)
    :param capsys: capture system stderr
    """
    # files = [ "test-dm-status-1.xml", "test-dm-status-2.xml" ]
    xmlfiles = [ testdir / base for base in xmlset ]
    for xmlfile in xmlfiles:
        xmlfile.copy(tmpdir)
    xmlfiles = [ str(tmpdir / base) for base in xmlset ]

    cli="get -p %s %s" % (",".join(props), " ".join(xmlfiles))
    a = Actions( parsecli(cli.split()) )
    out, err = capsys.readouterr()
    result = [ tuple(line.split(" -> "))  for line in out.strip().split("\n") ]

    # TODO: Make it more general
    # Expected the following output:
    #  file1 -> a
    #  file2 -> b
    if expected:
        expected = list(zip(repeat(xmlfiles, len(props)), expected))
    else:
        expected = [('',)]
    assert not err
    assert expected == result