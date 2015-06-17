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
from docmanager.shellcolors import ShellColors
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
        
        if hasattr(self.__args, 'stop_on_error'):
            self.__xml = [ XmlHandler(x, self.__args.stop_on_error) for x in self.__files ]
        else:
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

        invalidFiles = 0
        validFiles = 0

        # init xml handlers for all given files
        handlers = OrderedDict()
        index = 0

        for i in self.__files:
            log.debug("Trying to initialize the XmlHandler for file '{}'.".format(i))
            handlers[i] = self.__xml[index]

            if handlers[i].invalidXML == True:
                invalidFiles += 1
            else:
                validFiles += 1

            index += 1

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
                    if handlers[file].invalidXML == False:
                        log.debug("[{}] Trying to set value for property '{}' to '{}'.".format(file, key, value))
                        handlers[file].set({key: value})
                        print("[{}] Set value for property \"{}\" to \"{}\".".format(file, key, value))

            except ValueError:
                log.error('Invalid usage. '
                          'Set values with the following format: '
                          'property=value')
                sys.exit(ReturnCodes.E_INVALID_USAGE_KEYVAL)

        # save the changes
        for file in self.__files:
            if handlers[file].invalidXML == False:
                log.debug("[{}] Trying to save the changes.".format(file))
                handlers[file].write()
                print("[{}] Saved changes.".format(file))
        
        print("")
        if validFiles == 1:
            print("Wrote in {} valid XML file.".format(ShellColors().make_green(validFiles)))
        else:
            print("Wrote in {} valid XML files.".format(ShellColors().make_green(validFiles)))

        if invalidFiles > 0:
            print("")
            
            if invalidFiles == 1:
                print("Skipped {} XML file due to an error.".format(ShellColors().make_red(invalidFiles)))
            else:
                print("Skipped {} XML files due to errors.".format(ShellColors().make_red(invalidFiles)))

            for file in self.__files:
                if handlers[file].invalidXML == True:
                    print("{}: {}".format(file, ShellColors().make_red(handlers[file].xmlErrorString)))
            sys.exit(ReturnCodes.E_SOME_FILES_WERE_INVALID)

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

        handlers = dict()

        for file in self.__files:
            handlers[file] = XmlHandler(file)

            for a in arguments:
                prop = ""
                cond = None

                s = a.split("=")
                if len(s) == 1:
                    prop = s[0]
                else:
                    prop = s[0]
                    s.pop(0)
                    cond = "".join(s)

                log.debug("[{}] Trying to delete property \"{}\".".format(file, a))
                handlers[file].delete(prop, cond)
                print("[{}] Property \"{}\" has been deleted.".format(file, a))

        for file in self.__files:
            log.debug("[{}] Trying to save the changes.".format(file, a))
            handlers[file].write()
            print("[{}] Saved changes.".format(file, a))

    def remove_duplicate_langcodes(self, values):
        new_list = []
        for i in values:
            if i not in new_list:
                new_list.append(i)

        return new_list

    @property
    def args(self):
        return self.__args