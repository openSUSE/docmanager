#
# Copyright (c) 2015 SUSE Linux GmbH
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
from docmanager.core import NS, ReturnCodes
from docmanager.exceptions import DMInvalidXMLHandlerObject, DMAnalyzeInvalidFilterSyntax
from docmanager.logmanager import log
from docmanager.xmlutil import localname
from lxml import etree

class Analyzer(object):

    def __init__(self, xmlhandler):
        """Constructor for the Analyzer class

        :param XmlHandler xmlhandler: A valid XmlHandler object
        """

        self.xmlhandler = xmlhandler
        self.fields = set()

        # validate the XmlHandler object
        if self.xmlhandler is None:
            raise DMInvalidXMLHandlerObject()

    def replace_constants(self, queryformat):
        """Replaces constants

        :param string queryformat: The query format string from parameter -qf
        """

        # constants
        QueryFormConstants = [
            [ "{os.file}", self.xmlhandler.filename ]
        ]

        # replace constants
        for i in QueryFormConstants:
            queryformat = queryformat.replace(i[0], i[1])

        return queryformat

    def extract_fields(self, queryformat):
        """Extract requested properties from -qf (--queryformat)

        :param string queryformat: The query format string from parameter -qf
        :return list: the list of all requested properties from -qf (--queryformat)
        """

        fields = set()

        state = 0
        ignoreNext = False
        field = ""
        skip = -1
        c = len(queryformat)

        # algorithm for detecting the requested properties
        for idx, char in enumerate(queryformat):
            # ignore the current char if needed
            if ignoreNext == True:
                ignoreNext = False

                # if we are in the "capturing" state (1), we can just add the
                # current char to our field string
                if state == 1:
                    field += char

                continue

            # skip the current char if needed (user for escaping with '{')
            if skip != -1 and skip == idx:
                skip = -1
                continue

            # this is also an escape detection but it is actually no longer needed.
            # can be removed in future versions
            if char == '\\':
                ignoreNext = True
                continue

            # if we are not in any capturing state (1), we jump into this condition if
            # we found a '{'. '{' means, if there is not a second '{' after the current
            # '{', this should be a capturing instruction
            if char == '{' and state == 0:
                # if we are not at the end of the string, we have a look onto the next
                # character. If the next character also contains a '{', we are in a
                # 'ignore everything in it' statement
                if c-1 != idx:
                    if queryformat[idx+1] == '{':
                        # ok, we are in a 'ignore everything' statement. we skip now the next
                        # character (because that's the '{') and jump into the 'ignore everything'
                        # state (state 3)
                        skip = idx+1
                        state = 3
                    else:
                        # the next character is not a  'ignore everything' instruction. So we're
                        # in a 'capturing' state. (state 1)
                        state = 1
                else:
                    # we reached the end of the string - just jump into the 'capturing' statement
                    state = 1
                continue

            # detect the end of the 'capturing' sequence. (the current character has to be a '}' and
            # we also have to be in the 'capturing' state)
            if char == '}' and state == 1:
                state = 0

                # we copy our captured string into our 'fields' list - that is really important
                # because we need all requested properties
                fields.add(field)

                # clear the string because we need it for the next capturing sequence
                field = ""
                continue

            # detect the end of a 'ignore everything' sequence
            if char == '}' and state == 3:
                # check if we reached the end of the string - if not, look onto the next character.
                # if the next character is a '}', we can leave the 'ignore everything' sequence.
                # if not, just skip it
                if c-1 != idx:
                    if queryformat[idx+1] == '}':
                        # go back into the 'nothing' (append until we found a new instruction)
                        # statement
                        state = 0
                        skip = idx+1

            # if we're in the 'capturing' sequence, we have to append the current character
            # to our 'field' string
            if state == 1:
                field += char

        # make the fields list public - this will be needed for some other functions
        # like 'fetch_data' since there is no option for passing the 'fields' list
        # over the argument list
        self.fields = fields
        return self.fields

    def fetch_data(self, filter=None, sort=None, default_output=None):
        """Fetches the requested properties from self.extract_fields()

        :param list filter: The filter list from args.filter (can be None if we don't need the filter function)
        :param string sort: The sort item for the sort function (this is a property - can be None if we don't
                            want to use the sort function)
        :return dict: a dictionary with all properties and their values
        """

        data = dict()

        if self.fields:
            # build the xpath for selecting all needed properties
            xpath = "*[self::dm:" + " or self::dm:".join(self.fields)
            if sort is None:
                xpath += "]"
            else:
                # when the args.sort is set, we can append that string to our
                # xpath. that's needed if we want to display 'maintainer' but
                # sort
                xpath += " or self::dm:" + sort + "]"
                self.fields.add(sort)

            # if there are invalid characters in the xpath, lxml throws an exception.
            # We have to catch that.
            try:
                data = { localname(e.tag): e.text  for e in self.xmlhandler.dm.xpath(xpath, namespaces=NS) }
            except etree.XPathEvalError:
                log.error("The given XML properties in --sort/-s or --queryformat/-qf are invalid.")
                sys.exit(ReturnCodes.E_INVALID_XML_PROPERTIES)

            # loop over all 'properties' and fetch their values from the XML file. properties
            # without values will become an empty string
            for f in self.fields:
                data.setdefault(f, data.get(f, ""))

                if data[f] is None:
                    if default_output is None:
                        data[f] = ''
                    else:
                        data[f] = default_output

            if filter:
                filters = dict()
                filters_xpath = ""

                for idx, f in enumerate(filter):
                    try:
                        # validate the filter syntax of any given filter
                        mode, prop, condition = self.validate_filter(f)

                        # save the details about a filter in a dictionary
                        filters[prop] = dict()
                        filters[prop]['mode'] = mode
                        filters[prop]['condition'] = condition

                        if idx == 0:
                            filters_xpath += "self::dm:" + prop
                        else:
                            filters_xpath += " or self::dm:" + prop
                    except DMAnalyzeInvalidFilterSyntax:
                        # syntax is wrong
                        log.error("Invalid syntax in filter: '{}'".format(f))
                        log.error("Look into the manual page for more information about using filters.")
                        sys.exit(ReturnCodes.E_ANALYZE_FILTER_INVALID_SYNTAX)

                # catch the values of the filter properties
                f_xpath = { localname(e.tag): e.text  for e in self.xmlhandler.dm.xpath("*[{}]".format(filters_xpath), namespaces=NS) }

                for f in filters:
                    # if the filter property was not found in the XML file -> the filter does
                    # not match and we have to return an empty dictionary
                    if f not in f_xpath:
                        return {}

                        f_xpath[f] = ''

                    # condition checks
                    if filters[f]['mode'] == '+':
                        if f_xpath[f] != filters[f]['condition']:
                            return {}
                    elif filters[f]['mode'] == '-':
                        if f_xpath[f] == filters[f]['condition']:
                            return {}

        return data

    def validate_filter(self, filter):
        """Validates the syntax of a filter (example: +property=value, -property=value, property=value)

        :param string filter: One single filter (not the filter list)
        :return list: the mode, the property, the filter property condition
        """

        # look for the operator (if no valid operator was found, use '+')
        if filter[0] != '+' and filter[0] != '-':
            filter = "+{}".format(filter)

        # detect the first occurrence of the character '='
        pos = filter.find("=")
        if pos == -1:
            raise DMAnalyzeInvalidFilterSyntax()

        # extract the property and the condition
        prop = filter[1:-(len(filter)-pos)]
        cond = filter[pos+1:]

        return [filter[0],prop,cond]

    def format_output(self, source, data):
        """formats the output of the -qf (--queryformat)

        :param string source: The query format string (-qf/--queryformat) from the command line
        :param string data: the data items from fetch_data
        :return string: the formatted query format string
        """

        if data:
            # iterate through each item and replace the properties with their values
            for i in data:
                source = source.replace('{' + i + '}', data[i])

        return source
