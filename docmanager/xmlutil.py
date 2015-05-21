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
import re
import os

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


def root_sourceline(source, resolver=None):
    """Gets the line number of the root element

    :param source:
    :type source: filename, file object, or file-like object
    :param etree.Resolver resolver: custom resolver
    :return: line number, column
    :rtype: tuple
    """
    # See https://gist.github.com/tomschr/6ecaaf69231dfbc9517a
    # for an alternative implementation with SaX

    parser = etree.XMLParser(remove_blank_text=False,
                             resolve_entities=False,
                             dtd_validation=False,
                             load_dtd=False)
    if resolver is not None:
        parser.resolvers.add(resolver)

    # Get first an "approximation" of where we could find it
    maxsourceline = etree.parse(source, parser).getroot().sourceline

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
    # Therefor we need to go back until we find start-tag
    #
    # See thread in
    # https://mailman-mail5.webfaction.com/pipermail/lxml/2015-May/007518.html

    # Find any start-tag which match this regex:
    starttag = re.compile(r'<(?P<tag>(?:(?P<prefix>\w+):)?(?P<name>\w+))\s*')

    if hasattr(source, 'seek'):
        # We have a seek() method, so it's a file-like object
        # reset current position
        source.seek(0)
    elif os.path.exists(source):
        # if the string exists as a file, it must be a path to a file
        source = io.StringIO(open(source, 'r').read())
    else:
        # Anything else is a string
        source = io.StringIO(source)

    # Read lines until maxsourceline is reached
    header = [next(source) for _ in range(maxsourceline)]

    checkline = []
    # Iterate in reverse order to find a match for our start-tag
    for i, line in enumerate(reversed(header)):
        checkline.insert(0, line)
        match = starttag.match("".join(checkline))
        if match:
            break
    return maxsourceline - i, match.start()


def prolog(source, resolver=None):
    """Extract prolog of source and change position of source

    :param source:
    :type source: filename, file object, or file-like object
    :param etree.Resolver resolver: custom resolver
    :return: tuple of: length of header, sourceline, and header itself
    :rtype: (int, int, str)
    """
    rootnr, _ = root_sourceline(source, resolver)
    if hasattr(source, 'seek'):
        # We have a seek() method, so it's a file-like object
        # reset current position
        source.seek(0)

    header = "".join([next(source) for _ in range(rootnr)])

    if hasattr(source, 'seek'):
        return source.seek(len(header)), rootnr, header
    else:
        return len(header), rootnr, header
