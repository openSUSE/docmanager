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

from lxml import etree

class XmlHandler:

    __namespace = {"d":"http://docbook.org/ns/docbook", "dm":"urn:x-suse:ns:docmanager"}

    def __init__(self, filename):
        #register the namespace
        etree.register_namespace("dm", "{dm}".format(**self.__namespace))
        self.__xmlparser = etree.XMLParser(remove_blank_text=False, resolve_entities=False, dtd_validation=False)
        #load the file and set a reference to the dm group
        self.__tree = etree.parse(filename, self.__xmlparser)
        self.__root = self.__tree.getroot()
        self.indent=""
        self.__docmanager = self.__tree.find("//dm:docmanager", namespaces=self.__namespace)
        if self.__docmanager is None:
            self.create_group()

    def create_group(self):
        #search the info-element if not exists raise an error
        element = self.__tree.find("//d:info", namespaces=self.__namespace)
        if element is not None:
            prev=element.getprevious()
            self.__docmanager = etree.SubElement(element,
                                                 "{{{dm}}}docmanager".format(**self.__namespace),
                                                 )
            self.write()
        else:
            raise NameError("Can't find the info element in %s." %self.filename)

    def set(self, key, value):
        key_handler = self.__docmanager.find("dm:"+key, namespaces=self.__namespace)

        #update the old key or create a new key
        if key_handler is not None:
            key_handler.text = value
        else:
            node = etree.SubElement(self.__docmanager,
                                    "{{{dm}}}{key}".format(key=key, **self.__namespace),
                                    # nsmap=self.__namespace
                                    )
            node.text = value
        self.write()

    def is_set(self, key, values):
        element = self.__docmanager.find("./dm:"+key, namespaces=self.__namespace)
        if element is not None and element.text in values:
            return True
        else:
            return False

    def get(self, keys=None):
        values = {}
        for child in self.__docmanager.iterchildren():
            tag = etree.QName(child)
            #check if we want a selection or all keys
            if keys is not None and "all" not in keys:
                #if the element required?
                if tag.localname in keys:
                    values.update({tag.localname:child.text})
            else:
                values.update({tag.localname:child.text})
        return values

    def delete(self, key):
        key_handler = self.__docmanager.find("./dm:"+key, namespaces=self.__namespace)

        if key_handler is not None:
            key_handler.getparent().remove(key_handler)
            self.write()

    def get_indendation(self, node, indendation=""):
        indent = "".join([ "".join(n.tail.split("\n")) for n in node.iterancestors()
                          if n.tail is not None ])
        return indent+indendation

    def indent_dm(self):
        #
        dmindent='    '
        dm = self.__tree.find("//dm:docmanager",
                              namespaces=self.__namespace)
        info = dm.getparent().getprevious()
        infoindent = "".join(info.tail.split('\n'))
        prev = dm.getprevious()
        previndent = "".join(prev.tail.split('\n'))
        indent=self.get_indendation(dm.getprevious())
        prev.tail = '\n' + infoindent
        dm.text = '\n' + indent + '    '
        dm.tail = '\n' + infoindent
        for node in dm.iterchildren():
            i = dmindent if node.getnext() is not None else ''
            node.tail = '\n' + indent + i

    def write(self):
        # Only indent docmanager child elements
        self.indent_dm()
        self.__tree.write(self.filename,
                          # pretty_print=True,
                          with_tail=True)

    @property
    def filename(self):
        return self.__tree.docinfo.URL
