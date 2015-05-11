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

import re

from docmanager.logmanager import log, logmgr_flog
from docmanager.core import NS
from lxml import etree


def localname(tag):
    """Returns the local name of an element

    :param str tag: Usually in the form of {http://docbook.org/ns/docbook}article
    :return:  local name
    :rtype:  str
    """
    m = re.search("\{(?P<ns>.*)\}(?P<local>[a-z]+)", tag)
    if m:
        return m.groupdict()['local']
    else:
        return tag


class XmlHandler(object):
    """An XmlHandler instance represents an XML tree of a file
    """
    __namespace = {"d":"http://docbook.org/ns/docbook", "dm":"urn:x-suse:ns:docmanager"}
    # All elements which are valid as root (from 5.1CR3)
    validroots = ('abstract', 'address', 'annotation', 'audiodata',
                   'audioobject', 'bibliodiv', 'bibliography', 'bibliolist',
                   'bibliolist', 'blockquote', 'book', 'calloutlist',
                   'calloutlist', 'caption', 'caution', 'classsynopsis',
                   'classsynopsisinfo', 'cmdsynopsis', 'cmdsynopsis', 'components',
                   'constraintdef', 'constructorsynopsis', 'destructorsynopsis',
                   'epigraph', 'equation', 'equation', 'example', 'fieldsynopsis',
                   'figure', 'formalpara', 'funcsynopsis', 'funcsynopsisinfo',
                   'glossary', 'glossary', 'glossdiv', 'glosslist', 'glosslist',
                   'imagedata', 'imageobject', 'imageobjectco', 'imageobjectco',
                   'important', 'index', 'indexdiv', 'informalequation',
                   'informalequation', 'informalexample', 'informalfigure',
                   'informaltable', 'inlinemediaobject', 'itemizedlist', 'legalnotice',
                   'literallayout', 'mediaobject', 'methodsynopsis', 'msg', 'msgexplan',
                   'msgmain', 'msgrel', 'msgset', 'msgsub', 'note', 'orderedlist',
                   'para', 'part', 'partintro', 'personblurb', 'procedure',
                   'productionset', 'programlisting', 'programlistingco',
                   'programlistingco', 'qandadiv', 'qandaentry', 'qandaset',
                   'qandaset', 'refentry', 'refsect1', 'refsect2', 'refsect3',
                   'refsection', 'refsynopsisdiv', 'revhistory', 'screen', 'screenco',
                   'screenco', 'screenshot', 'sect1', 'sect2', 'sect3', 'sect4', 'sect5',
                   'section', 'segmentedlist', 'set', 'set', 'setindex', 'sidebar',
                   'simpara', 'simplelist', 'simplesect', 'step', 'stepalternatives',
                   'synopsis', 'table', 'task', 'taskprerequisites', 'taskrelated',
                   'tasksummary', 'textdata', 'textobject', 'tip', 'toc', 'tocdiv',
                   'topic', 'variablelist', 'videodata', 'videoobject', 'warning')

    def __init__(self, filename):
        """Initializes the XmlHandler class

        :param str filename: filename of XML file
        """
        logmgr_flog()
        #register the namespace
        etree.register_namespace("dm", "{dm}".format(**self.__namespace))
        self.__xmlparser = etree.XMLParser(remove_blank_text=False,
                                           resolve_entities=False,
                                           dtd_validation=False)
        #load the file and set a reference to the dm group
        self.__tree = etree.parse(filename, self.__xmlparser)
        self.__root = self.__tree.getroot()
        self.__docmanager = self.__tree.find("//dm:docmanager",
                                             namespaces=self.__namespace)
        if self.__docmanager is None:
            self.create_group()

    def check_root_element(self):
        """Checks if root element is valid"""
        if self._root.tag not in self.validroots:
            raise ValueError("Cannot add info element to %s. "
                             "Not a valid root element." % self._root.tag)

    def create_group(self):
        """Creates the docmanager group element"""
        logmgr_flog()

        #search the info-element if not exists raise an error
        element = self.__tree.find("//d:info", namespaces=self.__namespace)
        # TODO: We need to check for a --force option
        if element is None:
            log.warn("Can't find the <info> element in '%s'. "
                     "Adding one." % self.__tree.docinfo.URL)
            title = self.__root.getchildren()[0]
            idx = self.__root.index(title) + 1
            self.__root.insert(idx, etree.Element("{%s}info" % NS["d"]))
            element = self.__root.getchildren()[idx]
            element.tail = self.__root.getchildren()[idx-1].tail

        self.__docmanager = etree.SubElement(element,
                                             "{{{dm}}}docmanager".format(**self.__namespace),
                                            )
        #log.debug("docmanager?: %s" % etree.tostring(self.__tree).decode("UTF-8"))
        self.write()

    def set(self, key, value):
        """Sets the key as element and value as content

           :param key:    name of the element
           :param value:  value that this element will contain

           If key="foo" and value="bar" you will get:
            <foo>bar</foo>
           whereas foo belongs to the DocManager namespace
        """
        logmgr_flog()
        key_handler = self.__docmanager.find("./dm:"+key,
                                             namespaces=self.__namespace)
        #update the old key or create a new key
        if key_handler is not None:
            key_handler.text = value
        else:
            node = etree.SubElement(self.__docmanager,
                                    "{{{dm}}}{key}".format(key=key,
                                                           **self.__namespace),
                                    # nsmap=self.__namespace
                                    )
            node.text = value
        self.write()

    def is_set(self, key, values):
        """Checks if element 'key' exists with 'values'

        :param str key: the element to search for
        :param str values: the value inside the element

        :return: if conditions are met
        :rtype: bool
        """
        logmgr_flog()

        #check if the key has on of the given values
        element = self.__docmanager.find("./dm:"+key,
                                         namespaces=self.__namespace)
        if element is not None and element.text in values:
            return True
        else:
            return False


    def get(self, keys=None):
        """Returns all matching values for a key in docmanager element

        :param key: localname of element to search for
        :type key: list, tuple, or None
        :return: the values
        :rtype: dict
        """
        logmgr_flog()

        values = {}
        for child in self.__docmanager.iterchildren():
            tag = etree.QName(child)
            #check if we want a selection or all keys
            if keys is not None:
                #if the element required?
                if tag.localname in keys:
                    values.update({tag.localname:child.text})
            else:
                values.update({tag.localname:child.text})

        return values

    def get_all(self):
        """Returns all keys and values in a docmanager xml file
        """

        ret = dict()
        for i in self.__docmanager.iterchildren():
            ret[i.tag] = i.text

        return ret

    def delete(self, key):
        """Deletes an element inside docmanager element

        :param str key: element name to delete
        """
        logmgr_flog()
        key_handler = self.__docmanager.find("./dm:"+key,
                                             namespaces=self.__namespace)

        if key_handler is not None:
            key_handler.getparent().remove(key_handler)
            self.write()

    def get_indendation(self, node, indendation=""):
        """Calculates indendation level

        :param lxml.etree._Element node: node where to start
        :param str indendation: Additional indendation
        """
        indent = ""
        if node is not None:
            indent = "".join(["".join(n.tail.split("\n"))
                          for n in node.iterancestors()
                            if n.tail is not None ])
        return indent+indendation

    def indent_dm(self):
        """Indents only dm:docmanager element and its children"""
        dmindent='    '
        dm = self.__tree.find("//dm:docmanager",
                              namespaces=self.__namespace)
        if dm is None:
            return
        log.debug("-----")
        info = dm.getparent().getprevious()
        #log.info("info: %s" % info)
        infoindent = "".join(info.tail.split('\n'))
        prev = dm.getprevious()
        #log.info("prev: %s" % prev)
        if prev is not None:
            log.info("prev: %s" % prev)
            previndent = "".join(prev.tail.split('\n'))
            prev.tail = '\n' + infoindent
        indent=self.get_indendation(dm.getprevious())
        dm.text = '\n' + indent + '    '
        dm.tail = '\n' + infoindent
        for node in dm.iterchildren():
            i = dmindent if node.getnext() is not None else ''
            node.tail = '\n' + indent + i

    def write(self):
        """Write XML tree to original filename"""
        logmgr_flog()
        # Only indent docmanager child elements
        self.indent_dm()
        self.__tree.write(self.filename,
                          # pretty_print=True,
                          with_tail=True)

    @property
    def filename(self):
        """Returns filename of the input source

        :return: filename
        :rtype:  str
        """
        logmgr_flog()

        return self.__tree.docinfo.URL

    @filename.setter
    def filename(self, _):
        raise ValueError("filename is only readable")
    @filename.deleter
    def filename(self):
        raise ValueError("filename cannot be deleted")

    @property
    def tree(self):
        """Return our parsed tree object

        :return: tree object
        :rtype:  lxml.etree._ElementTree
        """
        return self.__tree

    @tree.setter
    def tree(self, _):
        raise ValueError("tree is only readable")
    @tree.deleter
    def tree(self):
        raise ValueError("tree cannot be deleted")

    @property
    def root(self):
        """Returns the root element of the XML tree

        :return: root element
        :rtype:  lxml.etree._Element
        """
        return self.__root

    @root.setter
    def root(self, _):
        raise ValueError("root is only readable")

    @root.deleter
    def root(self):
        raise ValueError("root cannot be deleted")
