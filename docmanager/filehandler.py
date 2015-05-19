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
from prettytable import PrettyTable
import os
import sys

__all__ = ['getrenderer', 'Files', 'textrender', 'tablerender', 'DEFAULTRENDERER']


# ---------------------------------------------------
def textrender(files, **kwargs):
    """Normal text output

    :param Files files: Files object
    :param dict kwargs: for further customizations
    :return: rendered output
    :rtype: str
    """
    data = files.action()
    if data is None:
        return

    result=[]
    datalen = len(data)
    for filename, props in data.items():
        # result.append("{}:".format(filename))
        # indent="  "
        for key, value in props.items():
            if datalen == 1:
                result.append(value)
            else:
                result.append("{} -> {}={}".format(filename, key, value))
    return "\n".join(result)


def tablerender(files, **kwargs):
    """Table rendered output

    :param Files files: Files object
    :param dict kwargs: for further customizations
    :return: rendered output
    :rtype: str
    """
    data = files.action()
    if data is None:
        return
    tbl = PrettyTable(["File", "Property", "Value"])
    # One space between column edges and contents (default)
    tbl.padding_width = 1
    for filename in data:
        props = data[filename]
        for k, v in props.items():
            tbl.add_row([filename, k, v])
    return str(tbl)


DEFAULTRENDERER = textrender

def getrenderer(fmt):
    """Returns the renderer for a specific format

    :param str fmt: format ('text', 'table', or 'default')
    :return: function of renderer
    :rtype: function
    """
    # Available renderer
    renderer = {
        'default': textrender,
        'text':    textrender,
        'table':   tablerender,
    }

    return renderer.get(fmt, DEFAULTRENDERER)



# ---------------------------------------------------
class Files(object):
    """Set of XML files"""

    def __init__(self, files, action, properties):
        """Initializes Files class

        :param list files: list with file names
        :param str action: action to perform
        :paran list properties: list of properties to search for
        """
        logmgr_flog()

        self.__xml_handlers = []
        self.__files = files
        self.__action = action
        self.__props = properties

        #open an XML-Handler for each file
        for f in files:
            #check if the file does exists
            if not os.path.exists(f):
                log.error("File '%s' not found.", f)
                sys.exit(ReturnCodes.E_FILE_NOT_FOUND)
            try:
                self.__xml_handlers.append(xmlhandler.XmlHandler(f))
            except etree.XMLSyntaxError as err:
                log.error("Error during parsing the file '%s': %s",
                          f, str(err) )
                sys.exit(ReturnCodes.E_XML_PARSE_ERROR)

    def __iter__(self):
        """return iter(self) (iterator protocol)"""
        return iter(self.__xml_handlers)

    def __repr__(self):
        """Return repr(self)"""
        return "<{}: {} {}>".format(self.__class__.__name__,
                                    self.__props,
                                    self.__files
                                   )

    def action(self, act=None, props=None):
        """Perform indirect function call

        :param str act: action; if None, use action from constructor
        :param list props: properties; if None, use properties from constructor
        :return: see .set(), .get(), .del() methods
        :rtype: depends on the methods
        """
        log.debug("{} {}".format(repr(self), act))

        props = props if props is not None else self.__props
        act = act if act is not None else self.__action

        if hasattr(self, act) and getattr(self, act) is not None:
            return getattr(self, act)(props)


    # --------------
    def get(self, keys):
        """Return a single property from all files

        :param str keys: single property
        :return: dictionary of all files and its value
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

        for prop in self.__props:
            #has the key an value?
            prop = prop.split("=")
            if len(prop) == 2:
                key, value = prop
                log.debug("Trying to set value for property '%s' to '%s'",
                          key, value)
                #
                #self.__files.set(key, value)
                print("Set value for property \"{}\" to \"{}\".".format(key, value))
            else:
                log.error("Invalid usage. Set values "
                          "with the following format: property=value")
                sys.exit(ReturnCodes.E_INVALID_USAGE_KEYVAL)

            #iter over all files and set key=value
            #if no value give delete the element
            for xml_handler in self.__xml_handlers:
                try:
                    if value is not None:
                        xml_handler.set(key, value)
                    else:
                        xml_handler.delete(key)
                except ValueError as err:
                    log.error("Could not set value for property "
                            "'%s': %s", key, str(err))
                    sys.exit(ReturnCodes.E_COULD_NOT_SET_VALUE)
