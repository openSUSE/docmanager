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
from docmanager.exceptions import DMInvalidXMLRootElement, \
                                  DMFileNotFoundError
from docmanager.logmanager import log, logmgr_flog
from io import StringIO
from itertools import accumulate

# -------------------------------------------------------------------
# Regular Expressions

ENTS = re.compile(r"(&([\w_\.-]+);)")
STEN = re.compile(r"(\[\[\[(\#?[\w_\.-]+)\]\]\])")
NAMESPACE_REGEX = re.compile(r"\{(?P<ns>.*)\}(?P<local>[-a-zA-Z0-9._]+)")

# Regular Expressions
SPACE = r"[ \t\r\n]"  # whitespace
S = "%s+" % SPACE  # One or more whitespace
opS = "%s*" % SPACE  # Zero or more  whitespace
oS = "%s?" % SPACE  # Optional whitespace
NAME = "[a-zA-Z_:][-a-zA-Z0-9._:]*"  # Valid XML name
QSTR = "(?:'[^']*'|\"[^\"]*\")"  # Quoted XML string
QUOTES = "(?:'[^']'|\"[^\"]\")"
SYSTEMLITERAL = "(?P<sysid>%s)" % QSTR
PUBLICLITERAL = (
    r'(?P<pubid>"[-\'\(\)+,./:=?;!*#@$_%% \n\ra-zA-Z0-9]*"|'
    r"'[-\(\)+,./:=?;!*#@$_%% \n\ra-zA-Z0-9]*')"
)
EXTERNALID = (
    """(?:SYSTEM|PUBLIC{S}{PUBLICLITERAL})""" """{S}{SYSTEMLITERAL}"""
).format(**locals())
ENTITY = (
    f"""<!ENTITY{S}%{S}""" """(?P<PEDecl>{NAME}){S}""" """{EXTERNALID}{opS}>"""
)
r_ENTITY = re.compile(ENTITY, re.VERBOSE | re.DOTALL | re.MULTILINE)
DOCTYPE = (
    """(?P<DOCTYPE><!DOCTYPE{S}"""
    "(?P<Name>{NAME})"
    "("
    "({S}{EXTERNALID}{opS})?"  # noqa: 127
    r"(?:{S}\[(?P<IntSubset>.*)\])?"  # noqa: 127
    ")?"
    """{opS}>{opS})"""
).format(**locals())
r_DOCTYPE = re.compile(DOCTYPE, re.VERBOSE | re.DOTALL | re.MULTILINE)
COMMENTOPEN = re.compile("<!--")
COMMENTCLOSE = re.compile("-->")


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
        raise DMInvalidXMLRootElement("Cannot add info element to %s. "
                                      "Not a valid root element." % tag.localname,
                                      ReturnCodes.E_INVALID_ROOT_ELEMENT)

# -------------------------------------------------------------------

def is_xml(text):
    """Checks if a text starts with a typical XML construct

       :param str text: The text to observe
       :return: True, if text can be considered as XML, otherwise False
       :rtype: bool
    """
    logmgr_flog()

    possiblestartstrings = (re.compile(r"<\?xml"),
                            re.compile(r"<!DOCTYPE"),
                            re.compile(r"<!--"),
                            re.compile(r'<(?P<tag>(?:(?P<prefix>\w+):)?'
                                       r'(?P<name>[a-zA-Z0-9_]+))\s*'),
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
        if is_xml(source):
            return StringIO(source)
        else:
            # source isn't a file-like object nor starts with XML structure
            # so it has to be a filename
            try:
                res = StringIO(open(source, 'r').read())
            except FileNotFoundError as err:  # pylint:disable=undefined-variable
                raise DMFileNotFoundError("Could not find file {!r}.".format(err.filename),
                                          err.filename, ReturnCodes.E_FILE_NOT_FOUND)
            # pylint: enable=undefined-variable

            return res
    # TODO: Check if source is an URL; should we allow this?


def xmlsyntaxcheck(xmlfile):
    """Check if the XML file is well-formed

    :param str xmlfile: XML filename
    :return: Nothing if the XML is well-formed, otherwise it raises
       an exception
    :raises: :class:`xml.sax.SAXParseException`
    """
    from xml.sax import make_parser
    import xml.sax.handler as xmlsh

    log.debug("Try XML parser for XML well-formedness...")
    parser = make_parser()

    # Set several features of the XML parser
    featureset = (
        (xmlsh.feature_validation, False),
        (xmlsh.feature_external_ges, False),
        (xmlsh.feature_external_pes, False),
    )
    for feature, state in featureset:
        parser.setFeature(feature, state)

    parser.setContentHandler(xmlsh.ContentHandler())
    # parser.setEntityResolver(MyEntityResolver())

    # This will fail with a SAXParseException when we have a XML file
    # with syntax errors:
    parser.parse(xmlfile)
    log.debug("XML syntax check for %r ok", xmlfile)


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
    # logmgr_flog()

    # Taken from the xmllib.py
    # http://code.metager.de/source/xref/python/jython/lib-python/2.7/xmllib.py
    _S = '[ \t\r\n]+'                       # white space
    _opS = '[ \t\r\n]*'                     # optional white space
    _Name = '[a-zA-Z_:][-a-zA-Z0-9._:]*'    # valid XML name
    _QStr = r"(?:'[^']*'|\"[^\"]*\")"        # quoted XML string
    attrfind = re.compile(
        _S + '(?P<name>' + _Name + ')'
        '(' + _opS + '=' + _opS +
        '(?P<value>' + _QStr + r'|[-a-zA-Z0-9.:+*%?!\(\)_#=~]+))?')
    starttagend = re.compile(_opS + '(?P<slash>/?)>\n?')
    if roottag:
        root = '<(?P<tagname>' + roottag + ')'
    else:
        root = '<(?P<tagname>' + _Name + ')'
    return re.compile(root + '(?P<attrs>(?:' + attrfind.pattern + ')*)' +
                      starttagend.pattern)


# -------------
def getdocinfo(lines):
    """Create dict with XML information about XML

    Expects well-formed XML lines.

    :param lines: The lines to investigate
    :param int maxlines: number of lines that should be investigated
    :return: { 'header': '...', # str everything before the start tag
               'root':   '...', # str: start tag from '<' til '>'
               'offset:  1,     # Integer
             }
    :rtype: dict
    """
    result = dict(header="", root="", roottag="", offset=0)
    # Try to find DOCTYPE first
    match = r_DOCTYPE.search(lines)
    if match:
        result["header"] = lines[:match.end()]
        pos = match.end()
        lines = lines[pos:]
        result["offset"] = pos

    # Continue with root tag
    starttag = compilestarttag()
    match = starttag.search(lines)
    if not match:
        return result

    result["header"] += lines[:match.start()]
    result["roottag"] = match["tagname"]
    result["root"] = lines[slice(*match.span())]
    result["offset"] += match.start()

    log.debug("Found match: %s", match)
    return result


def findprolog(source, maxsize=-1):
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

    buf = ensurefileobj(source)
    # We read in maxsize and hope this is enough...
    xmlbuf = buf.read(maxsize)
    return getdocinfo(xmlbuf)


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


def get_property_xpath(elem):
    """Gets the xpath of an lxml.etree._Element
    :param lxml.etree._Element elem: An etree element
    :return str: XPath of the given element
    """
    elems = [ localname(i.tag) for i in elem.iterancestors() if get_namespace(i.tag) == NS['dm'] ]

    elems.reverse()
    elems = elems[1:]

    elems.append(localname(elem.tag))

    return "/".join(elems)
