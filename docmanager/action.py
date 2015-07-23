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

import sys
from collections import OrderedDict
from docmanager.config import Config
from docmanager.core import DefaultDocManagerProperties, ReturnCodes, BugtrackerElementList
from docmanager.logmanager import log, logmgr_flog
from docmanager.shellcolors import ShellColors
from docmanager.xmlhandler import XmlHandler


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
        self.configfile = Config()
        
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

        _set = dict()
        props = list(DefaultDocManagerProperties)
        validFiles = 0
        invalidFiles = 0

        # append bugtracker properties if needed
        if self.__args.with_bugtracker == True:
            for p in BugtrackerElementList:
                props.append(p)

        # set default properties
        for d in props:
            rprop = d.replace("/", "_")

            if hasattr(self.__args, rprop) and getattr(self.__args, rprop) is not None:
                _set[d] = getattr(self.__args, rprop)

        # iter through all xml handlers and init its properties
        for xh in self.__xml:
            if xh.invalidXML == False:
                validFiles += 1

                log.debug("Trying to initialize the predefined DocManager properties for '{}'.".format(xh.filename))
                if xh.init_default_props(self.__args.force, self.__args.with_bugtracker) == 0:
                    print("[" + ShellColors().make_green("success") + "] Initialized default properties for '{}'.".format(xh.filename))
                else:
                    log.warn("Could not initialize all properties for '{}' because "
                          "there are already some properties in the XML file "
                          "which would be overwritten after this operation has been "
                          "finished. If you want to perform this operation and "
                          "overwrite the existing properties, you can add the "
                          "'--force' option to your command.".format(xh.filename))

                # set default values for the given properties
                for i in _set:
                    ret = xh.get(i)
                    if len(ret[i]) == 0 or self.__args.force:
                        xh.set({ i: str(_set[i]) })

                # if bugtracker options are provided, set default values
                for i in BugtrackerElementList:
                    rprop = i.replace("/", "_")

                    if hasattr(self.__args, rprop) and getattr(self.__args, rprop) is not None and len(getattr(self.__args, rprop)) >= 1:
                        xh.set({ i: getattr(self.__args, rprop) })

                # safe the xml file
                xh.write()
            else:
                invalidFiles += 1
                print("[" + ShellColors().make_red("failed") + "] Initialized default properties for '{}'. ".format(xh.filename) + ShellColors().make_red(xh.xmlLogErrorString))

        print("")
        print("Initialized successfully {} files. {} files failed.".format(ShellColors().make_green(validFiles), ShellColors().make_red(invalidFiles)))

    def set(self, arguments):
        """Set key/value pairs from arguments

        :param list arguments: List of arguments with key=value pairs
        """
        logmgr_flog()

        invalidFiles = 0
        validFiles = 0

        # init xml handlers for all given files
        handlers = OrderedDict()

        for idx, i in enumerate(self.__files):
            log.debug("Trying to initialize the XmlHandler for file '{}'.".format(i))
            handlers[i] = self.__xml[idx]

            if handlers[i].invalidXML:
                invalidFiles += 1
            else:
                validFiles += 1


        # split key and value
        args = [ i.split("=") for i in arguments]

        # iter through all key and values
        for arg in args:
            key, value = arg
            try:
                if key == "languages":
                    value = value.split(",")
                    value = ",".join(self.remove_duplicate_langcodes(value))

                for f in self.__files:
                    if not handlers[f].invalidXML:
                        log.debug("[{}] Trying to set value for property '{}' to '{}'.".format(f, key, value))
                        if self.__args.bugtracker == True:
                            handlers[f].set({"bugtracker/" + key: value})
                        else:
                            handlers[f].set({key: value})
                        print("[{}] Set value for property \"{}\" to \"{}\".".format(f, key, value))

            except ValueError:
                log.error('Invalid usage. '
                          'Set values with the following format: '
                          'property=value')
                sys.exit(ReturnCodes.E_INVALID_USAGE_KEYVAL)

        # save the changes
        for f in self.__files:
            if not handlers[f].invalidXML:
                log.debug("[{}] Trying to save the changes.".format(f))
                handlers[f].write()
                print("[{}] Saved changes.".format(f))
        
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

            for f in self.__files:
                if handlers[f].invalidXML:
                    print("{}: {}".format(f, ShellColors().make_red(handlers[f].xmlErrorString)))
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

        for f in self.__files:
            handlers[f] = XmlHandler(f)

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

                log.debug("[{}] Trying to delete property \"{}\".".format(f, a))
                handlers[f].delete(prop, cond)
                print("[{}] Property \"{}\" has been deleted.".format(f, a))

        for f in self.__files:
            log.debug("[{}] Trying to save the changes.".format(f))
            handlers[f].write()
            print("[{}] Saved changes.".format(f))

    def remove_duplicate_langcodes(self, values):
        new_list = []
        for i in values:
            if i not in new_list:
                new_list.append(i)

        return new_list

    @property
    def args(self):
        return self.__args