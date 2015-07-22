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
import sys
import xml.sax
from collections import namedtuple
from docmanager.core import NS, ReturnCodes, VALIDROOTS
from docmanager.logmanager import log, logmgr_flog
from io import StringIO
from itertools import accumulate

# -------------------------------------------------------------------
# Regular Expressions

ENTS = re.compile("(&([\w_\.-]+);)")
STEN = re.compile("(\[\[\[(\#?[\w_\.-]+)\]\]\])")
NAMESPACE_REGEX = re.compile("\{(?P<ns>.*)\}(?P<local>[-a-zA-Z0-9._]+)")


def ent2txt(match, start="[[[", end="]]]"):
    """Replace any &text; -> [[[text]]]

    :param _sre.SRE_Match match: match object from re
    :param str start: Start string of entity replacement
    :param str end:   end string
    :return: replaced string
    :rtype: str
    """
    logmgr_flog()
    
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
    logmgr_flog()
    
    if match:
        return "&{};".format(match.group(2))


def preserve_entities(text):
    """Preserve any entities in text

    :param str text: the text that should preserve entities
    :return: the preserved text
    :rtype: str
    """
    logmgr_flog()
    
    return ENTS.sub(ent2txt, text)


def recover_entities(text):
    """Recover any preserved entities in text

    :param str text: the text that should recover entities
    :return: the recovered text
    :rtype: str
    """
    logmgr_flog()
    
    return STEN.sub(txt2ent, text)


def replaceinstream(stream, func):
    """Preserve or restore any entities in a stream or file-like object
       depending on the function `func`

    :param stream: iterable stream or file-like object
    :param func: replacement function, signature: func(text)
    :return: another stream with replaced entities
    :rtype: StringIO
    """
    logmgr_flog()
    
    result = StringIO()

    for line in stream:
        result.write(func(line))

    result.seek(0)
    return result

def check_root_element(rootelem, etree):
    """Checks if root element is valid
    
    :param object: root element (object)
    :param object: etree element (etree object)"""
    logmgr_flog()
    
    tag = etree.QName(rootelem.tag)
    if tag.localname not in VALIDROOTS:
        raise ValueError("Cannot add info element to %s. "
                         "Not a valid root element." % tag.localname)

# -------------------------------------------------------------------

def isXML(text):
    """Checks if a text starts with a typical XML construct

       :param str text: The text to observe
       :return: True, if text can be considered as XML, otherwise False
       :rtype: bool
    """
    logmgr_flog()
    
    possiblestartstrings = (re.compile("<\?xml"),
                            re.compile("<!DOCTYPE"),
                            re.compile("<!--",),
                            re.compile(r'<(?P<tag>(?:(?P<prefix>\w+):)?'
                                        '(?P<name>[a-zA-Z0-9_]+))\s*'),
                           )
    result = False
    for matcher in possiblestartstrings:
        match = matcher.search(text)
        if match:
            result = True
            break
    return result


def findinfo_pos(root):
    """Find the position where to insert the <info> element

    :return: position where to insert <info>
    :rtype: int
    """
    logmgr_flog()
    
    titles = root.xpath("(d:title|d:subtitle|d:titleabbrev)[last()]",
                                namespaces=NS)
    if not titles:
        # Just in case we didn't find any titles at all, return null
        return 0

    return root.index(titles[0]) + 1


# -------------------------------------------------------------------

def ensurefileobj(source):
    """Return a file(-like) object, regardless if it's a another
       file-object, a filename, or a string

       :param source: filename, file-like object, or string
       :return: StringIO or file-like object
    """
    logmgr_flog()
    
    # StringIO support:
    if hasattr(source, 'getvalue') and hasattr(source, 'tell'):
        # we return the source
        return source
    elif isinstance(source, (str, bytes)):
        if isXML(source):
            return StringIO(source)
        else:
            # source isn't a file-like object nor starts with XML structure
            # so it has to be a filename
            try:
                res = StringIO(open(source, 'r').read())
            except FileNotFoundError as err:
                log.error("Could not find file '{}'.".format(err.filename))
                sys.exit(ReturnCodes.E_FILE_NOT_FOUND)
            
            return res
    # TODO: Check if source is an URL; should we allow this?


# -------------------------------------------------------------------
# Helper functions

def localname(tag):
    """Returns the local name of an element

    :param str tag: Usually in the form of {http://docbook.org/ns/docbook}article
    :return:  local name
    :rtype:  str
    """
    logmgr_flog()
    
    m = NAMESPACE_REGEX.search(tag)
    if m:
        return m.groupdict()['local']
    else:
        return tag

def get_namespace(tag):
    """Returns the namespace of an element

    :param str tag: Usually in the form of {http://docbook.org/ns/docbook}article
    :return:        namespace of the element
    :rtype:         str
    """
    logmgr_flog()
    
    m = NAMESPACE_REGEX.search(tag)
    if m:
        return m.groupdict()['ns']
    else:
        return ''

def compilestarttag(roottag=None):
    """Compile a regular expression for start tags like <article> or
       <d:book> with or without any  attributes

       :param str roottag: Name of roottag or None, for a general tag
       :return: a pattern object
       :rtype: _sre.SRE_Pattern
    """
    logmgr_flog()
    
    # Taken from the xmllib.py
    # http://code.metager.de/source/xref/python/jython/lib-python/2.7/xmllib.py
    _S = '[ \t\r\n]+'                       # white space
    _opS = '[ \t\r\n]*'                     # optional white space
    _Name = '[a-zA-Z_:][-a-zA-Z0-9._:]*'    # valid XML name
    _QStr = "(?:'[^']*'|\"[^\"]*\")"        # quoted XML string
    attrfind = re.compile(
        _S + '(?P<name>' + _Name + ')'
        '(' + _opS + '=' + _opS +
        '(?P<value>' + _QStr + '|[-a-zA-Z0-9.:+*%?!\(\)_#=~]+))?')
    starttagend = re.compile(_opS + '(?P<slash>/?)>')
    if roottag:
        root = '<(?P<tagname>' + roottag + ')'
    else:
        root = '<(?P<tagname>' + _Name + ')'
    return re.compile(root + '(?P<attrs>(?:' + attrfind.pattern + ')*)' +
                      starttagend.pattern)


# -------------

class LocatingWrapper(object):
    """Holds a table which are used to transform line and column position
       into offset
    """
    def __init__(self, f):
        logmgr_flog()
        
        self.f = f
        self.offset = [0]
        self.curoffs = 0

    def read(self, *a):
        """Read data"""
        logmgr_flog()
        
        data = self.f.read(*a)
        self.offset.extend(accumulate(len(m)+1 for m in data.split('\n')))
        return data

    def where(self, locator):
        """Returns the offset from line and column

        :param locator: locator object
        :return: offset
        :rtype:  int
        """
        logmgr_flog()
        
        return self.offset[locator.getLineNumber() - 1] + locator.getColumnNumber()

    def close(self):
        """Close the locator"""
        logmgr_flog()
        # Normally, we would close our file(-alike) object and call
        #   self.f.close()
        # However, we do nothing



class Handler(xml.sax.handler.ContentHandler):
    """ContentHandler to watch for start and end elements. Needed to
       get the location of all the elements
    """
    def __init__( self, context, locator):
        logmgr_flog()
        
        # handler.ContentHandler.__init__( self )
        super().__init__()
        self.context = context
        self.locstm = locator
        self.pos = namedtuple('Position', ['line', 'col', 'offset'])

    def setDocumentLocator(self, locator):
        """Called by the parser to give the application a locator for
           locating the origin of document events.

        :param LocatingWrapper loc: LocatingWrapper object
        """
        logmgr_flog()
        
        self.loc = locator

    def startElement(self, name, attrs):
        """Signals the start of an element in non-namespace mode

        :param str name:  XML 1.0 Name of the element
        :param Attributes attrs: attributes of the current element
        """
        logmgr_flog()
        
        ctxlen = len(self.context)
        # We are only interested in the first two start tags
        if ctxlen < 2:
            current = self.locstm.where(self.loc)
            pos = self.pos(self.loc.getLineNumber(), \
                         self.loc.getColumnNumber(), \
                         current)
            self.context.append(["%s" % name, pos])

    def endElement(self, name):
        """Signals the end of an element in non-namespace mode

        :param str name:  XML 1.0 Name of the element
        """
        logmgr_flog()
        
        eline = self.loc.getLineNumber()
        ecol = self.loc.getColumnNumber()
        last = self.locstm.where(self.loc)
        pos = self.pos(line=eline, col=ecol, offset=last)

        # save the position of an end tag and add '/' in front of the
        # name to distinguish it from a start tag
        self.context.append(["/%s" % name, pos])

    def processingInstruction(self, target, data):
        """Receive notification of a processing instruction (PI)

        :param str target: the target of the PI
        :param str data:   the data of the PI
        """
        logmgr_flog()
        
        ctxlen = len(self.context)
        # Only append PIs when it's NOT before start-tag
        if ctxlen:
            current = self.locstm.where(self.loc)
            pos = self.pos(self.loc.getLineNumber(), \
                            self.loc.getColumnNumber(), \
                            current)
            self.context.append(["?%s" % target, pos])

    def comment(self, text): # pylint:unused-argument
        """Signals an XML comment

        :param str text: text content of the XML comment
        """
        logmgr_flog()
        
        ctxlen = len(self.context)
        # We are only interested in the first two start tags
        if ctxlen:
            current = self.locstm.where(self.loc)
            pos = self.pos(self.loc.getLineNumber(), \
                           self.loc.getColumnNumber(), \
                           current)
            self.context.append(["-- comment", pos])

    # From LexicalParser
    def startCDATA(self):
        """Signals a CDATA section"""
        logmgr_flog()

    endCDATA = startCDATA

    def startDTD(self,  doctype, publicID, systemID): # pylint:unused-argument
        """Signals the start of an DTD declaration

        :param  doctype: name of the root element
        :param publicID: public identifier (or empty)
        :param systemID: system identifier (or empty)
        """
        logmgr_flog()

    def endDTD(self):
        """Reports the end of a DTD declaration"""
        logmgr_flog()

    def startEntity(self, name):  # pylint:unused-argument
        """Reports the start of an entity"""
        logmgr_flog()


def findprolog(source, maxsize=5000):
    """Returns a dictionary with essential information about the prolog

    :param source:
    :type source: source, file object, or file-like object
                  expected to be well-formed
    :param int maxize: Maximum size of bytes to read into XML buffer
    :return: { 'header': '...', # str everything before the start tag
               'root':   '...', # str: start tag from '<' til '>'
               'offset:  1,     # Integer
             }
    :rtype: dict
    """
    logmgr_flog()

    result = {}

    # context is used to save our locations
    context = []

    buf = ensurefileobj(source)
    # We read in maxsize and hope this is enough...
    xmlbuf = buf.read(maxsize)
    buf.seek(0)
    locstm = LocatingWrapper(buf)
    parser = xml.sax.make_parser()

    # Disable certain features:
    # no validation, no external general and parameter entities
    parser.setFeature(xml.sax.handler.feature_validation, False)
    parser.setFeature(xml.sax.handler.feature_external_ges, False)
    parser.setFeature(xml.sax.handler.feature_external_pes, False)

    handler = Handler(context, locstm)
    parser.setProperty(xml.sax.handler.property_lexical_handler, handler);

    parser.setContentHandler(handler)
    parser.parse(locstm)

    first = context[0]
    soffset = first[1].offset
    doctype = xmlbuf[:soffset]

    # Check if we have reached the "end tag" (symbolized with '/' in
    # its first character).
    # If yes, start and end tag is on the same line and we can use the
    # last entry.
    # If not, we need to look in the next entry
    if context[1][0][0] == '/':
        last = context[-1]
    elif context[1][0][0] ==  '-':
        last = context[1]
    else:
        last = context[1]

    eoffset = last[1].offset
    starttag = xmlbuf[soffset:eoffset].rstrip(' ')

    result['header'] = doctype
    result['root'] = starttag
    result['offset'] = len(doctype)
    result['roottag'] = context[0][0]

    return result

def xml_indent(elem, level=0):
    """Indent XML elements

    :param lxml.etree._Element elem: XML Element to indent
    :param int level: indentation level
    """

    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            xml_indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i