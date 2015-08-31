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

import datetime
import os.path

class FileUtil(object):

	def __init__(self, filename):
		# set the default variables
		self.filename = filename

	def get_mtime(self, with_ms=False):
		"""Returns the last modify time
		:param bool with_ms: With or without milliseconds
		:return mixed(float|int): The last modify time
		"""

		if with_ms:
			return int(os.path.getmtime(self.filename))

		return os.path.getmtime(self.filename)

	def get_mtime_format(self, formatstr):
		"""Returns the last modify time as a string
		:param str formatstr: Format string like: %Y-%m-%d %H:%M:%S
		:return str: Formatted string
		"""

		# read the last modify time
		mtime = self.get_mtime()
		return datetime.datetime.fromtimestamp( \
					mtime \
				).strftime(formatstr)
