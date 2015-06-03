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

from io import StringIO
import re
import os
import sys

from lxml import etree

# All elements which are valid as root (from 5.1CR3)
VALIDROOTS = ('abstract', 'address', 'annotation', 'audiodata',
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
              'informaltable', 'inlinemediaobject', 'itemizedlist',
              'legalnotice', 'literallayout', 'mediaobject', 'methodsynopsis',
              'msg', 'msgexplan', 'msgmain', 'msgrel', 'msgset', 'msgsub',
              'note', 'orderedlist', 'para', 'part', 'partintro',
              'personblurb', 'procedure', 'productionset', 'programlisting',
              'programlistingco', 'programlistingco', 'qandadiv',
              'qandaentry', 'qandaset', 'qandaset', 'refentry',
              'refsect1', 'refsect2', 'refsect3',
              'refsection', 'refsynopsisdiv', 'revhistory', 'screen',
              'screenco', 'screenco', 'screenshot',
              'sect1', 'sect2', 'sect3', 'sect4', 'sect5',
              'section', 'segmentedlist', 'set', 'set', 'setindex', 'sidebar',
              'simpara', 'simplelist', 'simplesect',
              'step', 'stepalternatives', 'synopsis',
              'table', 'task', 'taskprerequisites', 'taskrelated',
              'tasksummary', 'textdata', 'textobject', 'tip', 'toc', 'tocdiv',
              'topic', 'variablelist', 'videodata', 'videoobject', 'warning'
             )


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
        # we do nothing
        pass
    elif isinstance(source, (str, bytes)):
        if isXML(source):
            source = StringIO(source)
        else:
            # source isn't a file-like object nor starts with XML structure
            # so it has to be a filename
            source = StringIO(open(source, 'r').read())
    # TODO: Check if source is an URL; should we allow this?
    return source


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

def compilestarttag():
    """Compile a regular expression for start tags like <article> or
       <d:book> with or without any  attributes

       :return: a pattern object
       :rtype: _sre.SRE_Pattern
    """
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
    return re.compile('<(?P<tagname>' + _Name + ')'
                      '(?P<attrs>(?:' + attrfind.pattern + ')*)' +
                      starttagend.pattern)


def root_sourceline(source, resolver=None):
    """Returns a dictionary with essential information about the root element

    :param source:
    :type source: filename, file object, or file-like object
                  expected to be well-formed
    :param etree.Resolver resolver: custom resolver
    :return: line number, column
    :rtype: tuple
    """
    # See https://gist.github.com/tomschr/6ecaaf69231dfbc9517a
    # for an alternative implementation with SaX

    result = {}
    parser = etree.XMLParser(remove_blank_text=False,
                             resolve_entities=False,
                             dtd_validation=False,
                             load_dtd=False)
    if resolver is not None:
        parser.resolvers.add(resolver)

    buffer = ensurefileobj(source)
    tree = etree.parse(buffer, parser)
    root = tree.getroot()

    # Get first an "approximation" of where we could find it
    maxsourceline = root.sourceline

    # HACK: lxml's .sourceline returns only the _end_ of the start tag.
    # For example:
    #
    # 1| <?xml version="1.0"?>
    # 2| <!DOCTYPE article
    # 3| [ ...
    # 4| ]>
    # 5| <article version="5.0" xml:lang="en"
    # 6|          xmlns:dm="urn:x-suse:ns:docmanager"
    # 7|          xmlns="http://docbook.org/ns/docbook"
    # 8|          xmlns:xlink="http://www.w3.org/1999/xlink">
    #
    # In the above example, we need line 5, but .sourceline returns line 8
    # which is "wrong". 
    # Therefor we need to go back from line 8 until we find the start-tag
    #
    # See thread in
    # https://mailman-mail5.webfaction.com/pipermail/lxml/2015-May/007518.html

    # Find any start-tag which match this regex:

    prefix = root.prefix if root.prefix else ""
    starttag = compilestarttag()

    # Read lines until maxsourceline is reached
    header = [next(buffer) for _ in range(maxsourceline)]

    # Try to first check, if start tag appears on one line
    i = maxsourceline - 1
    match = starttag.search(header[i])
    offset = 0
    
    if not match:
        # We need to search for the beginning of the start tag
        ll = []
        # Iterate in reverse order to find a match for our start-tag
        for i, line in enumerate(reversed(header)):
            ll.insert(0, line)
            match = starttag.search("".join(ll))
            
            if match:
                break
        
        length = len("".join(ll))
        length -= match.span()[0]
        offset = len("".join(header))-length
    else:
        offset = match.span()[0]
        offset += len("".join(header[:i]))

    # Variable 'i' contains now the (line) offset where you can find
    # the start tag inside the header
    #
    # offset is the number of character before the start tag
    #offset += len("".join(header[:i]))
    # print("Match obj:", match, match.groupdict() )

    # The character offset
    result['offset'] = offset

    # span is the character offset and can be used to cut off the start tag
    # for example: "".join(result['header'])[slice(*result['span'])]
    s = match.span()
    result['header'] = "".join(header)[:offset]
    result['root'] = "".join(header)[offset:]
    
    return result