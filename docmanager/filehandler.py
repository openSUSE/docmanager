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
from docmanager.logmanager import log, logmgr_flog
from docmanager.core import ReturnCodes
from lxml import etree
import os
import subprocess
import sys

class Files(object):
    """TODO
    """

    def __init__(self, files):
        """Initializes Files class

        :param list files: list with file names
        """
        logmgr_flog()

        self.__xml_handlers = []

        #open an XML-Handler for each file
        for f in files:
            #check if the file does exists
            if not os.path.exists(f):
                log.error("File '%s' not found." % f)
                sys.exit(ReturnCodes.E_FILE_NOT_FOUND)

            _, file_extension = os.path.splitext(f)
            #check if the file is a normal XML or a DC file
            if file_extension == ".xml":
                try:
                    self.__xml_handlers.append(xmlhandler.XmlHandler(f))
                except etree.XMLSyntaxError as e:
                    log.error("Error during parsing the file '%s': %s" %
                              (f, str(e)) )
                    sys.exit(ReturnCodes.E_XML_PARSE_ERROR)
            else:
                try:
                    #run daps to get all files from a documentation
                    daps_files = subprocess.check_output("daps -d %s list-srcfiles --nodc --noent --noimg" % f, shell=True)
                    daps_files = daps_files.decode("utf-8")
                    for daps_file in daps_files.split():
                        self.__xml_handlers.append(xmlhandler.XmlHandler(daps_file))
                except subprocess.CalledProcessError as e:
                    sys.debug("Exception thrown: subprocess.CalledProcessError")
                    log.error("An error occurred while running daps for file "
                              "'%s': %s" % (f , str(e)) )
                    sys.exit(ReturnCodes.E_DAPS_ERROR)

    def get(self, keys):
        """TODO

        :param str keys:
        :return:
        :rtype: dict
        """
        logmgr_flog()

        values = {}
        #iter over all files
        for xml_handler in self.__xml_handlers:
            #get all values for a list of keys
            xml_values = xml_handler.get(keys)
            values.update({xml_handler.filename:xml_values})
        return values

    def is_set(self, pairs):
        """TODO

        :param type pairs:
        :return: mapping of filenames and result
        :rtype: dict
        """
        logmgr_flog()

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
        """Set value to key

        :param key:   element name to set
        :param value: value of element
        :type value:  str or None
        """
        logmgr_flog()

        #iter over all files and set key=value
        #if no value give delete the element
        for xml_handler in self.__xml_handlers:
            try:
                if value is not None:
                    xml_handler.set(key, value)
                else:
                    xml_handler.delete(key)
            except ValueError as e:
                log.error("Could not set value for property "
                          "'%s': %s", key, str(e))
                sys.exit(ReturnCodes.E_COULD_NOT_SET_VALUE)
