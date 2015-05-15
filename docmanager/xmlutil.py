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
    :return: tuple of length of header and header itself
    :rtype: (int, str)
    """
    rootnr = root_sourceline(source, resolver)

    header = "".join([ line for nr, line in enumerate(source, 1)
                       if nr < rootnr ]
                    )
    if hasattr(source, 'seek'):
        return source.seek(len(header)), header
    else:
        return len(header), header