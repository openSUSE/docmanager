#
# Copyright (c) 2015 SUSE Linux GmbH
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
from docmanager.shellcolors import red, green
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
#        self.__xml = [ XmlHandler(x, self.__args.stop_on_error) \
#                       for x in self.__files ]


    def parse(self):
        logmgr_flog()

        action = self.__args.action
        if hasattr(self, action) and getattr(self, action) is not None:
            log.debug("Action.__init__: %s", self.__args)
            return getattr(self, action)(self.__args.properties)
        else:
            log.error("Method \"%s\" is not implemented.", action)
            sys.exit(ReturnCodes.E_METHOD_NOT_IMPLEMENTED)


    def init(self, arguments):
        logmgr_flog()
        log.debug("Arguments %s", arguments)

        _set = dict()
        props = list(DefaultDocManagerProperties)
        validfiles = 0
        invalidfiles = 0

        # append bugtracker properties if needed
        if self.__args.with_bugtracker:
            for item in BugtrackerElementList:
                props.append(item)

        # set default properties
        for item in props:
            rprop = item.replace("/", "_")

            if hasattr(self.__args, rprop) and \
               getattr(self.__args, rprop) is not None:
                _set[item] = getattr(self.__args, rprop)

        # iter through all xml handlers and init its properties
        for xh in self.__xml:
            if not xh.invalidXML:
                validfiles += 1

                log.debug("Trying to initialize the predefined DocManager "
                          "properties for %r.", xh.filename)
                if xh.init_default_props(self.__args.force,
                                         self.__args.with_bugtracker) == 0:
                    print("[{}] Initialized default "
                          "properties for {!r}.".format(green("success"),
                                                        xh.filename))
                else:
                    log.warn("Could not initialize all properties for %r because "
                          "there are already some properties in the XML file "
                          "which would be overwritten after this operation has been "
                          "finished. If you want to perform this operation and "
                          "overwrite the existing properties, you can add the "
                          "'--force' option to your command.", xh.filename)

                # set default values for the given properties
                for i in _set:
                    ret = xh.get(i)
                    if len(ret[i]) == 0 or self.__args.force:
                        xh.set({ i: str(_set[i]) })

                # if bugtracker options are provided, set default values
                for i in BugtrackerElementList:
                    rprop = i.replace("/", "_")

                    if hasattr(self.__args, rprop) and \
                       getattr(self.__args, rprop) is not None and \
                       len(getattr(self.__args, rprop)) >= 1:
                           xh.set({ i: getattr(self.__args, rprop) })

                # safe the xml file
                xh.write()
            else:
                invalidfiles += 1
                print("[{}] Initialized default properties for '{}{}'. ".format(\
                    red("failed"),
                    xh.filename,
                    red(xh.xmlLogErrorString)))

        print("\nInitialized successfully {} files. {} files failed.".format(\
              green(validfiles), red(invalidfiles)))

    def set(self, arguments):
        """Set key/value pairs from arguments

        :param list arguments: List of arguments with key=value pairs
        """
        logmgr_flog()

        invalidfiles = 0
        validfiles = 0

        # init xml handlers for all given files
        handlers = OrderedDict()

        for idx, i in enumerate(self.__files):
            log.debug("Trying to initialize the XmlHandler for file '{}'.".format(i))
            handlers[i] = self.__xml[idx]

            if handlers[i].invalidXML:
                invalidfiles += 1
            else:
                validfiles += 1

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
                        log.debug("[%s] Trying to set value for property "
                                  "%r to %r.", f, key, value)
                        if self.__args.bugtracker:
                            handlers[f].set({"bugtracker/" + key: value})
                        else:
                            handlers[f].set({key: value})
                        print("[{}] Set value for property {!r} to {!r}.".format(f, key, value))

            except ValueError:
                log.error('Invalid usage. '
                          'Set values with the following format: '
                          'property=value')
                sys.exit(ReturnCodes.E_INVALID_USAGE_KEYVAL)

        # save the changes
        for f in self.__files:
            if not handlers[f].invalidXML:
                log.debug("[%s] Trying to save the changes.", f)
                handlers[f].write()
                print("[{}] Saved changes.".format(f))

        print("\nWrote {} valid XML file{}.".format(green(validfiles),
              '' if validfiles == 1 else 's')
             )

        if invalidfiles > 0:
            print("\nSkipped {} XML file{} due to errors.".format(red(invalidfiles),
                  '' if invalidfiles == 1 else 's')
                 )

            for f in self.__files:
                if handlers[f].invalidXML:
                    print("{}: {}".format(f, red(handlers[f].xmlErrorString)))
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

            for arg in arguments:
                prop = ""
                cond = None

                arglist = arg.split("=")
                if len(arglist) == 1:
                    prop = arglist[0]
                else:
                    prop = arglist[0]
                    arglist.pop(0)
                    cond = "".join(arglist)

                log.debug("[%s] Trying to delete property %r.", f, arg)
                handlers[f].delete(prop, cond)
                print("[{}] Property {!r} has been deleted.".format(f, arg))

        for f in self.__files:
            log.debug("[%s] Trying to save the changes.", f)
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