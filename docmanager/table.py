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

from docmanager import prettytable

class Table(object):
    """A Table instance represents the result of the search
    """
    def __init__(self):
        """Initialize Table class"""
        self.__table = prettytable.PrettyTable()
        self.__header = []

    def add_row(self, name, values):
        """Add row into table

        :param str name:
        :param dict values:
        """
        row = [name]
        for key in self.__header:
            #ignore the Files item we have the name already
            if key != "Files":
                value = (values.get(key))
                #has the file this value?
                if value is not None:
                    row.append(value)
                else:
                    row.append("-")
        self.__table.add_row(row)

    def set_header(self, keys):
        """Set header of table

        :param str keys:
        """
        #prepare header first column is filename + keys
        header = ["Files"]
        header = header + list(keys)
        self.__table.field_names = header
        self.__header = header

    def add_by_list(self, file_list):
        """TODO:

        :param list file_list:
        """
        #first gather all header items
        keys = set()
        for filename, values in file_list.items():
            keys.update(values.keys())
        self.set_header(keys)

        #now we can create the rows
        for filename, values in file_list.items():
            self.add_row(filename, values)

    def sort(self, sortby):
        """Sort table

        :param sortby:
        """
        self.__table.sortby = sortby

    def print(self):
        # TODO: Use __str__ magic method instead!
        print(self.__table)
