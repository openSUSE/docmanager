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

from docmanager.core import ReturnCodes
from docmanager.logmanager import log, logmgr_flog
from docmanager.xmlutil import prolog, VALIDROOTS
from docmanager.core import NS
import io
import re
from lxml import etree

# -------------------------------------------------------------------
# Regular Expressions
ENTS = re.compile("(&(\#?\w+);)")
STEN = re.compile("(\[\[\[(\#?\w+)\]\]\])")

def ent2txt(match, start="[[[", end="]]]"):
    """Replace any &text; -> [[[text]]]

    :param _sre.SRE_Match match: match object from re
    :param str start: Start string of entity replacement
    :param str end:   end string
    :return: replaced string
    :rtype: str
    """
    if match:
        return "{}{}{}".format(start,
                               match.group(2),
                               end)


def txt2ent(match):
    """Replace any [[[text]]] -> &text;

    :param _sre.SRE_Match match: match object from re
    :return: replaced string
    :rtype: str
    """
    if match:
        return "&{};".format(match.group(2))


def preserve_entities(text):
    """Preserve any entities in text

    :param str text: the text that should preserve entities
    :return: the preserved text
    :rtype: str
    """
    return ENTS.sub(ent2txt, text)


def recover_entities(text):
    """Recover any preserved entities in text

    :param str text: the text that should recover entities
    :return: the recovered text
    :rtype: str
    """
    return STEN.sub(txt2ent, text)


# -------------------------------------------------------------------

class XMLProxy:
    """Proxy base class; redirects everything to another object"""
    def __init__(self, subject):
        """Constructor

        :param subject: Any object
        """
        self.__subject = subject


    def __getattr__(self, name):
        """Redirects acces of XMLProxy.METHOD to self.__subject.METHOD

    See https://docs.python.org/3.4/reference/datamodel.html#object.__getattr__

        :param str name: Name of the
        """
        return getattr(self.__subject, name)


class XMLProxyHandler(XMLProxy):
    """Proxy class that stands for a XmlHandler class"""

    def __init__(self, subject, source):
        """Constructor

        :param subject: non-instantiated object
        :param source:  filename,
        """
        self.__source = source
        self.__buffer = None
        self.__doctype = None
        self.__xml = None

        if os.path.exists(source):
            source = open(source, 'r')
        # elif isinstance(source, io.TextIOWrapper):
        self.__buffer = io.StringIO(source.read())
        self.prologlen, self.sourceline, self.header = prolog(self.__buffer)
        self.__buffer.seek(self.prologlen)
        super().__init__(self, subject() )

    def write(self, target):
        """Write XML tree to original filename

        :param target: target filename, or file-like object
                       if None, use filename from property instead
        """


class XmlHandler(object):
    """An XmlHandler instance represents an XML tree of a file
    """

    def __init__(self, source):
        """Initializes the XmlHandler class

        :param str source: filename of XML file
        """
        logmgr_flog()
        #register the namespace
        etree.register_namespace("dm", "{dm}".format(**NS))
        self.__xmlparser = etree.XMLParser(remove_blank_text=False,
                                           resolve_entities=False,
                                           # load_dtd=False,
                                           dtd_validation=False)
        #load the file and set a reference to the dm group
        self.__tree = etree.parse(source, self.__xmlparser)
        self.__root = self.__tree.getroot()
        # self.check_root_element()
        self.__docmanager = self.__tree.find("//dm:docmanager",
                                             namespaces=NS)
        if self.__docmanager is None:
            self.create_group()

    def check_root_element(self):
        """Checks if root element is valid"""
        if self._root.tag not in VALIDROOTS:
            raise ValueError("Cannot add info element to %s. "
                             "Not a valid root element." % self._root.tag)

    def create_group(self):
        """Creates the docmanager group element"""
        logmgr_flog()
        #search the info-element if not exists raise an error
        element = self.__tree.find("//d:info", namespaces=NS)
        # TODO: We need to check for a --force option
        if element is None:
            log.warn("Can't find the <info> element in '%s'. Adding one.",
                     self.__tree.docinfo.URL)
            if not self.__root.getchildren():
                log.error("The \"%s\" file is not a valid DocBook 5 file.",
                          self.__tree.docinfo.URL)
                sys.exit(ReturnCodes.E_INVALID_XML_DOCUMENT)
            
            title = self.__root.getchildren()[0]
            
            idx = self.__root.index(title) + 1
            self.__root.insert(idx, etree.Element("{%s}info" % NS["d"]))
            element = self.__root.getchildren()[idx]
            element.tail = self.__root.getchildren()[idx-1].tail

        self.__docmanager = etree.SubElement(element,
                                             "{{{dm}}}docmanager".format(**NS),
                                            )
        #log.debug("docmanager?: %s" % etree.tostring(self.__tree).decode("UTF-8"))
        self.write()

    def set_only(self, key, value):
        """Sets the key as element and value as content

           :param key:    name of the element
           :param value:  value that this element will contain

           If key="foo" and value="bar" you will get:
            <foo>bar</foo>
           whereas foo belongs to the DocManager namespace
        """
        logmgr_flog()
        key_handler = self.__docmanager.find("./dm:"+key,
                                             namespaces=NS)
        #update the old key or create a new key
        if key_handler is not None:
            key_handler.text = value
        else:
            node = etree.SubElement(self.__docmanager,
                                    "{{{dm}}}{key}".format(key=key,
                                                           **NS),
                                    # nsmap=NS
                                    )
            node.text = value

    def set(self, key, value):
        """Sets the key as element and value as content and perform a write

           :param key:    name of the element
           :param value:  value that this element will contain

           If key="foo" and value="bar" you will get:
            <foo>bar</foo>
           whereas foo belongs to the DocManager namespace
        """
        self.set_only(key, value)
        self.write()

    def set_all(self, **kwargs):
        """Set all keys at once

           :param dict kwargs: dictionary with properties and their values
        """
        for key in kwargs:
            self.set_only(key, kwargs[key])
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
        element = self.__docmanager.find("./dm:" + key,
                                         namespaces=NS)
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

        :return: the values
        :rtype: dict
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
                                             namespaces=NS)

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
        dm = self.__tree.find("//dm:docmanager", namespaces=NS)
        if dm is None:
            return
        log.debug("-----")
        info = dm.getparent().getprevious()
        #log.info("info: %s", info)
        infoindent = "".join(info.tail.split('\n'))
        prev = dm.getprevious()
        #log.info("prev: %s", prev)
        if prev is not None:
            log.info("prev: %s", prev)
            previndent = "".join(prev.tail.split('\n'))
            prev.tail = '\n' + infoindent
        indent=self.get_indendation(dm.getprevious())
        dm.text = '\n' + indent + '    '
        dm.tail = '\n' + infoindent
        for node in dm.iterchildren():
            i = dmindent if node.getnext() is not None else ''
            node.tail = '\n' + indent + i

    def write(self, target=None):
        """Write XML tree to original filename

        :param target: target filename, or file-like object
                       if None, use filename from property instead
        """
        logmgr_flog()
        # Only indent docmanager child elements
        self.indent_dm()
        target = target if target is not None else self.filename
        self.__tree.write(target,
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
