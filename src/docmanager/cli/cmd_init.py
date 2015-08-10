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


def init_subcmd(subparsers, stop_on_error, propargs, mainprops, filesargs):
    """Create the 'init' subcommand

    :param subparsers:           Subparser for all subcommands
    :param dict stop_on_error:   Dict for the --stop-on-error option
    :param dict propargs:        Dict with action and help for default
                                 properties
    :param tuple mainprops:      Tuple of short and long options of default
                                 properties
    :param dict filesargs:       Dict for FILE argument
    """
    # 'init' command for the initialization
    pinit = subparsers.add_parser('init',
                                  aliases=['i'],
                                  help='Initializes an XML document with '
                                       'predefined properties.')
    pinit.add_argument('--force',
                       action='store_true',
                       help='This option forces the initialization.'
                       )
    pinit.add_argument('--stop-on-error', **stop_on_error)
    pinit.add_argument('--with-bugtracker',
                       action='store_true',
                       help='Adds a bugtracker structure to an XML file.'
                       )
    pinit.add_argument('-p', '--properties', **propargs)

    for options in mainprops:
        pinit.add_argument(*options,
                           help='Sets the property "{}"'.format(options[1][2:])
                           )

    # TODO: Do we really need that?
    pinit.add_argument('--repository',
                       help='Sets the property "repository".'
                       )
    for item in BT_ELEMENTLIST:
        _, option = item.split('/')
        pinit.add_argument('--bugtracker-{}'.format(option),
                           help='Sets the property '
                                '"bugtracker/{}".'.format(option)
                           )

    pinit.add_argument("files", **filesargs)
