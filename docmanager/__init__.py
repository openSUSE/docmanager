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
__version__="3.0.0"

from docmanager import filehandler
from docmanager.cli import parsecli
from docmanager.logmanager import log
from docmanager.core import ReturnCodes
import logging
import re
import sys



def main(cliargs=None):
    """Entry point for the application script

    :param list cliargs: Arguments to parse or None (=use sys.argv)
    """
    args = parsecli(cliargs)
    # print(args)
    renderer = filehandler.getRenderer(args.format)
    files = filehandler.Files(args.files,
                              args.action,
                              args.properties,
                              )
    result = renderer(files)
    if result is not None:
        print(result)
