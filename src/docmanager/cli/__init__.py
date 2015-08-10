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

import argparse
from configparser import NoOptionError, NoSectionError

from .. import __version__
from ..config import docmanagerconfig, create_userconfig
from ..core import ReturnCodes, DEFAULT_DM_PROPERTIES
from ..logmanager import log, logmgr_flog, setloglevel

from .checks import (show_langlist, populate_properties, populate_bugtracker_properties,
clean_filelist, fix_properties, is_alias, parse_alias_value, input_format_check,
fix_filelist)
from .cmd_alias import alias_subcmd, rewrite_alias
from .cmd_analyze import analyze_subcmd
from .cmd_config import config_subcmd
from .cmd_del import del_subcmd
from .cmd_get import get_subcmd
from .cmd_init import init_subcmd
from .cmd_set import set_subcmd

from glob import glob
import re
import os
import shlex
import sys
import urllib.request



def parsecli(cliargs=None, error_on_config=False):
    """Parse command line arguments

    :param list cliargs: Arguments to parse or None (=use sys.argv)
    :return: parsed arguments
    :rtype: argparse.Namespace
    """

    # parse just --config and --verbose
    confparser = argparse.ArgumentParser(add_help=False)
    confparser.add_argument('--config', dest='configfile', metavar='CONFIGFILE',
                            help='user config file location, uses also '
                                 'XDG_CONFIG_HOME env variable if set')
    confparser.add_argument('-v', '--verbose', action='count',
                            help="Increase verbosity level")
    args, remaining_argv = confparser.parse_known_args(cliargs)

    # Store configuration filename for further usage:
    configfile = args.configfile
    config = None

    # init log module
    setloglevel(args.verbose)

    # init config module
    # Exception handled in __init__.py
    config = docmanagerconfig(args.configfile)

    # Read the log level from the config files
    try:
        verbosity_level = int(config["general"]["verbosity_level"])

        if args.verbose is not None:
            if verbosity_level > args.verbose:
                args.verbose =  verbosity_level
        else:
            args.verbose = verbosity_level

        # set log level
        setloglevel(args.verbose)
    except KeyError:
        pass

    if remaining_argv:
        alias = remaining_argv[0]

        # parse aliases
        if is_alias(alias) and not alias.startswith('-'):
            remaining_argv = remaining_argv[1:]

            try:
                value = parse_alias_value("{alias} {args}".format(alias=config.get("alias", alias),
                                                args=" ".join(remaining_argv)))
                cliargs = shlex.split(value)
            except (NoSectionError, NoOptionError) as err:
                pass

    # parse cli parameters
    filesargs = dict(nargs='+',
                     metavar="FILE",
                     help='One or more DocBook XML or DC files.'
                     )
    propargs = dict(action='append',
                    # metavar="PROP[[=VALUE],PROP[=VALUE]...]
                    help='One or more properties to get, set, or delete. '
                         'Syntax of PROPERTIES: PROP[[=VALUE],PROP[=VALUE]...]'
                         ' Example (get/del): -p foo or -p foo,bar or '
                         '-p foo -p bar '
                         'Example (set): -p foo=a or -p foo=a,bar=b or '
                         '-p foo=a -p bar=b'
                    )
    stop_on_error = dict(action='store_true',
                       default=False,
                       help='Stop if an (XML) error is found '
                            'in a XML file (default: %(default)s)'
                )
    queryformat = dict(action='store',
                       help='The output query format. For more information, have a look into the manual page.'
                )
    sort = dict(action='store',
                       help='Sorts the output by XML properties.'
                )
    filters = dict(action='append',
                       help='Filters the analyzed data. For more information, have a look into the manual page.'
                )
    default_output = dict(action='store',
                       help='Sets the default output for properties which are not available in a file. By default, DocManager prints nothing.'
                )
    mainprops = tuple(("-{}".format(i.upper()[0]), "--{}".format(i))
                      for i in DEFAULT_DM_PROPERTIES)

    parser = argparse.ArgumentParser(
        prog="docmanager",
        parents=[confparser],
        # usage="%(prog)s COMMAND [OPTIONS] FILE [FILE ...]\n",
        description="Docmanager sets, gets, deletes, or queries "
                    "meta-information for DocBook5 XML files.")
    parser.add_argument('--version',
                        action='version',
                        version='%(prog)s ' + __version__
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

    init_subcmd(subparsers, stop_on_error, propargs, mainprops, filesargs)
    get_subcmd(subparsers, propargs, filesargs)
    set_subcmd(subparsers, stop_on_error, propargs, mainprops, filesargs)
    del_subcmd(subparsers, propargs, filesargs)
    analyze_subcmd(subparsers, queryformat, filters, sort, default_output, filesargs)
    config_subcmd(subparsers)
    alias_subcmd(subparsers)

    # -----
    args = parser.parse_args(args=cliargs)

    if args.configfile is None:
        args.configfile = configfile

    args.config = config

    ##
    rewrite_alias(args)

    # Display language list
    if args.langlist is True:
        show_langlist()

    # If docmanager is called without anything, print the help and exit
    if args.action is None:
        parser.print_help()
        sys.exit(ReturnCodes.E_CALL_WITHOUT_PARAMS)

    if not hasattr(args, 'properties'):
        args.properties = None

    if not hasattr(args, 'stop_on_error'):
        args.stop_on_error = False

    # Clean file list
    if hasattr(args, 'files'):
        clean_filelist(args)
    else:
        args.files = None

    # Fix file list - this is needed for aliases - issue#67
    fix_filelist(args.files)

    # Fix properties
    fix_properties(args)

    # check for input format
    input_format_check(args)

    return args
