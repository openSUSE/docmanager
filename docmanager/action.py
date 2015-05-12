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

from docmanager import filehandler
from docmanager import table
from docmanager.logmanager import log, logmgr_flog
from docmanager.xmlhandler import XmlHandler, localname
from docmanager.core import ReturnCodes
from prettytable import PrettyTable
import sys

class Actions(object):
    """An Actions instance represents an action event
    """

    __keywords=["SELECT", "WHERE", "SORTBY"]

    def __init__(self, args):
        """Initialize Actions class

        :param argparse.Namespace args: result from argparse.parse_args
        """
        logmgr_flog()

        files = args.files
        action = args.action
        arguments = args.arguments

        self.__args = args
        self.__files = filehandler.Files(files)

        if hasattr(self, action) and getattr(self, action) is not None:
            getattr(self, action)(arguments)
        else:
            log.error("Method \"%s\" is not implemented.", action)
            sys.exit(ReturnCodes.E_METHOD_NOT_IMPLEMENTED)

    def set(self, arguments):
        """Set key/value pairs from arguments

        :param list arguments: List of arguments with key=value pairs
        """
        logmgr_flog()

        for argument in arguments:
            #has the key an value?
            #when not delete the element
            if argument.find("=") >= 0:
                key, value = argument.split("=")
                log.debug("Trying to set value for property '%s' to '%s'" %
                          (key, value))
                self.__files.set(key, value)
                print("Set value for property \"{}\" to \"{}\".".format(key, value))
            else:
                log.error("Invalid usage. Set values "
                          "with the following format: property=value")
                sys.exit(ReturnCodes.E_INVALID_USAGE_KEYVAL)

    def get(self, arguments, output = None):
        """Lists all properties

        :param list arguments
        """
        logmgr_flog()

        #get the key=value pairs and print them file by file
        file_values = self.__files.get(arguments)
        files_count = len(file_values.items())

        if not len(arguments):
            for i in file_values.keys():
                count = 0
                print("Properties in " + i + ":")

                if self.__args.format == "table":
                    tbl = PrettyTable(["Property", "Value"])
                    tbl.padding_width = 1 # One space between column edges and contents (default)

                    handler = XmlHandler(i)
                    x = handler.get_all()
                    for k in x.keys():
                        prop = localname(k)
                        tbl.add_row([prop, x[k]])
                        count += 1

                    if count > 0:
                        print(tbl)
                else:
                    handler = XmlHandler(i)
                    x = handler.get_all()
                    for k in x.keys():
                        prop = localname(k)
                        print(prop + ": " + x[k])
        else:
            if self.__args.format == "table":
                count = 0

                tbl = PrettyTable(["Property", "Value"])
                tbl.padding_width = 1 # One space between column edges and contents (default)

                for i in sorted(file_values.keys()):
                    for x in file_values[i]:
                        tbl.add_row([x, file_values[i][x]])
                        count += 1

                if count > 0:
                    print(tbl)
            else:
                for i in sorted(file_values.keys()):
                    for x in file_values[i]:
                        if len(file_values[i]) > 1:
                            print("{}: {}".format(x, file_values[i][x]))
                        else:
                            print(file_values[i][x])

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
        for file, boolean in is_set.items():
            if boolean is False:
                values.pop(file)

        #create the table, add content, sort and print
        tbl = table.Table()
        tbl.add_by_list(values)
        tbl.sort(sort)
        print(tbl)

    def delete(self, arguments):
        """Delete a property

        :param list arguments:
        """
        logmgr_flog()

        for argument in arguments:
            log.debug("Trying to delete property \"%s\".", argument)
            self.__files.set(argument)
            print("Property \"{}\" has been deleted.".format(argument))

    def split_arguments(self, arguments):
        """TODO:

        :param list arguments:
        :return:
        :rtype:  dict
        """
        logmgr_flog()

        splited_arguments = {}
        for keyword in self.__keywords:
            splited_arguments.update({keyword:[]})

        keyword = None
        for part in arguments:
            if part in self.__keywords:
                keyword = part
            elif keyword is not None:
                splited_arguments[keyword].append(part)
        return splited_arguments

    def parse_where(self, where):
        """TODO:

        :param list where:
        :return:
        :rtype: dict
        """

        logmgr_flog()

        filterd_where = {}
        for pair in where:
            key, values = pair.split("=")
            value = values.split(",")
            filterd_where.update({key:value})
        return filterd_where

    def parse_sort(self, sort):
        """TODO:

        :param sort:
        :return:
        :rtype:  None or TODO
        """
        logmgr_flog()

        if len(sort) > 0:
            return sort[0]
        else:
            return None
