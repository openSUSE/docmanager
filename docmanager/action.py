#!/usr/bin/python3
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
import sys

class Actions:

    __keywords=["SELECT", "WHERE", "SORTBY"]

    def __init__(self, files, action, arguments):
        logmgr_flog()

        self.__files = filehandler.Files(files)
        method = getattr(self, action)
        if method is not None:
            method(arguments)
        else:
            log.error("Method \"%s\" is not implemented.", action)
            sys.exit(6)


    def set(self, arguments):
        logmgr_flog()

        for argument in arguments:
            #has the key an value?
            #when not delete the element
            if argument.find("=") >= 0:
                key, value = argument.split("=")
                log.debug("Set value for property \"%s\" to \"%s\".", key, value)
                self.__files.set(key, value)
            else:
                log.error("Invalid usage. You can set values with the following format: property=value")
                sys.exit(5)

    def get(self, arguments):
        logmgr_flog()

        #get the key=value pairs and print them file by file
        file_values = self.__files.get(arguments)
        files_count = len(file_values.items())

        for filename, values in sorted(file_values.items()):
            for key, value in values.items():
                if files_count > 1:
                    print(filename + " -> " + value)
                else:
                    print(value)


    def analyze(self, arguments):
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
        for file, bool in is_set.items():
            if bool == False:
                values.pop(file)

        #create the table, add content, sort and print
        tbl = table.Table()
        tbl.add_by_list(values)
        tbl.sort(sort)
        tbl.print()

    def split_arguments(self, arguments):
        logmgr_flog()

        splited_arguments = {}
        for keyword in self.__keywords:
            splited_arguments.update({keyword:[]})

        keyword = None
        for part in arguments:
            if part in self.__keywords:
                keyword = part
            elif keyword != None:
                splited_arguments[keyword].append(part)
        return splited_arguments

    def parse_where(self, where):
        logmgr_flog()

        filterd_where = {}
        for pair in where:
            key, values = pair.split("=")
            value = values.split(",")
            filterd_where.update({key:value})
        return filterd_where

    def parse_sort(self, sort):
        logmgr_flog()

        if len(sort) > 0:
            return sort[0]
        else:
            return None