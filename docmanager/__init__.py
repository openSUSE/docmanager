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
__version__="3.0"

import argparse
from docmanager import action
from docmanager.logmanager import log
import logging
import re
import sys


class ArgParser:
    """Encapsulates arguments in ArgumentParser
    """

    def __init__(self, args=None):
        """Initializes ArgParser class"""
        self.__args=args
        self.__parser = argparse.ArgumentParser(prog="docmanager",
                        description="Docmanager sets, gets, or analyzes meta-information for DocBook5 XML files.")
        self.add_arguments()
        self.parse_arguments()

    def add_arguments(self):
        """Adds arguments to ArgumentParser"""
        self.__parser.add_argument('--version',
                        action='version',
                        version='%(prog)s ' + __version__
                        )
        self.__parser.add_argument('-v', '--verbose',
                    action='count',
                    help="Increase verbosity level"
                )

        # Create a subparser for all of our subcommands,
        # save the subcommand in 'dest'
        subparsers = self.__parser.add_subparsers(dest='action')

        # 'get' subparser
        pget = subparsers.add_parser('get',
                            aliases=['g'],
                            help='Get key and returns value'
                        )
        pget.add_argument('-p', '--properties',
                        action='append',
                        help=''
                        )
        pget.add_argument('-k', '--list-all-keys',
                        help='list all keys in info element'
                        )

        # 'set' subparser
        pset = subparsers.add_parser('set',
                            aliases=['s'],
                            help='Set key=value property (one or more) to delete the key let the value blank.'
                        )
        pset.add_argument('-p', '--properties',
                        action='append',
                        help=''
                        )

        # 'del' subparser
        pdel = subparsers.add_parser('del',
                            aliases=['d'],
                            help='Delete properties from XML documents'
                        )
        pdel.add_argument('-p', '--properties',
                        action='append',
                        help=''
                        )

        # analyze subparser
        panalyze = subparsers.add_parser('analyze',
                                         aliases=['a'],
                                         help='Similar to get, but query can be given as pseudo SQL syntax. '  \
                                            'allowed keywords are SELECT, WHERE, and SORTBY. ' \
                                            'Output is formatted as table.'
                                        )

        # Filenames
        self.__parser.add_argument("files",
                    nargs='+',
                    metavar="FILES",
                    help="One or more DocBook XML or DC files."
                    )


    def parse_arguments(self):
        """Parses command line arguments"""
        self.__parser.parse_args(args=self.__args, namespace=self)

        # Fix properties
        # Handle the different styles with -p foo and -p foo,bar
        # Needed to split the syntax 'a,b', 'a;b' or 'a b' into a list
        # regardless of the passed arguments
        _props=[ ]
        for item in self.properties:
            _props.extend(re.split("[ ,;]", item))
        self.properties = _props

        self.arguments = self.properties
        loglevel = {
            None: logging.NOTSET,
            1: logging.INFO,
            2: logging.DEBUG
        }

        log.setLevel(loglevel.get(self.verbose, logging.DEBUG))
        log.debug("args: {}".format(dir(self.__args)))

    def __repr__(self):
        """ """


def main():
    """Entry point for the application script"""
    parser = ArgParser()
    action.Actions(parser.files, parser.action, parser.arguments)