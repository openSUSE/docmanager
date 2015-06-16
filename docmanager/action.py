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
from collections import OrderedDict
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

    def __init__(self, args):
        """Initialize Actions class

        :param argparse.Namespace args: result from argparse.parse_args
        """
        logmgr_flog()

        self.__files = args.files
        self.__args = args
        self.__xml = [ XmlHandler(x) for x in self.__files ]


    def parse(self):
        logmgr_flog()
        
        action = self.__args.action
        if hasattr(self, action) and getattr(self, action) is not None:
            log.debug("Action.__init__: {}".format(self.__args))
            return getattr(self, action)(self.__args.properties)
        else:
            log.error("Method \"%s\" is not implemented.", action)
            sys.exit(ReturnCodes.E_METHOD_NOT_IMPLEMENTED)


    def init(self, arguments):
        logmgr_flog()
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
            
            xh.write()

    def set(self, arguments):
        """Set key/value pairs from arguments

        :param list arguments: List of arguments with key=value pairs
        """
        logmgr_flog()

        # init xml handlers for all given files
        handlers = OrderedDict()
        for i in self.__files:
            handlers[i] = XmlHandler(i)

        # split key and value
        args = [ i.split("=") for i in arguments]

        # iter through all key and values
        for arg in args:
            key, value = arg
            try:
                if key == "languages":
                    value = value.split(",")
                    value = ",".join(self.remove_duplicate_langcodes(value))

                for file in self.__files:
                    log.debug("[{}] Trying to set value for property '{}' to '{}'.".format(file, key, value))
                    handlers[file].set({key: value})
                    print("[{}] Set value for property \"{}\" to \"{}\".".format(file, key, value))

            except ValueError:
                log.error('Invalid usage. '
                          'Set values with the following format: '
                          'property=value')
                sys.exit(ReturnCodes.E_INVALID_USAGE_KEYVAL)

        print("")

        # save the changes
        for file in self.__files:
            log.debug("[{}] Trying to save the changes.".format(file))
            handlers[file].write()
            print("[{}] Saved changes.".format(file))

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

    def remove_duplicate_langcodes(self, values):
        new_list = []
        for i in values:
            if i not in new_list:
                new_list.append(i)

        return new_list

    @property
    def args(self):
        return self.__args