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

from configparser import ConfigParser
from os import makedirs, path

class Config(object):

    def __init__(self):
        self.config_path = path.expanduser('~/.config/docmanager')
        self.config_file = 'docmanager.conf'
        self.config_path_full = '{}/{}'.format(self.config_path, self.config_file)
        self.config = ConfigParser()
        self.parse_config()

    def parse_config(self):
        if path.isfile(self.config_path) != True:
            self.create_config()
        else:
            self.config.read(self.config_path)

    def create_config(self):
        # just create the file - the config file is currently not needed
        if not path.exists(self.config_path):
            makedirs(self.config_path)
            open(self.config_path_full, 'w+').close()
        else:
            open(self.config_path_full, 'w+').close()
