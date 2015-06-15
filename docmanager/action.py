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

import json
import sys
# from docmanager import filehandler
from docmanager import table
from docmanager.core import ReturnCodes
from docmanager.display import getrenderer
from docmanager.logmanager import log, logmgr_flog
from docmanager.xmlhandler import XmlHandler
from docmanager.xmlutil import localname
from prettytable import PrettyTable

class Actions(object):
    """An Actions instance represents an action event
    """

    # __keywords=["SELECT", "WHERE", "SORTBY"]

    def __init__(self, args):
        """Initialize Actions class

        :param argparse.Namespace args: result from argparse.parse_args
        """
        logmgr_flog()

        self.__files = args.files
        self.__args = args
        self.__xml = [ XmlHandler(x) for x in self.__files ]


    def parse(self,):
        action = self.__args.action
        if hasattr(self, action) and getattr(self, action) is not None:
            log.debug("Action.__init__: {}".format(self.__args))
            return getattr(self, action)(self.__args.properties)
        else:
            log.error("Method \"%s\" is not implemented.", action)
            sys.exit(ReturnCodes.E_METHOD_NOT_IMPLEMENTED)


    def init(self, arguments):
        log.debug("Arguments {}".format(arguments))
        for xh in self.__xml:
            log.debug("Trying to initialize the predefined DocManager properties for '{}'.".format(xh.filename))
            if xh.init_default_props(self.__args.force) == 0:
                log.info("Initialized default properties for '{}'.".format(xh.filename))
            else:
                log.warn("Could not initialize all properties for '{}' because "
                      "there are already some properties in the XML file "
                      "which would be overwritten after this operation has been "
                      "finished. If you want to perform this operation and "
                      "overwrite the existing properties, you can add the "
                      "'--force' option to your command.".format(xh.filename))

    def set(self, arguments):
        """Set key/value pairs from arguments

        :param list arguments: List of arguments with key=value pairs
        """
        logmgr_flog()

        args = [ i.split("=") for i in arguments]

        for arg in args:
            key, value = arg
            try:
                if key == "languages":
                    value = value.split(",")
                    value = ",".join(self.remove_duplicate_langcodes(value))
                log.debug("Trying to set value for property '{}' to '{}'".format(key, value))
                for xh in self.__files:
                    xml = XmlHandler(xh)
                    xml.set(key, value)
                    xml.write()

                print("Set value for property \"{}\" to \"{}\".".format(key, value))

            except ValueError:
                log.error('Invalid usage. '
                          'Set values with the following format: '
                          'property=value')
                sys.exit(ReturnCodes.E_INVALID_USAGE_KEYVAL)


    def get(self, arguments):
        """Lists all properties

        :param list arguments:
        :return: [(FILENAME, {PROPERTIES}), ...]
        :rtype: list
        """
        logmgr_flog()
        return [ (xh.filename, xh.get(arguments)) for xh in self.__xml ]


    def delete(self, arguments):
        """Delete a property

        :param list arguments:
        """
        logmgr_flog()

        for argument in arguments:
            log.debug("Trying to delete property \"%s\".", argument)
            self.__files.set(argument)
            print("Property \"{}\" has been deleted.".format(argument))


    def query(self, arguments):
        """Display table after selecting properties

        :param list arguments:
        """
        logmgr_flog()

        #split the arguments by sql like keywords
        #and convert strings into dicts
        splited_arguments = self.split_arguments(arguments)
        values = self.__files.get(splited_arguments["SELECT"])
        where = self.parse_where(splited_arguments["WHERE"])
        sort = self.parse_sort(splited_arguments["SORTBY"])

        #if the file has no key=value match remove the file
        #from the list
        is_set = self.__files.is_set(where)
        for fileobj, boolean in is_set.items():
            if boolean is False:
                values.pop(fileobj)

        #create the table, add content, sort and print
        tbl = table.Table()
        tbl.add_by_list(values)
        tbl.sort(sort)
        print(tbl)

    def remove_duplicate_langcodes(self, values):
        new_list = []
        for i in values:
            if i not in new_list:
                new_list.append(i)

        return new_list

    @property
    def args(self):
        return self.__args