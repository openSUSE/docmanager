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
from docmanager.core import DefaultDocManagerProperties, \
     NS, ReturnCodes, VALIDROOTS
from docmanager.logmanager import log, logmgr_flog
from docmanager.xmlutil import check_root_element, compilestarttag, ensurefileobj, \
     findprolog, get_namespace, localname, recover_entities, replaceinstream, preserve_entities, \
     findinfo_pos
from io import StringIO
from lxml import etree
from xml.sax._exceptions import SAXParseException

class XmlHandler(object):
    """An XmlHandler instance represents an XML tree of a file
    """

    def __init__(self, filename):
        """Initializes the XmlHandler class

        :param str filename: filename of XML file
        """
        logmgr_flog()

        # general
        self._filename = ""
        self._buffer = None # StringIO
        
        # prolog
        self._offset = 0
        self._header = ""
        self._root = ""
        self.roottag = ""
        
        # parser
        self.__xmlparser = None
        
        # lxml
        self.__tree = None
        self.__root = None
        self.__docmanager = None

        # load the file into a StringIO buffer
        self._filename = filename
        self._buffer = ensurefileobj(self._filename)
        
        # parse the given file with lxml
        self.parse()

    def parse(self):
        """This function parses the whole XML file
        """
        logmgr_flog()
        
        # find the prolog of the XML file (everything before the start tag)
        try:
            prolog = findprolog(self._buffer)
        except SAXParseException as err:
            log.error("<{}:{}> {} in {!r}.".format(err.getLineNumber(), \
                                      err.getColumnNumber(), \
                                      err.getMessage(), \
                                      self.filename,))
            sys.exit(ReturnCodes.E_XML_PARSE_ERROR)

        # save prolog details
        self._offset, self._header, self._root, self._roottag = prolog['offset'], \
            prolog['header'], \
            prolog['root'], \
            prolog['roottag']

        # replace any entities
        self.replace_entities()

        # register namespace
        # etree.register_namespace("dm", "{dm}".format(**NS))
        self.__xmlparser = etree.XMLParser(remove_blank_text=False,
                                           resolve_entities=False,
                                           dtd_validation=False)
        
        # load the file and set a reference to the dm group
        self.__tree = etree.parse(self._buffer, self.__xmlparser)
        self.__root = self.__tree.getroot()
        
        check_root_element(self.__root, etree)
        
        # check for DocBook 5 namespace in start tag
        self.check_docbook5_ns()
        
        # check for docmanager element
        self.__docmanager = self.__tree.find("//dm:docmanager", namespaces=NS)
        
        if self.__docmanager is None:
            log.info("No docmanager element found")
            self.create_group()
        else:
            log.info("Found docmanager element %s", self.__docmanager.getparent() )

    def check_docbook5_ns(self):
        """Checks if the current file is a valid DocBook 5 file.
        """
        rootns = get_namespace(self.__root.tag)
        if rootns != NS['d']:
            log.error("{} is not a DocBook 5 XML document. The start tag of the document has to be in the official " \
                      "DocBook 5 namespace: {}".format(self._filename, NS['d']))
            sys.exit(ReturnCodes.E_NOT_DOCBOOK5_FILE)
    
    def replace_entities(self):
        """This function replaces entities in the StringIO buffer
        """
        logmgr_flog()
        
        self._buffer.seek(self._offset)
        self._buffer = replaceinstream(self._buffer, preserve_entities)

    def init_default_props(self, force=False):
        """Initializes the default properties for the given XML files
    
        :param bool force: Ignore if there are already properties in an XML - just overwrite them
        """
        ret = 0
        for i in DefaultDocManagerProperties:
            if (i not in self.get(i)) or \
               (self.get(i)[i] is None) or \
               (self.get(i)[i] is not None and force):
                self.set({i: ""})
            else:
                ret += 1
        return ret

    def check_root_element(self):
        """Checks if root element is valid"""
        tag = etree.QName(self.__root.tag)
        if tag.localname not in VALIDROOTS:
            raise ValueError("Cannot add info element to file '{}'. '{}' is not a valid root "
                             "element.".format(self._filename, localname(self.__root.tag)))

    def create_group(self):
        """Creates the docmanager group element"""
        logmgr_flog()

        #search the info-element if not exists raise an error
        info = self.__tree.find("//d:info", namespaces=NS)
        # TODO: We need to check for a --force option
        if info is None:
            log.info("No <info> element found!")
            pos = findinfo_pos(self.__root)
            log.info("Using position %d", pos)
            info = etree.Element("{%s}info" % NS["d"])
            info.tail = '\n'
            info.text = '\n'
            self.__root.insert(pos, info)

            log.info("Adding <info> element in '%s'", self.filename)

        log.info("Adding <dm:docmanager> to <info>")
        # dm = etree.Element("{%s}docmanager" % NS["dm"])
        # self.__docmanager = info.insert(0, dm)
        self.__docmanager = etree.SubElement(info,
                                             "{{{dm}}}docmanager".format(**NS),
                                             nsmap={'dm': NS['dm']},
                                            )
        #print("docmanager?: %s" % etree.tostring(self.__tree, encoding="unicode"))
        self.write()

    def set(self, pairs):
        """Sets the key as element and value as content

           :param key:    name of the element
           :param value:  value that this element will contain

           If key="foo" and value="bar" you will get:
            <foo>bar</foo>
           whereas foo belongs to the DocManager namespace
        """
        logmgr_flog()
        
        for i in pairs:
            key_handler = self.__docmanager.find("./dm:"+i,
                                                 namespaces=NS)
            #update the old key or create a new key
            if key_handler is not None:
                key_handler.text = pairs[i]
            else:
                node = etree.SubElement(self.__docmanager,
                                        "{{{dm}}}{key}".format(key=i,
                                                               **NS),
                                        # nsmap=NS
                                        )
                node.text = pairs[i]
        
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
                                         namespaces=NS)
        if self.is_prop_set(key) is True and element.text in values:
            return True

        return False

    def is_prop_set(self, prop):
        """
        Checks if a property is set in an XML element
        
        :param str prop: the property
        
        :return: if property is set
        :rtype: bool
        """
        element = self.__docmanager.find("./dm:{}".format(prop), namespaces=NS)
        if element is not None:
            return True
        
        return False

    def get(self, keys=None):
        """Returns all matching values for a key in docmanager element

        :param key: localname of element to search for
        :type key: list, tuple, or None
        :return: the values
        :rtype: dict
        """
        logmgr_flog()

        if len(keys) == 0:
            return self.get_all()
        
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
            ret[localname(i.tag)] = i.text

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
        dm = self.__tree.find("//dm:docmanager",
                              namespaces=NS)
        log.debug("dm is %s", dm)
        if dm is None:
            return
        log.debug("-----")
        info = dm.getparent() #.getprevious()
        log.info("info: %s", info)
        prev = info.getprevious()
        log.info("prev: %s", prev)
        parent = info.getparent()
        log.info("parent of info: %s", parent)
        log.info("child of info: %s", info.getchildren())

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

    def write(self):
        """Write XML tree to original filename"""
        logmgr_flog()
        # Only indent docmanager child elements
        self.indent_dm()

        log.debug("root: %s", repr(self._root))
        with open(self._filename, 'w') as f:
            content = recover_entities(etree.tostring(self.__tree, \
                           encoding='unicode', \
                           # doctype=self._header.rstrip())
                      ))
            # self._offset, self._header, self._root, self._roottag
            starttag = compilestarttag(self._roottag)
            content = starttag.sub(lambda _: self._root.rstrip(), content, 1)

            # log.debug("content: %s", repr(content))
            f.write(self._header.rstrip()+"\n" + content)

    @property
    def filename(self):
        """Returns filename of the input source

        :return: filename
        :rtype:  str
        """
        # return self.__tree.docinfo.URL
        return self._filename

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
