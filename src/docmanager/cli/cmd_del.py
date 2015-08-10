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


def del_subcmd(subparsers, propargs, filesargs):
    """Create the 'del' subcommand

    :param subparsers:      Subparser for all subcommands
    :param dict propargs:   Dict with action and help for
                            default properties
    :param dict filesargs:  Dict for FILE argument

    """
    pdel = subparsers.add_parser('del',
                                 aliases=['d'],
                                 help='Delete properties from XML documents'
                                 )
    pdel.add_argument('-p', '--properties', **propargs)
    pdel.add_argument("files", **filesargs)
