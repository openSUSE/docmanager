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

import json
from prettytable import PrettyTable


def textrenderer(data, **kwargs):
    """Normal text output

    :param list data: Filename with properties
                      syntax: [(FILENAME, {PROPERTIES}), ...]
    :param dict kwargs: for further customizations
    :return: rendered output
    :rtype: str
    """
    if data is None:
        return

    for d in data:
        props = d[1]
        props = " ".join([ "%s=%s" % (key, value) for key, value in props.items()])
        print("{} -> {}".format(d[0], props))


DEFAULTRENDERER = textrenderer

def tablerenderer(data, **kwargs):
    raise NotImplementedError

def jsonrenderer(data, **kwargs):
    raise NotImplementedError

def xmlrenderer(data, **kwargs):
    raise NotImplementedError

def getrenderer(fmt):
    """Returns the renderer for a specific format

    :param str fmt: format ('text', 'table', 'json', or 'default')
    :return: function of renderer
    :rtype: function
    """
    # Available renderers
    renderer = {
        'default': textrenderer,
        'text':    textrenderer,
        'table':   tablerenderer,
        'json':    jsonrenderer,
        'xml':     xmlrenderer,
    }

    return renderer.get(fmt, DEFAULTRENDERER)