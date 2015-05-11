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
