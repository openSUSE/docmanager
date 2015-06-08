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

NS = {
        "d":"http://docbook.org/ns/docbook",
        "dm":"urn:x-suse:ns:docmanager"
}

DefaultDocManagerProperties = [
        "maintainer",
        "status",
        "deadline",
        "priority",
        "translation",
        "languages"
]

class ReturnCodes():
    E_OK = 0
    E_FILE_NOT_FOUND = 1
    E_COULD_NOT_SET_VALUE = 2
    E_XML_PARSE_ERROR = 3
    E_DAPS_ERROR = 4
    E_INVALID_USAGE_KEYVAL = 5
    E_METHOD_NOT_IMPLEMENTED = 6
    E_INFO_ELEMENT_MISSING = 7
    E_CALL_WITHOUT_PARAMS = 8
    E_INVALID_XML_DOCUMENT = 9
    E_WRONG_INPUT_FORMAT = 10
    E_PERMISSION_DENIED = 11

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
              'informaltable', 'inlinemediaobject', 'itemizedlist', 'legalnotice',
              'literallayout', 'mediaobject', 'methodsynopsis', 'msg', 'msgexplan',
              'msgmain', 'msgrel', 'msgset', 'msgsub', 'note', 'orderedlist',
              'para', 'part', 'partintro', 'personblurb', 'procedure',
              'productionset', 'programlisting', 'programlistingco',
              'programlistingco', 'qandadiv', 'qandaentry', 'qandaset',
              'qandaset', 'refentry', 'refsect1', 'refsect2', 'refsect3',
              'refsection', 'refsynopsisdiv', 'revhistory', 'screen', 'screenco',
              'screenco', 'screenshot', 'sect1', 'sect2', 'sect3', 'sect4', 'sect5',
              'section', 'segmentedlist', 'set', 'setindex', 'sidebar',
              'simpara', 'simplelist', 'simplesect', 'step', 'stepalternatives',
              'synopsis', 'table', 'task', 'taskprerequisites', 'taskrelated',
              'tasksummary', 'textdata', 'textobject', 'tip', 'toc', 'tocdiv',
              'topic', 'variablelist', 'videodata', 'videoobject', 'warning')