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

import os
import random
from glob import glob

class TmpFile():
    
    filename = ""
    
    def __init__(self):
        self.create()

    def create(self):
        # generate a tmp file name
        self.filename = self.generate_filename()
        
        # just create the tmp file
        t = open(self.filename, 'w')
        t.close()
    
    def write(self, content):
        with open(self.filename, 'w') as t:
            t.write(content)
    
    def read(self):
        with open(self.filename, 'r') as t:
            content = t.read()
            return content

        return ""
    
    def generate_filename(self):
        chars = "aAbBcCdD9eEfFgG8hHiI7jJkKl6LmMn5NoOpP4qQrRs3StTuUv2VwWx1XyYzZ"
        out = ""

        i = 1
        while i <= 8:
            out += chars[random.randrange(1,len(chars))]
            i += 1

        return "/tmp/docmanager_{}".format(out)

def clear_tmpdir():
    """
    Deletes all old docmanager tmp files
    """
    files = glob("/tmp/docmanager_*")
    if len(files):
        for i in files:
            os.remove(i)
