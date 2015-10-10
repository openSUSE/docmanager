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

from contextlib import contextmanager

@contextmanager
def ignored(*exceptions):
    """Ignore any exception

       :param tuple exceptions: Sequence of exceptions which are ignored

       >>> import os
       >>> with ignored(OSError):
       ...    os.remove("does_not_exist.abc")
    """
    try:
        yield
    except exceptions:
        pass


@contextmanager
def logandexit(msg, rcode, *exceptions):
    """Catch exception, log it, and exit with error code

    :param str/list msg: Error string or list of error strings to pass to log.error
    :param rcode: return value
    :param tuple exceptions: Sequence of exceptions which are caught
    """
    if isinstance(msg, str):
        msg = (msg,)

    try:
        yield
    except exceptions:
        for m in msg:
            log.error(m)
        sys.exit(rcode)
