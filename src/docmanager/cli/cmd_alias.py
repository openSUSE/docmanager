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

from ..core import DEFAULTSUBCOMMANDS


def alias_subcmd(subparsers):
    """Create the 'alias' subcommand

    :param subparsers:           Subparser for all subcommands
    """

    palias = subparsers.add_parser('alias',
                                   aliases=['al'],
                                   help='Modify tool for aliases.')
    _choices = ('set', 'del', 'get', 'list')
    palias.add_argument('alias_action',
                        metavar='ACTION',
                        choices=_choices,
                        help='The action you want to perform; use one of '
                             '{}'.format(", ".join(_choices)))
    cfgfile_group = palias.add_mutually_exclusive_group(required=True)
    cfgfile_group.add_argument('-s', '--system',
                               action='store_const',
                               const=1,
                               dest="method",
                               help='Uses the system config file.'
                               )
    cfgfile_group.add_argument('-u', '--user',
                               action='store_const',
                               const=2,
                               dest="method",
                               help='Uses the user config file.'
                               )
    cfgfile_group.add_argument('-r', '--repo',
                               action='store_const',
                               const=3,
                               dest="method",
                               help='Uses the repository config file of the current repository.'
                                    ' (The user has to be in a git repository!)'
                               )
    cfgfile_group.add_argument('-o', '--own',
                               metavar='FILE',
                               action='store', help='Uses a specified config file.')
    palias.add_argument('-f', '--format',
                        choices=('table', 'json', 'xml'),
                        help='Set the output format'
                        )
    palias.add_argument('alias', metavar='ALIAS',
                        nargs='?',
                        help='Name of the alias')
    palias.add_argument('command',
                        metavar='COMMAND',
                        nargs='?',
                        help='Command for the alias.'
                        )


def rewrite_alias(args):
    """Rewrite aliases

    :param argparse.Namespace args: Parsed arguments
    """
    actions = DEFAULTSUBCOMMANDS
    args.action = actions.get(args.action)
