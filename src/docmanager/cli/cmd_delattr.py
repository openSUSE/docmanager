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

from ..core import BT_ELEMENTLIST


def delattr_subcmd(subparsers, stop_on_error, prop, attributes, filesargs):
    """Creates the 'set-attr' subcommand

    :param subparsers:           Subparser for all subcommands
    :param dict stop_on_error:   Dict for the --stop-on-error option
    :param str prop:             The property which gets modified
    :param list attributes:      A list of all attributes
    :param dict filesargs:       Dict for FILE argument

    """
    pattrget = subparsers.add_parser('del-attr',
                                 aliases=['da'],
                                 help='Deletes an attribute from a property/XML-Tag.'
                                 )
    pattrget.add_argument('--stop-on-error', **stop_on_error)
    pattrget.add_argument('-p', '--property')
    pattrget.add_argument('-a', '--attributes', **attributes)
    pattrget.add_argument("files", **filesargs)
