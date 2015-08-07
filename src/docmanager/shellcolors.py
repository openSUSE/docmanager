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

from functools import wraps

def shellcolor(func):
    """Decorator for shell color functions

    :param func: Function to decorate
    :return: decorated function
    """
    @wraps(func)
    def wrapped(text):
        return "\033[01;{0}\033[00m".format(func(text))
    return wrapped

@shellcolor
def green(text):
    """Create green text string

    :param string text: text to print in green
    :return: a green string
    """
    return "32m{0}".format(text)

@shellcolor
def red(text):
    """Create red text string

    :param string text: text to print in red
    :return: a red string
    """
    return "31m{0}".format(text)

@shellcolor
def yellow(text):
    """Create yellow text string

    :param string text: text to print in yellow
    :return: a yellow string
    """
    return "33m{0}".format(text)