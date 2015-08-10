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


def config_subcmd(subparsers):
    """Create the 'config' subcommand

    :param subparsers:           Subparser for all subcommands
    """

    pconfig = subparsers.add_parser('config',
                                    aliases=['c'],
                                    help='Modify tool for config files.'
                                    )
    pconfig.add_argument('-s', '--system',
                         action='store_true',
                         help='Uses the system config file.'
                         )
    pconfig.add_argument('-u', '--user',
                         action='store_true',
                         help='Uses the user config file.'
                         )
    pconfig.add_argument('-r', '--repo',
                         action='store_true',
                         help='Uses the repository config file of the current repository.'
                              ' (The user has to be in a git repository!)')
    pconfig.add_argument('-o', '--own',
                         metavar='FILE',
                         action='store',
                         help='Uses a specified config file.'
                         )
    pconfig.add_argument('property',
                         metavar='PROPERTY',
                         help='Property (Syntax: section.property)')
    pconfig.add_argument('value',
                         metavar='VALUE',
                         nargs='?',
                         help='Value of the property.')
