#!/usr/bin/env python3

import contextlib
import logging
from io import StringIO
from lxml import etree
import re
import sys
import os
import py.path

from docmanager.xmlutil import root_sourceline, ensurefileobj, \
                               recover_entities, preserve_entities, \
                               replaceinstream

log = logging.getLogger(__file__)
_ch = logging.StreamHandler(sys.stderr)
_frmt = logging.Formatter('%(asctime)s [%(levelname)s]: '
                          '%(message)s', '%H:%M:%S')
_ch.setFormatter(_frmt)
log.setLevel(logging.DEBUG)
log.addHandler(_ch)

testdir = py.path.local(py.path.local(__file__).dirname)
docmgrdir = testdir.join("..")
sys.path.append(docmgrdir.strpath)

# -------------------------------------------------------------------

class XmlProxy(object):
    """Context manager

    Usage:
    with XmlProxy(XmlHandler, source) as xml:
        xml.set("maintainer", "tux")
        xml.del("status")
        # any other

    """
    def __init__(self, handler, source):
        """Constructor

        :param source: filename, file-like object, or string
        :param handler: uninstanciated handler object
        """
        self._handler = handler
        self._source = source
        self._buffer = None


    def __enter__(self):
        # 1. Read in the XML file and create a file-like object:
        self._buffer = ensurefileobj(self._source)
        print(self._buffer)

        # 2. Determine the header:
        self._r = root_sourceline(self._buffer)
        print(self._r)

        # 3. Save the header
        self._header = "".join(self._r['header'])
        # Cut off any linebreak as it is added by etree.tostring again
        self._header = self._header[:-1] \
                       if self._header[-1] == '\n' else self._header

        headerlen = len(self._header)

        # 4. Replace any entities left in the remaining XML code
        self._buffer.seek(headerlen)
        self._buffer = replaceinstream(self._buffer, preserve_entities)

        # 5. Hand over the remaining XML code to our handler:
        self._xml = self._handler(self._buffer)

        # 6. Do stuff with it (outside of the context manager)
        return self._xml

    def createresult(self):
        t = self._xml.tree
        log.debug("handler: %s", type(t))
        return etree.tostring(t,
                              doctype=self._header,
                              encoding="unicode"
                             )

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            log.error(exc_type, exc_val, exc_tb)
            # print(exc_type, exc_val, exc_tb)
            return False

        log.debug("__exit__")

        # 7. Finalize everything and write to the buffer
        self._xml.finalize(self._buffer)

        # 8. Restore any entities in the XML code
        # 9. Write back/finalize
        with open(self._source, 'w') as fh:
            fh.write(recover_entities(self.createresult()))

        return True


# -----------------------------------------------------------------------

NS = {
        "d":  "http://docbook.org/ns/docbook",
        "dm": "urn:x-suse:ns:docmanager"
     }


class XmlHandler(object):
    """An XmlHandler instance represents an XML tree of a file"""

    def __init__(self, source):
        """Initializes the XmlHandler class

        :param source: filename, file-like object, or string
        """

        #register the namespace
        etree.register_namespace("dm", "{dm}".format(**NS))
        self.__xmlparser = etree.XMLParser(remove_blank_text=False,
                                           resolve_entities=False,
                                           # load_dtd=False,
                                           dtd_validation=False)
        #load the file and set a reference to the dm group
        self.__tree = etree.parse(source, self.__xmlparser)
        # self.tree = self.__tree
        self.__root = self.__tree.getroot()
        # self.check_root_element()
        self.__docmanager = self.__tree.find("//dm:docmanager",
                                             namespaces=NS)
        if self.__docmanager is None:
            self.create_group()

    def __str__(self):
        """Return entire XML tree as Unicode string """
        return etree.tostring(self.__tree, encoding="unicode")

    def __repr__(self):
        return "<{} '{}': {}>".format(self.__class__.__name__,
                                  self.filename,
                                  self.__root.tag
                                 )

    def __iter__(self):
        return iter(self.__str__().split())


    def create_group(self):
        """Creates the docmanager group element"""

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
        # self.write()

    def set_only(self, key, value):
        """Sets the key as element and value as content

           :param key:    name of the element
           :param value:  value that this element will contain

           If key="foo" and value="bar" you will get:
            <foo>bar</foo>
           whereas foo belongs to the DocManager namespace
        """

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
        # self.write()

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
        log.debug("indent_dm")
        dmindent='    '
        dm = self.__tree.find("//dm:docmanager", namespaces=NS)
        if dm is None:
            return

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

    def write(self, *, target=None, doctype=None):
        """Write XML tree to original filename

        :param target: target filename, or file-like object
                       if None, use filename from property instead
        """
        log.debug("write: self=%r, target=%s, doctype=%r", self, target, doctype)
        if target is None:
            self.__tree.write(self.filename,
                              # pretty_print=True,
                              with_tail=True)
        else:
            target.write(etree.tostring(self.__tree,
                                        doctype=doctype,
                                        encoding="unicode"
                                        )
                        )

    def finalize(self, target=None):
        """Indent and write the tree"""
        log.debug("finalize: self=%r, target=%s", self, target)
        self.indent_dm()
        self.write(target=target)

    @property
    def filename(self):
        """Returns filename of the input source

        :return: filename
        :rtype:  str
        """

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

#    @tree.setter
#    def tree(self, _):
#        raise ValueError("tree is only readable")
#    @tree.deleter
#    def tree(self):
#        raise ValueError("tree cannot be deleted")

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


if __name__ == "__main__":
    source = "test/testfiles/valid_xml_file_with_doctype.xml"

    # xmlhl = XmlHandler(source)
    #print(repr(xmlhl))
    #print(xmlhl)

    # Example 1:
    # with xmlproxy(XmlHandler, source) as xml:
    #    print(xml)

    # Example 2:
    with XmlProxy(XmlHandler, source) as xml:
        print(repr(xml))
        xml.set("maintainer", "toms")
        print("dir:", dir(xml))
