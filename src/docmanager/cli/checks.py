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


import os
import os.path
import re
import sys
import urllib.request
from glob import glob

from ..core import BT_ELEMENTLIST
from ..core import DEFAULT_DM_PROPERTIES
from ..core import DEFAULTSUBCOMMANDS
from ..core import LANGUAGES
from ..core import STATUSFLAGS
from ..core import ReturnCodes
from ..logmanager import log
from ..logmanager import logmgr_flog


def show_langlist(columns=None, padding=2):
    """Prints all supported languages

    :param int columns: Maximum number of characters in a column;
                        None to fill the current terminal window
    :param int padding: space from longest entry to border
    """

    try:
        from shutil import get_terminal_size
    except ImportError:
        import os

        def get_terminal_size(fallback=(80, 24)):
            return os.terminal_size(fallback)

    maxl = max([len(i) for i in LANGUAGES])

    if columns is None or columns < maxl:
        columns = get_terminal_size().columns
    length = len(LANGUAGES)
    rowwidth = maxl + padding + 1
    divisor = columns // rowwidth
    maxline = divisor * rowwidth

    fmt="".join(["{{:<{}}}|".format(maxl + padding) for _ in range(divisor)])# flake8: noqa
    line = "-"*maxline
    print(line)
    for start, stop in zip(range(0, length, divisor),
                           range(divisor, length+divisor, divisor)):
        x = list(LANGUAGES[start:stop])
        if len(x) < divisor:
            for i in range(divisor - len(x)):
                x.append("")
        print(fmt.format(*x))
    print(line)

    sys.exit(ReturnCodes.E_OK)


def populate_properties(args):
    """Populate args.properties from "standard" options

    :param argparse.Namespace args:
    :return: list of property=value items
    :rtype: list
    """

    result = []
    for prop in DEFAULT_DM_PROPERTIES:
        proparg = prop.replace("/", "_")
        if hasattr(args, proparg) and getattr(args, proparg) is not None:
            result.append("{}={}".format(prop, getattr(args, proparg)))

    return result


def populate_bugtracker_properties(args):
    """Populate args.bugtracker_* from "standard" options

    :param argparse.Namespace args:
    :return: list of property=value items
    :rtype: list
    """

    result = []
    for prop in BT_ELEMENTLIST:
        proparg = prop.replace("/", "_")
        if hasattr(args, proparg) and getattr(args, proparg) is not None:
            result.append("{}={}".format(prop, getattr(args, proparg)))

    return result


def clean_filelist(args):
    """Clean the file list from unwanted directory names

    :param argparse.Namespace args: Parsed arguments
    """
    # Remove any directories from our files list
    allfiles = args.files[:]
    args.files = [f for f in args.files if not os.path.isdir(f)]
    diff = list(set(allfiles) - set(args.files))

    # This just disturbs especially if we want to use DocManager in scripts
    #if diff:
    #    print("Ignoring the following directories:", ", ".join(diff))


def fix_properties(args):
    """Make different property styles consistent

    :param argparse.Namespace args: Parsed arguments
    """
    # Handle the different styles with -p foo and -p foo,bar
    # Needed to split the syntax 'a,b', 'a;b' or 'a b' into a list
    # regardless of the passed arguments
    _props = []
    # Use an empty list when args.properties = None
    args.properties = [] if args.properties is None else args.properties
    for item in args.properties:
        repl = re.split("[,;]", item)
        _props.extend(repl)
    args.properties = _props

    # Fill "standard" properties (like status) also into properties list:
    if args.action in ("s", "set"):
        args.properties.extend(populate_properties(args))
        args.properties.extend(populate_bugtracker_properties(args))


def is_alias(subcmd):
    """Check if subcmd is an alias
    :rtype: bool
    """
    return subcmd not in DEFAULTSUBCOMMANDS


def parse_alias_value(value):
    """Parse pre defined constants

    :param str value: alias
    :return: parsed alias
    :rtype: str
    """
    return value.replace("{USER}", os.environ['USER'])


def input_format_check(args):
    """Checks if the given arguments have a correct value

    :param object args: Arguments object from argparser
    """
    logmgr_flog()

    if hasattr(args, 'status') and args.status is not None:
        if args.status not in STATUSFLAGS:
            print("Value of 'status' property is incorrect. "
                  "Expecting one of these values: "
                  "{}".format(", ".join(STATUSFLAGS)))
            sys.exit(ReturnCodes.E_WRONG_INPUT_FORMAT)

    if hasattr(args, 'deadline') and args.deadline is not None:
        match = re.match("^[0-9]{4}\-[0-9]{2}\-[0-9]{2}$", args.deadline)
        if match is None:
            print("Value of 'deadline' is incorrect. "
                  "Use this date format: YYYY-MM-DD")
            sys.exit(ReturnCodes.E_WRONG_INPUT_FORMAT)

    if hasattr(args, 'priority') and args.priority is not None:
        errmsg = ("Value of 'priority' is incorrect. "
                  "Expecting a value between 1 and 10.")

        if not args.priority.isnumeric():
            print(errmsg)
            sys.exit(ReturnCodes.E_WRONG_INPUT_FORMAT)

        args.priority = int(args.priority)
        if args.priority < 1 or args.priority > 10:
            print(errmsg)
            sys.exit(ReturnCodes.E_WRONG_INPUT_FORMAT)

    if hasattr(args, 'translation') and args.translation is not None:
        values = ('yes', 'no')
        if args.translation not in values:
            print("Value of 'translation' is incorrect. "
                  "Expecting one of these values: yes or no")
            sys.exit(ReturnCodes.E_WRONG_INPUT_FORMAT)

    if hasattr(args, 'languages') and args.languages is not None:
        for i in args.languages.split(","):
            if i not in LANGUAGES:
                print("Value of 'languages' is incorrect. "
                      "Language code '{}' is not supported. "
                      "Type 'docmanager --langlist' to see "
                      "all supported language codes.".format(i))
                sys.exit(ReturnCodes.E_WRONG_INPUT_FORMAT)

    if hasattr(args, 'repository') and args.repository is not None:
        request = None
        try:
            request = urllib.request.urlopen(args.repository)
        except ValueError:
            print("Value of 'repository' is incorrect. "
                  "The value is not a URL.")
            sys.exit(ReturnCodes.E_WRONG_INPUT_FORMAT)
        except urllib.error.URLError as err:
            if hasattr(err, 'code') and err.code is not None:
                if err.code is not 200:
                    log.warn("The remote server returns an error code "
                             "for this request: {} - Please double check if "
                             "the URL is correct. Nevertheless the URL will "
                             "be written into the "
                             "given files.".format(err.code))
            else:
                log.warn("The given URL '{}' seems to be invalid or the "
                         "remote server is not online. Please double "
                         "check if the URL is correct. Nevertheless the "
                         "URL will be written into the "
                         "given files.".format(args.repository))

        if hasattr(request, 'close'):
            request.close()


def fix_filelist(files):
    """Replaces * with all files in a directory (shell like)

    :param list files: file list from args.files
    """

    if files:
        tmpfiles = files[:]
        files.clear()

        for idx, i in enumerate(tmpfiles[:]):
            filelist = glob(i)
            if filelist:
                for x in filelist:
                    if not os.path.exists(x):
                        log.error("Cannot find file {!r}!".format(x))
                        sys.exit(ReturnCodes.E_FILE_NOT_FOUND)

                    files.append(x)
            else:
                if not os.path.exists(i):
                    log.error("Cannot find file {!r}!".format(i))
                    sys.exit(ReturnCodes.E_FILE_NOT_FOUND)

def fix_attributes(args):
    """Make different attributes styles consistent

    :param argparse.Namespace args: Parsed arguments
    """
    # Handle the different styles with -a foo and -a foo,bar
    # Needed to split the syntax 'a,b', 'a;b' or 'a b' into a list
    # regardless of the passed arguments
    _attrs = []
    # Use an empty list when args.attributes = None or if args.attributes does not exists
    args.attributes = [] if not hasattr(args, 'attributes') or args.attributes is None else args.attributes
    for item in args.attributes:
        repl = re.split("[,;]", item)
        _attrs.extend(repl)
    args.attributes = _attrs
