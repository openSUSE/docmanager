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

__all__ = ['DMInvalidXMLHandlerObject',
           'DMAnalyzeInvalidFilterSyntax',
           'DMConfigFileNotFound',
           'DMNotDocBook5File',
           'DMXmlParseError',
           'DMInvalidXMLRootElement',
           'DMFileNotFoundError',
           'DMPropertyNotFound',
           ]


class DMInvalidXMLHandlerObject(Exception):
	pass


class DMAnalyzeInvalidFilterSyntax(Exception):
	pass


class DMConfigFileNotFound(Exception):
	pass


class DMNotDocBook5File(Exception):
	def __init__(self, errorstr, error):
		self.errorstr = errorstr
		self.error = error	


class DMXmlParseError(Exception):
	def __init__(self, errorstr, error):
		self.errorstr = errorstr
		self.error = error


class DMInvalidXMLRootElement(Exception):
	def __init__(self, errorstr, error):
		self.errorstr = errorstr
		self.error = error


class DMFileNotFoundError(Exception):
	def __init__(self, errorstr, filename, error):
		self.errorstr = errorstr
		self.error = error
		self.filename = filename


class DMPropertyNotFound(Exception):
	def __init__(self, filename, prop):
		self.filename = filename
		self.property = prop
