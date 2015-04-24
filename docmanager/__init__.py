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

import argparse
from docmanager import action
from docmanager.logmanager import log
import logging
import sys

class DocManager:

    def __init__(self):
        parser = ArgParser()
        action.Actions(parser.files, parser.action, parser.arguments)

class ArgParser:

    def __init__(self):
        self.__parser = argparse.ArgumentParser(prog="docmanager",
                        description="Docmanager sets, gets, or analyzes meta-information for DocBook5 XML files.")
        self.add_arguments()
        self.parse_arguments()

    def add_arguments(self):
        file_group = self.__parser.add_argument_group("Files")
        file_group.add_argument(
                    "-f",
                    "--files",
                    nargs="+",
                    required=True,
                    help="One or more DocBook XML or DC files."
                )

        action_group = self.__parser.add_argument_group("Actions")
        actions = action_group.add_mutually_exclusive_group(required=True)
        actions.add_argument(
                    "-s",
                    "--set",
                    nargs="+",
                    help="Set key=value property (one or more) to delete the key let the value blank."
                )
        actions.add_argument(
                    "-g",
                    "--get",
                    nargs="+",
                    help="Get key and returns value."
                )
        actions.add_argument(
                    "-a",
                    "--analyze",
                    nargs="+",
                    help="Similar to get, but query can be given as pseudo SQL syntax. "  \
                         "allowed keywords are SELECT, WHERE, and SORTBY. " \
                         "Output is formatted as table."
                )
        self.__parser.add_argument('-v', '--verbose',
                    action='count',
                    help="Increase verbosity level"
                )

    def parse_arguments(self):
        self.__parser.parse_args(namespace=self)
        if self.set is not None:
            self.action="set"
            self.arguments=self.set
        elif self.get is not None:
            self.action="get"
            self.arguments=self.get
        elif self.analyze is not None:
            self.action="analyze"
            self.arguments=self.analyze

        loglevel = {
            None: logging.NOTSET,
            1: logging.INFO,
            2: logging.DEBUG
        }

        log.setLevel(loglevel.get(self.verbose, logging.DEBUG))

def main():
    """Entry point for the application script"""
    DocManager()