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
    :type source: file name/path, file object, file-like object, URL
    :param etree.Resolver resolver: custom resolver
    :return: line number
    :rtype: int
    """
    parser = etree.XMLParser(remove_blank_text=False,
                             resolve_entities=False,
                             dtd_validation=False,
                             load_dtd=False)
    if resolver is not None:
        parser.resolvers.add(resolver)
    tree = etree.parse(source, parser)
    return tree.getroot().sourceline


def prolog(source, resolver=None):
    """Extract prolog of source and change position of source

    :param source:
    :type source: file name/path, file object, file-like object, URL
    :param etree.Resolver resolver: custom resolver
    :return: tuple of: length of header, sourceline, and header itself
    :rtype: (int, str)
    """
    rootnr = root_sourceline(source, resolver)

    header = "".join([ line for nr, line in enumerate(source, 1)
                       if nr < rootnr ]
                    )
    if hasattr(source, 'seek'):
        return source.seek(len(header)), rootnr, header
    else:
        return len(header), rootnr, header