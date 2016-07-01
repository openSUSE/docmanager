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

import json
import sys
from collections import OrderedDict
from lxml import etree
from prettytable import PrettyTable
from docmanager.core import ReturnCodes
from docmanager.shellcolors import red,green

def textrenderer(data, **kwargs): # pylint: disable=unused-argument
    """Normal text output

    :param list data: Filename with properties
                      syntax: [(FILENAME, {PROPERTIES}), ...]
    :param dict kwargs: for further customizations
    :return: rendered output
    :rtype: str
    """

    if data is None:
        return

    args = kwargs["args"]

    if args.action == "get":
        # print only the value of the given property if only one property and
        # only one file are given
        errors = data['errors']
        data = data['data']

        if len(data) == 1:
            if len(data[0][1]) == 1:
                for v in data[0][1]:
                    if data[0][1][v] is not None:
                        print(data[0][1][v])
                    return

        # if there are more than one file or one property
        for d in data:
            props = d[1]
            props = " ".join(["%s=%s" % (key, value) \
                              for key, value in props.items()])
            if len(props):
                print("{} -> {}".format(d[0], props))

        # print all errors if -q/--quiet is not set
        if errors and not args.quiet:
            print("")

            for i in errors:
                print("[{}] {} -> {}".format(red(" error "), i[0], i[1]))
    elif args.action == "get_attr":
        errors = data['errors']
        data = data['data']

        if data:
            for i in data:
                if data[i]:
                    for prop in data[i]:
                        if data[i][prop]:
                            print("{}[{}] -> {}".format(i, prop, ", ".join(["%s=%s" % (key, value) \
                                                          for key, value in data[i][prop].items()])))

def tablerenderer(data, **kwargs): # pylint: disable=unused-argument
    """Output as table

    :param list data: Filename with properties
                      syntax: [(FILENAME, {PROPERTIES}), ...]
    :param dict kwargs: for further customizations
    :return: rendered output
    :rtype: str
    """
    if data is None:
        return

    args = kwargs["args"]

    if args.action == "alias":
        if len(data['aliases']) == 0:
            print("There are no aliases in config file: {}".format(data["configfile"]))
        else:
            table = PrettyTable(["Alias", "Command"])
            table.align["Alias"] = "l" # left align
            table.align["Command"] = "l" # left align

            for i in data['aliases']:
                table.add_row([i, data['aliases'][i]])

            print(table)
    elif args.action == "get":
        index = 0
        for i in data['data']:
            if len(i[1]):
                filename = i[0]
                print("File: {}".format(filename))
                table = PrettyTable(["Property", "Value"])
                table.align["Property"] = "l" # left align
                table.align["Value"] = "l" # left align

                for prop in i[1]:
                    value = i[1][prop]
                    table.add_row([prop, value])

                print(table)
                if (len(data)-1) is not index:
                    print("")

            index += 1
    elif args.action == "get_attr":
        if data['data']:
            # file names
            for f in data['data']:
                if data['data'][f]:
                    print("File: {}".format(f))

                    table = PrettyTable(["Property", "Attribute", "Value"])
                    table.align["Property"] = "1"
                    table.align["Attribute"] = "1"
                    table.align["Value"] = "1"

                    # properties
                    for prop in data['data'][f]:
                        # attributes
                        for i in data['data'][f][prop]:
                            table.add_row([prop, i, data['data'][f][prop][i]])

                    print(table)


def jsonrenderer(data, **kwargs): # pylint: disable=unused-argument
    """Output as JSON

    :param list data: Filename with properties
                      syntax: [(FILENAME, {PROPERTIES}), ...]
    :param dict kwargs: for further customizations
    :return: rendered output
    :rtype: str
    """

    args = kwargs["args"]

    if args.action == "alias":
        json_out = OrderedDict()
        for i in data['aliases'].keys():
            json_out[i] = {}
            json_out[i] = data['aliases'][i]

        print(json.dumps(json_out))
    elif args.action == "get":
        json_out = OrderedDict()
        for i in data['data']:
            json_out[i[0]] = {}
            json_out[i[0]] = i[1]

        print(json.dumps(json_out))
    elif args.action == "get_attr":
        json_out = OrderedDict()
        data = data['data']

        print(json.dumps(data))

def xmlrenderer(data, **kwargs): # pylint: disable=unused-argument
    """Output as XML

    :param list data: Filename with properties
                      syntax: [(FILENAME, {PROPERTIES}), ...]
    :param dict kwargs: for further customizations
    :return: rendered output
    :rtype: str
    """

    root = etree.Element("docmanager")
    tree = root.getroottree()

    args = kwargs["args"]
    index = 0

    if args.action == "alias":
        aliaseselem = etree.Element("aliases")
        root.append(aliaseselem)

        for name in data['aliases'].keys():
            value = data['aliases'][name]

            root[0].append(etree.Element("alias"))

            child = root[0][index]
            child.set("name", name)

            child.text = value

            index += 1

    elif args.action == "get":
        fileselem = etree.Element("files")
        root.append(fileselem)

        for i in data['data']:
            if len(i[1]):
                filename = i[0]

                root[0].append(etree.Element("file"))

                child = root[0][index]
                child.set("name", filename)

                for x in i[1]:
                    prop = x
                    value = i[1][x]

                    elem = etree.Element("property")
                    elem.set("name", prop)
                    elem.text = value

                    child.append(elem)

                index += 1

    elif args.action == "get_attr":
        """
        Output structure:
        <!DOCTYPE docmanager>
        <docmanager>
          <files>
            <file name="example.xml">
              <property name="priority/test/hello">
                <attribute name="someattribute">Hello</attribute>
                <attribute name="attr2">Hallo</attribute>
              </property>
              <property name="status">
                <attribute name="attr3">Hi</attribute>
              </property>
            </file>
          </files>
        </docmanager>
        """

        fileselem = etree.Element("files")
        root.append(fileselem)

        if data['data']:
            index = 0

            for i in data['data']:
                filename = i
                root[0].append(etree.Element("file"))

                child = root[0][index]
                child.set("name", filename)

                for prop in data['data'][i]:
                    propelem = etree.Element("property")
                    child.append(propelem)
                    propelem.set("name", prop)

                    for key, value in data['data'][i][prop].items():
                        elem = etree.Element("attribute")
                        elem.set("name", key)
                        elem.text = value

                        propelem.append(elem)

                    index += 1

    print(etree.tostring(tree,
                         encoding="unicode",
                         pretty_print=True,
                         doctype="<!DOCTYPE docmanager>"))


DEFAULTRENDERER = textrenderer

def getrenderer(fmt):
    """Returns the renderer for a specific format

    :param str fmt: format ('text', 'table', 'json', or 'default')
    :return: function of renderer
    :rtype: function
    """
    # Available renderers
    renderer = {
        'default': textrenderer,
        'text':    textrenderer,
        'table':   tablerenderer,
        'json':    jsonrenderer,
        'xml':     xmlrenderer,
    }

    return renderer.get(fmt, DEFAULTRENDERER)


def print_stats(validfiles, invalidfiles):
    """Print statistics how many files were valid/invalid, do a sys.exit
    if there were invalid files.

    :param int validfiles: The number of valid files
    :param int invalidfiles: The number of invalid files
    """

    message = "\n"
    if validfiles > 0:
        message += "Wrote {} valid XML file{}. ".format(
            green(validfiles),
            '' if validfiles == 1 else 's'
            )
    if invalidfiles > 0:
        message += "Skipped {} XML file{} due to errors.".format(
            red(invalidfiles),
            '' if invalidfiles == 1 else 's'
            )

    print(message)

    if invalidfiles > 0:
        sys.exit(ReturnCodes.E_SOME_FILES_WERE_INVALID)
