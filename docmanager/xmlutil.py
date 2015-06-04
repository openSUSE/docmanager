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

import copy
from collections import namedtuple
from docmanager.core import ReturnCodes
from io import StringIO
from itertools import accumulate
import re
import os
import sys

from lxml import etree
import xml.sax
from xml.sax._exceptions import SAXParseException

# -------------------------------------------------------------------
# Regular Expressions

ENTS = re.compile("(&([\w_.]+);)")
STEN = re.compile("(\[\[\[(\#?[\w_.]+)\]\]\])")


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


def replaceinstream(stream, func):
    """Preserve or restore any entities in a stream or file-like object
       depending on the function `func`

    :param stream: iterable stream or file-like object
    :param func: replacement function, signature: func(text)
    :return: another stream with replaced entities
    :rtype: StringIO
    """
    result = StringIO()

    for line in stream:
        result.write(func(line))

    result.seek(0)
    return result

# -------------------------------------------------------------------

def isXML(text):
    """Checks if a text starts with a typical XML construct

       :param str text: The text to observe
       :return: True, if text can be considered as XML, otherwise False
       :rtype: bool
    """
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


def ensurefileobj(source):
    """Return a file(-like) object, regardless if it's a another
       file-object,a filename, or a string

       :param source: filename, file-like object, or string
       :return: StringIO or file-like object
    """

    # StringIO support:
    if hasattr(source, 'getvalue') and hasattr(source, 'tell'):
        # we return a copy
        return copy.copy(source)
    elif isinstance(source, (str, bytes)):
        if isXML(source):
            return StringIO(source)
        else:
            # source isn't a file-like object nor starts with XML structure
            # so it has to be a filename
            return StringIO(open(source, 'r').read())
    # TODO: Check if source is an URL; should we allow this?


# -------------------------------------------------------------------
# Helper functions

def localname(tag):
    """Returns the local name of an element

    :param str tag: Usually in the form of {http://docbook.org/ns/docbook}article
    :return:  local name
    :rtype:  str
    """
    m = re.search("\{(?P<ns>.*)\}(?P<local>[\w]+)", tag)
    if m:
        return m.groupdict()['local']
    else:
        return tag



# -------------

class LocatingWrapper(object):
    def __init__(self, f):
        self.f = f
        self.offset = [0]
        self.curoffs = 0

    def read(self, *a):
        data = self.f.read(*a)
        self.offset.extend(accumulate(len(m)+1 for m in data.split('\n')))
        return data

    def where(self, loc):
        return self.offset[loc.getLineNumber() - 1] + loc.getColumnNumber()

    def close(self):
        self.f.close()


class Handler(xml.sax.handler.ContentHandler):
    def __init__( self, context, locator):
        # handler.ContentHandler.__init__( self )
        super().__init__()
        self.context = context
        self.locstm = locator
        self.pos = namedtuple('Position', ['line', 'col', 'offset'])

    def setDocumentLocator(self, loc):
        self.loc = loc

    def startDocument(self):
        current = self.locstm.where(self.loc)

    def startElement(self, name, attrs):
        ctxlen = len(self.context)
        if ctxlen < 2:
            current = self.locstm.where(self.loc)
            p = self.pos(self.loc.getLineNumber(), \
                         self.loc.getColumnNumber(), \
                         current)
            self.context.append(["%s" % name, p])

    def endElement(self, name):
        ctxlen = len(self.context)

        eline = self.loc.getLineNumber()
        ecol = self.loc.getColumnNumber()
        last = self.locstm.where(self.loc)
        p = self.pos(line=eline, col=ecol, offset=last)
        self.context.append(["/%s" % name, p])


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
    result = {}

    # context is used to save everything
    context = []

    try:
        buffer = ensurefileobj(source)
        # We read in maxsize and save it
        XML = buffer.read(maxsize)
        buffer.seek(0)
        locstm = LocatingWrapper(buffer)
        parser = xml.sax.make_parser()

        # Disable certain features
        parser.setFeature(xml.sax.handler.feature_validation, False)
        parser.setFeature(xml.sax.handler.feature_external_ges, False)
        parser.setFeature(xml.sax.handler.feature_external_pes, False)

        parser.setContentHandler(Handler(context, locstm))
        parser.parse(locstm)
    except SAXParseException as err:
        raise SystemExit(ReturnCodes.E_XML_PARSE_ERROR)

    first = context[0]
    soffset = first[1].offset
    doctype = XML[:soffset]

    if context[1][0][0] == '/':
        last = context[-1]
    else:
        last = context[1]

    eoffset = last[1].offset
    starttag = XML[soffset:eoffset].rstrip(' ')


    result['header'] = doctype
    result['root'] = starttag
    result['offset'] = len(doctype)
    return result
