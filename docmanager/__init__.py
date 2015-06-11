#
# Copyright (c) 2014-2015 SUSE Linux GmbH
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

__author__="Rick Salevsky"
__version__="3.0.0-RC3"

import argparse
import logging
import re
import sys
from docmanager import action
from docmanager.core import ReturnCodes, LANGUAGES, DefaultDocManagerProperties
from docmanager.logmanager import log
from docmanager.tmpfile import clear_tmpdir
from prettytable import PrettyTable
from xml.sax._exceptions import SAXParseException

def populate_properties(args):
    """Populate args.properties from "standard" options

    :param argparse.Namespace args:
    :return: list of property=value items
    :rtype: list
    """
    result=[]

    for prop in DefaultDocManagerProperties:
        if hasattr(args, prop) and getattr(args, prop) is not None:
            result.append( "{}={}".format(prop, getattr(args, prop)) )
    return result


def parsecli(cliargs=None):
    """Parse command line arguments

    :param list cliargs: Arguments to parse or None (=use sys.argv)
    :return: parsed arguments
    :rtype: argparse.Namespace
    """
    filesargs = dict(nargs='+',
                     metavar="FILE",
                     help='One or more DocBook XML or DC files.'
                )
    propargs = dict(action='append',
                    # metavar="PROP[[=VALUE],PROP[=VALUE]...]
                    help='One or more properties to get, set, or delete. '
                         'Syntax of PROPERTIES: PROP[[=VALUE],PROP[=VALUE]...] '
                         'Example (get/del): -p foo or -p foo,bar or -p foo -p bar '
                         'Example (set): -p foo=a or -p foo=a,bar=b or -p foo=a -p bar=b'
               )

    parser = argparse.ArgumentParser(
        prog="docmanager",
        usage="%(prog)s COMMAND [OPTIONS] FILE [FILE ...]",
        description="Docmanager sets, gets, delets, or queries "
                    "meta-information for DocBook5 XML files.")
    parser.add_argument('--version',
                        action='version',
                        version='%(prog)s ' + __version__
                        )
    parser.add_argument('-v', '--verbose',
                action='count',
                help="Increase verbosity level"
            )
    parser.add_argument('--langlist',
                       action='store_true'
                       )

    # Create a subparser for all of our subcommands,
    # save the subcommand in 'dest'
    subparsers = parser.add_subparsers(
        dest='action',
        title="Available subcommands",
        # metavar="COMMAND"
        )

    # 'init' command for the initialization
    pinit = subparsers.add_parser('init',
                                  aliases=['i'],
                                  help='Initializes an XML document with predefined properties.')
    pinit.add_argument('--force',
                       action='store_true'
                      )
    pinit.add_argument("files", **filesargs)

    # 'get' subparser
    pget = subparsers.add_parser('get',
                        aliases=['g'],
                        help='Get key and returns value'
                    )
    pget.add_argument('-p', '--properties', **propargs)
    pget.add_argument('-f', '--format',
                      choices=['table','json'],
                      help='Set the output format.'
                    )
    pget.add_argument("files", **filesargs)

    # 'set' subparser
    pset = subparsers.add_parser('set',
                        aliases=['s'],
                        help='Set key=value property (one or more) to '
                             'delete the key let the value blank.'
                    )
    pset.add_argument('-p', '--properties', **propargs)
    pset.add_argument('-M', '--maintainer',
                      help='Set the property "maintainer" for the given documents.'
                    )
    pset.add_argument('-S', '--status',
                      help='Set the property "status" for the given documents.'
                    )
    pset.add_argument('-D', '--deadline',
                      help='Set the property "deadline" for the given documents.'
                    )
    pset.add_argument('-P', '--priority',
                      help='Set the property "priority" for the given documents.'
                    )
    pset.add_argument('-T', '--translation',
                      help='Set the property "translation" for the given documents.'
                    )
    pset.add_argument('-L', '--languages',
                      help='Set the property "languages" for the given documents.'
                    )
    pset.add_argument("files", **filesargs)

    # 'del' subparser
    pdel = subparsers.add_parser('del',
                        aliases=['d'],
                        help='Delete properties from XML documents'
                    )
    pdel.add_argument('-p', '--properties', **propargs)
    pdel.add_argument("files", **filesargs)

    # analyze subparser
    panalyze = subparsers.add_parser('query',
                                     aliases=['q', 'analyze'],
                                     help='Similar to get, but query can be given as pseudo SQL syntax. '  \
                                        'allowed keywords are SELECT, WHERE, and SORTBY. ' \
                                        'Output is formatted as table.'
                                    )
    panalyze.add_argument("files",
                nargs='+',
                metavar="FILES",
                help='One or more DocBook XML or DC files.'
                )

    ## -----
    args = parser.parse_args(args=cliargs)

    # Rewrite aliases
    actions = { "i":       "init",
                "init":    "init",
                "g":       "get",
                "get":     "get",
                "d":       "delete",
                "del":     "delete",
                "s":       "set",
                "set":     "set",
                "q":       "query",
                "a":       "query",
                "analyze": "query",
               }
    args.action = actions.get(args.action)
    
    # Display language list
    if args.langlist is True:
        show_langlist()

    # If docmanager is called without anything, print the help and exit
    if args.action is None:
        parser.print_help()
        sys.exit(ReturnCodes.E_CALL_WITHOUT_PARAMS)

    if args.action == "init":
        args.properties = []

    # Fix properties
    # Handle the different styles with -p foo and -p foo,bar
    # Needed to split the syntax 'a,b', 'a;b' or 'a b' into a list
    # regardless of the passed arguments
    _props=[ ]
    # Use an empty list when args.properties = None
    args.properties = [] if args.properties is None else args.properties
    for item in args.properties:
        m = re.split("[,;]", item)
        _props.extend(m)
    args.properties = _props

    # Fill "standard" properties (like status) also into properties list:
    if args.action in ("s", "set"):
        args.properties.extend(populate_properties(args))

    args.arguments = args.properties
    loglevel = {
        None: logging.NOTSET,
        1: logging.INFO,
        2: logging.DEBUG
    }

    log.setLevel(loglevel.get(args.verbose, logging.DEBUG))
    log.debug("Arguments: %s", args)

    # clear old docmanager tmp files
    clear_tmpdir()

    # check for input format
    input_format_check(args)

    return args

def show_langlist(columns=None):
    """Prints the language table

    :param int columns: Maximum number of characters in a column;
                        None to fill the current terminal window
    """
    try:
        import os
        from shutil import get_terminal_size
    except ImportError:
        def get_terminal_size(fallback=(80, 24)):
            return os.terminal_size(fallback)

    maxl = max([len(i) for i in LANGUAGES])

    if columns is None or columns < maxl:
        columns = get_terminal_size().columns
    length = len(LANGUAGES)
    padding = 2
    rowwidth = maxl + padding + 1
    divisor = columns // rowwidth
    maxline = divisor * rowwidth

    fmt="".join([ "{{:<{}}}|".format(maxl + padding) for _ in range(divisor)])
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

def input_format_check(args):
    """Checks if the given arguments have a correct value

    :param object args: Arguments object from argparser
    """
    if hasattr(args, 'status') and args.status is not None:
        values = [ 'editing', 'edited', 'proofing', 'proofed', 'comment', 'ready' ]
        if args.status not in values:
            print("Value of 'status' is incorrect. Expecting one of these values: editing, edited, proofing, proofed, comment, or ready")
            sys.exit(ReturnCodes.E_WRONG_INPUT_FORMAT)
    elif hasattr(args, 'deadline') and args.deadline is not None:
        r = re.match("^[0-9]{4}\-[0-9]{2}\-[0-9]{2}$", args.deadline)
        if r is None:
            print("Value of 'deadline' is incorrect. Use this date format: YYYY-MM-DD")
            sys.exit(ReturnCodes.E_WRONG_INPUT_FORMAT)
    elif hasattr(args, 'priority') and args.priority is not None:
        args.priority = int(args.priority)
        if args.priority < 1 or args.priority > 10:
            print("Value of 'priority' is incorrect. Expecting a value between 1 and 10.")
            sys.exit(ReturnCodes.E_WRONG_INPUT_FORMAT)
    elif hasattr(args, 'translation') and args.translation is not None:
        values = [ 'yes', 'no' ]
        if args.translation not in values:
            print("Value of 'translation' is incorrect. Expecting one of these values: yes or no")
            sys.exit(ReturnCodes.E_WRONG_INPUT_FORMAT)
    elif hasattr(args, 'languages') and args.languages is not None:
        for i in args.languages.split(","):
            if i not in LANGUAGES:
                print("Value of 'languages' is incorrect. Language code '{}' is not supported. Type 'docmanager --langlist' to see all supported language codes.".format(i))
                sys.exit(ReturnCodes.E_WRONG_INPUT_FORMAT)

def main(cliargs=None):
    """Entry point for the application script

    :param list cliargs: Arguments to parse or None (=use sys.argv)
    """
    try:
        action.Actions(parsecli(cliargs))
    except PermissionError as err:
        log.error("{} on file {!r}.".format(err.args[1], err.filename))
        sys.exit(ReturnCodes.E_PERMISSION_DENIED)
    except ValueError as err:
        log.error(err)
        sys.exit(ReturnCodes.E_INVALID_XML_DOCUMENT)