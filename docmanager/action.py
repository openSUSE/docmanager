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

import os.path
import sys
from collections import OrderedDict, namedtuple
from configparser import ConfigParser, NoOptionError
from docmanager.analyzer import Analyzer
from docmanager.config import GLOBAL_CONFIG, USER_CONFIG, GIT_CONFIG
from docmanager.core import DefaultDocManagerProperties, ReturnCodes, BugtrackerElementList, NS
from docmanager.exceptions import DMInvalidXMLHandlerObject
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

        if self.__files:
            if hasattr(self.__args, 'stop_on_error'):
                self.__xml = [ XmlHandler(x, self.__args.stop_on_error) for x in self.__files ]
            else:
                self.__xml = [ XmlHandler(x) for x in self.__files ]

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
                print("[{}] Initialized default properties for {!r}: {}. ".format(\
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
            props_success = list()
            props_failed = list()

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
                if handlers[f].delete(prop, cond) is True:
                    props_success.append(prop)
                else:
                    props_failed.append(prop)

            props_success_c = len(props_success)
            props_failed_c = len(props_failed)

            if props_success_c == 1:
                props_str = "property has been deleted"
            else:
                props_str = "properties have been deleted"

            print("[{}] {} {} and {} could not be deleted.".format(f, green(props_success_c), props_str, red(props_failed_c)))
            if props_success_c > 0:
                print("  - [{}] {}".format(green("success"), ", ".join(props_success)))

            if props_failed_c > 0:
                print("  - [{}] {}".format(red("failed"), ", ".join(props_failed)))

        for f in self.__files:
            log.debug("[%s] Trying to save the changes.", f)
            handlers[f].write()

    def analyze(self, arguments):
        handlers = dict()

        # Set default query format
        try:
            qformat = self.args.config['analzye']['querformat']
        except KeyError:
            pass
        if self.args.queryformat:
            qformat = self.args.queryformat

        file_data = list()
        NTFILEDATA = namedtuple("FileData", "file,out_formatted,data")

        for f in self.__files:
            handlers[f] = XmlHandler(f)

            try:
                analyzer = Analyzer(handlers[f])
            except DMInvalidXMLHandlerObject:
                log.critical("XML Handler object is None.")

            out = qformat[:]
            out = analyzer.replace_constants(out)
            fields = analyzer.extract_fields(out)
            data = analyzer.fetch_data(self.__args.filter, self.__args.sort, self.__args.default_output)

            if not self.__args.sort and data:
                print(analyzer.format_output(out, data))
            else:
                file_data.append(NTFILEDATA(file=f, out_formatted=out, data=data))

        if self.__args.sort:
            values = None

            if self.__args.sort == 'filename':
                values = sorted(file_data, key=lambda x: x.file)
            else:
                try:
                    values = sorted(file_data, key=lambda x: int(x.data[self.__args.sort]) \
                        if x.data[self.__args.sort].isnumeric() \
                        else \
                        x.data[self.__args.sort])
                except KeyError:
                    log.error("Could not find key '{}' in -qf for sort.")
            
            for i in values:
                print(analyzer.format_output(i.out_formatted, i.data))

    def config(self, values):
        if not self.__args.system and not self.__args.user and not self.__args.repo and not self.__args.own:
            log.error("No config file specified. Please choice between either '--system', '--user', '--repo', or '--own'.")
            sys.exit(ReturnCodes().E_CONFIGCMD_NO_METHOD_SPECIFIED)

        prop = self.__args.property
        value = self.__args.value

        # search for the section, the property and the value
        pos = prop.find(".")
        if pos == -1:
            log.error("Invalid property syntax. Use: section.property")
            sys.exit(ReturnCodes().E_INVALID_CONFIG_PROPERTY_SYNTAX)

        section = prop[:pos]
        prop = prop[pos+1:]

        confname = None

        # determine config file
        if self.__args.system:
            confname = GLOBAL_CONFIG[0]
        elif self.__args.user:
            confname = USER_CONFIG
        elif self.__args.repo:
            confname = GIT_CONFIG
        elif self.__args.own:
            confname = self.__args.own

        # open the config file with the ConfigParser
        conf = ConfigParser()
        if not conf.read(confname):
            if os.path.exists(confname):
                log.error("Permission denied for file '{}'! "
                          "Maybe you need sudo rights?".format(confname))
                sys.exit(ReturnCodes().E_PERMISSION_DENIED)

        # handle the 'get' method
        if value is None:
            if conf.has_section(section):
                try:
                    print(conf.get(section, prop))
                except NoOptionError:
                    pass

            sys.exit(ReturnCodes.E_OK)

        # add the section if its not available
        if not conf.has_section(section):
            conf.add_section(section)

        # set the property
        conf.set(section, prop, value)

        # save the changes
        try:
            if not os.path.exists(confname):
                conf.write(open(confname, 'x'))
            else:
                conf.write(open(confname, 'w'))
        except PermissionError:
            log.error("Permission denied for file '{}'! "
                      "Maybe you need sudo rights?".format(confname))
            sys.exit(ReturnCodes().E_PERMISSION_DENIED)

    def alias(self, values):
        action = self.__args.alias_action
        alias = self.__args.alias
        value = self.__args.command
        m = { 0: None, 1: GLOBAL_CONFIG[0], 2: USER_CONFIG, 3: GIT_CONFIG }
        config = m.get(self.__args.method, self.__args.own)
        save = False

        if not value:
            value = ""

        # parse the config file
        conf = ConfigParser()
        if not conf.read(config):
            if os.path.exists(config):
                log.error("Permission denied for file '{}'! "
                          "Maybe you need sudo rights?".format(config))
                sys.exit(ReturnCodes().E_PERMISSION_DENIED)

        # exit if the config file is a directory
        if os.path.isdir(config):
            log.error("File '{}' is a directory. Cannot write "
                      "into directories!".format(config))
            sys.exit(ReturnCodes().E_FILE_IS_DIRECTORY)

        # add alias section if it's not found
        if not conf.has_section("alias"):
            conf.add_section("alias")

        # handle actions
        if action == "set":
            conf.set("alias", alias, value)
            save = True
        elif action == "get":
            try:
                print(conf.get("alias", alias))
            except NoOptionError:
                pass
        elif action == "del":
            save = True
            conf.remove_option("alias", alias)

        # save the changes
        if save:
            try:
                if not os.path.exists(config):
                    log.error("The config file does not exists.")
                    sys.exit(ReturnCodes().E_FILE_NOT_FOUND)
                
                conf.write(open(config, 'w'))
            except PermissionError:
                log.error("Permission denied for file '{}'! "
                          "Maybe you need sudo rights?".format(config))
                sys.exit(ReturnCodes().E_PERMISSION_DENIED)

    def remove_duplicate_langcodes(self, values):
        new_list = []
        for i in values:
            if i not in new_list:
                new_list.append(i)

        return new_list

    @property
    def args(self):
        return self.__args
