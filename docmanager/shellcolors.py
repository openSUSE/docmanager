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

from docmanager.logmanager import logmgr_flog

class ShellColors:
    
    def __init__(self):
        self.col_red = "\033[01;31m{0}\033[00m"
        self.col_green = "\033[1;32m{0}\033[00m"
        
    def make_red(self, text):
        """This function appends a red color code to the given text
        :param string text: the wanted text
        """
        logmgr_flog()

        return self.col_red.format(text)

    def make_green(self, text):
        """This function appends a green color code to the given text
        :param string text: the wanted text
        """
        logmgr_flog()

        return self.col_green.format(text)

    def print_red(self, text):
        """This function appends a red color code to the given text and prints it
        :param string text: the wanted text
        """
        logmgr_flog()

        print(self.make_red(text))

    def print_green(self, text):
        """This function appends a green color code to the given text and prints it
        :param string text: the wanted text
        """
        logmgr_flog()

        print(self.make_green(text))
