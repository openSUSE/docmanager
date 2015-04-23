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

from docmanager import xmlhandler
from lxml import etree
import os
import subprocess
import sys

class Files:

    def __init__(self, files):
        self.__xml_handlers = []

        #open an XML-Handler for each file
        for file in files:
            #check if the file does exists
            if not os.path.exists(file):
                print("File \"" + file + "\" could not be found.")
                sys.exit(1)

            file_name, file_extension = os.path.splitext(file)
            #check if the file is a normal XML or a DC file
            if file_extension == ".xml":
                try:
                    self.__xml_handlers.append(xmlhandler.XmlHandler(file))
                except etree.XMLSyntaxError as e:
                    print("Error during parsing the file \"" + file + "\": " + str(e))
                    sys.exit(3)
            else:
                try:
                    #run daps to get all files from a documentation
                    daps_files = subprocess.check_output("daps -d %s list-srcfiles --nodc --noent --noimg" %file, shell=True)
                    daps_files = daps_files.decode("utf-8")
                    for daps_file in daps_files.split():
                        self.__xml_handlers.append(xmlhandler.XmlHandler(daps_file))
                except subprocess.CalledProcessError as e:
                    print("An error occurred while running daps for file \"" + file + "\": " + str(e))
                    sys.exit(4)

    def get(self, keys):
        values = {}
        #iter over all files
        for xml_handler in self.__xml_handlers:
            #get all values for a list of keys
            xml_values = xml_handler.get(keys)
            values.update({xml_handler.filename:xml_values})
        return values

    def is_set(self, pairs):
        is_set = {}
        #iter over all files
        for xml_handler in self.__xml_handlers:
            result = None
            #check if the file has one of the give values
            for key, values in pairs.items():
                if result is not False:
                    result = xml_handler.is_set(key, values)
            is_set.update({xml_handler.filename:result})
        return is_set

    def set(self, key, value=None):
        #iter over all files and set key=value
        #if no value give delete the element
        for xml_handler in self.__xml_handlers:
            try:
                if value is not None:
                    xml_handler.set(key, value)
                else:
                    xml_handler.delete(key)
            except ValueError as e:
                print("Could not set value for property \"" + key + "\": " + str(e))
                sys.exit(2)