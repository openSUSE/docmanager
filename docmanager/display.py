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
from collections import OrderedDict
from lxml import etree
from prettytable import PrettyTable

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

    # print only the value of the given property if only one property and
    # only one file are given
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

    index = 0
    for i in data:
        if len(i[1]):
            filename = i[0]
            print("File: {}".format(filename))
            t = PrettyTable(["Property", "Value"])
            t.align["Property"] = "l" # left align
            t.align["Value"] = "l" # left align

            for prop in i[1]:
                value = i[1][prop]
                t.add_row([prop, value])

            print(t)
            if (len(data)-1) is not index:
                print("")

        index += 1


def jsonrenderer(data, **kwargs): # pylint: disable=unused-argument
    """Output as JSON

    :param list data: Filename with properties
                      syntax: [(FILENAME, {PROPERTIES}), ...]
    :param dict kwargs: for further customizations
    :return: rendered output
    :rtype: str
    """
    json_out = OrderedDict()
    for i in data:
        json_out[i[0]] = {}
        json_out[i[0]] = i[1]
    
    print(json.dumps(json_out))


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
    
    fileselem = etree.Element("files")
    root.append(fileselem)

    index = 0

    for i in data:
        if len(i[1]):
            filename = i[0]

            elem = etree.Element("file")
            root[0].append(elem)

            child = root[0][index]
            child.set("name", filename)

            for x in i[1]:
                prop = x
                value = i[1][x]

                elem = etree.Element(prop)
                elem.text = value

                child.append(elem)

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