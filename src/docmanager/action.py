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
import threading
from collections import OrderedDict, namedtuple
from configparser import ConfigParser, NoOptionError
from docmanager.analyzer import Analyzer
from docmanager.config import GLOBAL_CONFIG, USER_CONFIG, GIT_CONFIG
from docmanager.core import DEFAULT_DM_PROPERTIES, ReturnCodes, BT_ELEMENTLIST
from docmanager.exceptions import *
from docmanager.logmanager import log, logmgr_flog
from docmanager.shellcolors import red, green, yellow
from docmanager.xmlhandler import XmlHandler
from docmanager.display import print_stats
from math import trunc
from multiprocessing.pool import ThreadPool


class Actions(object):
    """An Actions instance represents an action event
    """

    def __init__(self, args):
        """Initialize Actions class

        :param argparse.Namespace args: result from argparse.parse_args
        """
        logmgr_flog()

        # set default variables
        self.__files = args.files
        self.__args = args
        self.__xml = OrderedDict()

        # set the default output format for 'alias' sub cmd to 'table'
        if args.action == "alias":
            args.format = "table"

        if self.__files:
            # temporary xml handler list
            xml = list()

            # start multiple processes for initialize all XML files
            with ThreadPool(processes=self.__args.jobs) as pool:
                for i in pool.map(self.init_xml_handlers, self.__files):
                    xml.append(i)

            # build the self.__xml dict
            for i in xml:
                name = i["file"]
                self.__xml[name] = dict()

                for x in i:
                    if x is not "file":
                        self.__xml[name][x] = i[x]

                # stop if we found an error and --stop-on-error is set
                if self.__args.stop_on_error and "error" in self.__xml[name]:
                    log.error("{}: {}".format(name, self.__xml[name]["errorstr"]))
                    sys.exit(self.__xml[name]["error"])

    def init_xml_handlers(self, fname):
        """
        Initializes an XmlHandler for a file.

        :param string fname: The file name
        """
        handler = None

        try:
            handler = { "file": fname, "handler": XmlHandler(fname, True) }
        except (DMXmlParseError, DMInvalidXMLRootElement, DMFileNotFoundError, DMNotDocBook5File) as err:
            handler = { "file": fname, "errorstr": err.errorstr, "error": err.error }

        return handler

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

        _set = dict()
        props = list(DEFAULT_DM_PROPERTIES)

        # count all valid and invalid xml files
        validfiles, invalidfiles = self.get_files_status(self.__xml)

        # append bugtracker properties if needed
        if self.__args.with_bugtracker:
            for item in BT_ELEMENTLIST:
                props.append(item)

        # set default properties
        for item in props:
            rprop = item.replace("/", "_")

            if hasattr(self.__args, rprop) and \
               getattr(self.__args, rprop) is not None:
                _set[item] = getattr(self.__args, rprop)

        # iter through all xml handlers and init its properties
        for f in self.__files:
            if "error" not in self.__xml[f]:
                xh = self.__xml[f]["handler"]

                log.info("Trying to initialize the predefined DocManager "
                          "properties for %r.", xh.filename)

                if xh.init_default_props(self.__args.force,
                                         self.__args.with_bugtracker) == 0:
                    print("[{}] Initialized default "
                          "properties for {!r}.".format(green(" ok "),
                                                        xh.filename))
                else:
                    log.warning("Could not initialize all properties for %r because "
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
                for i in BT_ELEMENTLIST:
                    rprop = i.replace("/", "_")

                    if hasattr(self.__args, rprop) and \
                       getattr(self.__args, rprop) is not None and \
                       len(getattr(self.__args, rprop)) >= 1:
                        xh.set({ i: getattr(self.__args, rprop) })
            else:
                print("[{}] Initialized default properties for {!r}: {}. ".format(\
                    red(" error "),
                    f,
                    red(self.__xml[f]["errorstr"])))

        # save the changes
        if validfiles:
            for f in self.__files:
                if "error" not in self.__xml[f]:
                    self.__xml[f]["handler"].write()

        # print the statistics
        print("\nInitialized successfully {} files. {} files failed.".format(\
              green(validfiles), red(invalidfiles)))

    def set(self, arguments):
        """Set key/value pairs from arguments

        :param list arguments: List of arguments with key=value pairs
        """
        logmgr_flog()

        # count all valid and invalid xml files
        validfiles, invalidfiles = self.get_files_status(self.__xml)

        # split key and value
        args = [i.split("=") for i in arguments]

        # iter through all key and values
        for f in self.__files:
            if "error" in self.__xml[f]:
                print("[ {} ] {} -> {}".format(red("error"), f, red(self.__xml[f]['errorstr'])))
            else:
                for arg in args:
                    try:
                        key, value = arg

                        if key == "languages":
                            value = value.split(",")
                            value = ",".join(self.remove_duplicate_langcodes(value))

                        log.debug("[%s] Trying to set value for property "
                                  "%r to %r.", f, key, value)

                        if self.__args.bugtracker:
                            self.__xml[f]["handler"].set({"bugtracker/" + key: value})
                        else:
                            self.__xml[f]["handler"].set({key: value})
                    except ValueError:
                        log.error('Invalid usage. '
                                  'Set values with the following format: '
                                  'property=value')
                        sys.exit(ReturnCodes.E_INVALID_USAGE_KEYVAL)

                print("[ {} ] Set data for file {}.".format(green("ok"), f))

        # save the changes
        for f in self.__files:
            if "error" not in self.__xml[f]:
                log.debug("[%s] Trying to save the changes.", f)
                self.__xml[f]["handler"].write()

        print_stats(validfiles, invalidfiles)


    def set_attr(self, arguments):
        prop = self.__args.property
        attrs = self.__args.attributes

        if not prop:
            log.error("You must specify a property with -p!")
            sys.exit(ReturnCodes.E_INVALID_ARGUMENTS)

        if not attrs:
            log.error("You must specify at least one attribute with -a!")
            sys.exit(ReturnCodes.E_INVALID_ARGUMENTS)

        # count all valid and invalid xml files
        validfiles, invalidfiles = self.get_files_status(self.__xml)

        data = OrderedDict()
        for i in attrs:
            try:
                key, val = i.split("=")
                data[key] = val
            except ValueError:
                log.error("The values of -a must have a key and a value, like: key=value or key=")
                sys.exit(ReturnCodes.E_INVALID_USAGE_KEYVAL)

        for f in self.__files:
            if "error" in self.__xml[f]:
                print("[{}] {} -> {}".format(red(" error "), f, red(self.__xml[f]["errorstr"])))
            else:
                try:
                    self.__xml[f]["handler"].set_attr(prop, data)
                    self.__xml[f]["handler"].write()

                    print("[{}] Set attributes for file {}.".format(green(" ok "), f))
                except DMPropertyNotFound:
                    print("[{}] Property {} was not found in {}.".format(red(" error "), yellow(prop), f))

                    # we must substract 1 of "validfiles" since XML files are valid even
                    # if they don't have the given property.
                    validfiles -= 1
                    invalidfiles += 1

        print_stats(validfiles, invalidfiles)


    def del_attr(self, arguments):
        prop = self.__args.property
        attrs = self.__args.attributes

        if not prop:
            log.error("You must specify a property with -p!")
            sys.exit(ReturnCodes.E_INVALID_ARGUMENTS)

        if not attrs:
            log.error("You must specify at least one attribute with -a!")
            sys.exit(ReturnCodes.E_INVALID_ARGUMENTS)

        # count all valid and invalid xml files
        validfiles, invalidfiles = self.get_files_status(self.__xml)

        for f in self.__files:
            if "error" in self.__xml[f]:
                print("[{}] {} -> {}".format(red(" error "), f, red(self.__xml[f]["errorstr"])))
            else:
                try:
                    errors = self.__xml[f]["handler"].del_attr(prop, attrs)
                    self.__xml[f]["handler"].write()

                    if errors:
                        print("[{}] These attributes couldn't be deleted for {}: {}".format(
                            yellow(" notice "), f, ", ".join(errors)
                        ))
                    else:
                        print("[{}] Deleted attributes for file {}.".format(green(" ok "), f))

                except DMPropertyNotFound:
                    print("[{}] Property {} was not found in {}.".format(red(" error "), yellow(prop), f))

                    # we must substract 1 of "validfiles" since XML files are valid even
                    # if they don't have the given property.
                    validfiles -= 1
                    invalidfiles += 1

        print_stats(validfiles,invalidfiles)


    def get_attr(self, arguments):
        props = self.__args.properties
        attrs = self.__args.attributes

        data = dict(data=OrderedDict(),errors=None)

        for f in self.__files:
            data['data'][f] = self.__xml[f]["handler"].get_attr(props, attrs)

        return data

    def get(self, arguments):
        """Lists all properties

        :param list arguments:
        :return: [(FILENAME, {PROPERTIES}), ...]
        :rtype: list
        """
        logmgr_flog()

        output = list()
        errors = list()

        for f in self.__files:
            if "error" in self.__xml[f]:
                errors.append([f, self.__xml[f]['errorstr']])
            else:
                output.append((f, self.__xml[f]["handler"].get(arguments)))

        return {'data': output, 'errors': errors}


    def delete(self, arguments):
        """Delete a property

        :param list arguments:
        """
        logmgr_flog()

        # statistics variables
        file_errors = 0
        props_failed = 0
        props_deleted = 0

        # delete the properties
        for f in self.__files:
            if "error" in self.__xml[f]:
                print("[{}] {} -> {}".format(red(" error "), f, red(self.__xml[f]["errorstr"])))
                file_errors += 1
            else:
                failed_properties = list()

                for arg in arguments:
                    cond = None
                    prop = arg
                    pos = arg.find("=")

                    # look if there is condition
                    if pos != -1:
                        prop = arg[:pos]
                        cond = arg[pos+1:]

                    if not self.__xml[f]["handler"].delete(prop, cond):
                        failed_properties.append(arg)
                        props_failed += 1
                    else:
                        props_deleted += 1

                if not failed_properties:
                    print("[{}] {}".format(green(" ok "), f))
                else:
                    print("[{}] {} -> Couldn't delete these properties: {}".format(
                          yellow(" info "), f, ", ".join(failed_properties)
                         ))

        # save changes
        for f in self.__files:
            if "error" not in self.__xml[f]:
                self.__xml[f]["handler"].write()

        # print statistics
        print("")
        print("Deleted successfully {} propert{}, {} propert{} couldn't be deleted, and {} {} invalid.".format(
                green(props_deleted), 'ies' if props_deleted != 1 else 'y',
                yellow(props_failed), 'ies' if props_failed != 1 else 'y', red(file_errors),
                'files were' if file_errors != 1 else 'file was'
             ))

    def analyze(self, arguments): # pylint:disable=unused-argument
        handlers = dict()

        # Set default query format
        try:
            qformat = self.args.config['analzye']['queryformat']
        except KeyError:
            pass

        if self.args.queryformat:
            qformat = self.args.queryformat

        file_data = list()
        errors = list()
        ntfiledata = namedtuple("FileData", "file,out_formatted,data")
        validfiles, invalidfiles = self.get_files_status(self.__xml)

        for f in self.__files:
            if "error" in self.__xml[f]:
                errors.append("Error in '{}': {}".format(f, red(self.__xml[f]["errorstr"])))
            else:
                try:
                    analyzer = Analyzer(self.__xml[f]["handler"])
                except DMInvalidXMLHandlerObject:
                    log.critical("XML Handler object is None.")

                out = qformat[:]
                out = analyzer.replace_constants(out)
                fields = analyzer.extract_fields(out)
                data = analyzer.fetch_data(self.__args.filter, self.__args.sort, self.__args.default_output)

                if not self.__args.sort:
                    # we can print all caught data here. If we have no data, we assume that the user
                    # didn't want to see any data from the XML files and he just want to see the
                    # output of the constants like {os.file} - https://github.com/openSUSE/docmanager/issues/93
                    if data:
                        print(analyzer.format_output(out, data))
                    elif analyzer.filters_matched:
                        print(analyzer.format_output(out, data))
                else:
                    file_data.append(ntfiledata(file=f, out_formatted=out, data=data))

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

            if values:
                for i in values:
                    print(analyzer.format_output(i.out_formatted, i.data))

        if not self.__args.quiet:
            print("\nSuccessfully analyzed {} XML files.".format(green(validfiles)))

        if errors and not self.__args.quiet:
            print("Got {} errors in the analyzed files:\n".format(red(len(errors))))
            for i in errors:
                print(i)

    def _readconfig(self, confname):
        """Read the configuration file

        :param str confname: name of configuration file
        :return: ConfigParser object
        """

        # exit if the config file is a directory
        if os.path.isdir(confname):
            log.error("File '{}' is a directory. Cannot write "
                      "into directories!".format(confname))
            sys.exit(ReturnCodes.E_FILE_IS_DIRECTORY)

        # open the config file with the ConfigParser
        conf = ConfigParser()
        if not conf.read(confname):
            if os.path.exists(confname):
                log.error("Permission denied for file '{}'! "
                          "Maybe you need sudo rights?".format(confname))
                sys.exit(ReturnCodes.E_PERMISSION_DENIED)
        return conf

    def config(self, values): # pylint:disable=unused-argument
        if not self.__args.system and not self.__args.user and not self.__args.repo and not self.__args.own:
            log.error("No config file specified. Please choice between either '--system', '--user', '--repo', or '--own'.")
            sys.exit(ReturnCodes.E_CONFIGCMD_NO_METHOD_SPECIFIED)

        prop = self.__args.property
        value = self.__args.value

        # search for the section, the property and the value
        pos = prop.find(".")
        if pos == -1:
            log.error("Invalid property syntax. Use: section.property")
            sys.exit(ReturnCodes.E_INVALID_CONFIG_PROPERTY_SYNTAX)

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
        conf = self._readconfig(confname)

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
                # 'x' for creating and writing to a new file
                conf.write(open(confname, 'x')) # pylint:disable=bad-open-mode
            else:
                conf.write(open(confname, 'w'))
        except PermissionError: # pylint:disable=undefined-variable
            log.error("Permission denied for file '{}'! "
                      "Maybe you need sudo rights?".format(confname))
            sys.exit(ReturnCodes.E_PERMISSION_DENIED)

    def alias(self, values):
        action = self.__args.alias_action
        alias = self.__args.alias
        value = self.__args.command
        m = { 0: None, 1: GLOBAL_CONFIG[0], 2: USER_CONFIG, 3: GIT_CONFIG }
        configname = m.get(self.__args.method, self.__args.own)
        save = False

        if action != 'list':
            if alias is None and value is None:
                log.error("You have to provide an alias name for method '{}'.".format(action))
                sys.exit(ReturnCodes.E_INVALID_ARGUMENTS)

        if not value:
            value = ""

        # parse the config file
        conf = self._readconfig(configname)

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
        elif action == "list":
            data = dict()
            data["configfile"] = configname
            data["aliases"] = conf['alias']

            return data

        # save the changes
        if save:
            try:
                if not os.path.exists(configname):
                    log.error("The config file does not exists.")
                    sys.exit(ReturnCodes.E_FILE_NOT_FOUND)

                conf.write(open(configname, 'w'))
            except PermissionError:
                log.error("Permission denied for file '{}'! "
                          "Maybe you need sudo rights?".format(configname))
                sys.exit(ReturnCodes.E_PERMISSION_DENIED)

    def remove_duplicate_langcodes(self, values):
        new_list = []
        for i in values:
            if i not in new_list:
                new_list.append(i)

        return new_list


    def get_files_status(self, handlers):
        """Count all valid and invalid XML files

        :param dict handlers: The self.__xml object with all XML handlers
        """
        validfiles = 0
        invalidfiles = 0

        for i in self.__files:
            if "error" in handlers[i]:
                invalidfiles += 1
            else:
                validfiles += 1

        return [validfiles, invalidfiles]

    @property
    def args(self):
        return self.__args
