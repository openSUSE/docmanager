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


def set_subcmd(subparsers, stop_on_error, propargs, mainprops, filesargs):
    """Create the 'set' subcommand

    :param subparsers:           Subparser for all subcommands
    :param dict stop_on_error:   Dict for the --stop-on-error option
    :param dict propargs:        Dict with action and help for default
                                 properties
    :param tuple mainprops:      Tuple of short and long options of
                                 default properties
    :param dict filesargs:       Dict for FILE argument

    """
    pset = subparsers.add_parser('set',
                                 aliases=['s'],
                                 help='Set key=value property (one or more) '
                                      ' to delete the key let the value blank.'
                                 )
    pset.add_argument('-B', '--bugtracker',
                      action='store_true')
    pset.add_argument('--stop-on-error', **stop_on_error)
    pset.add_argument('-p', '--properties', **propargs)

    for options in mainprops:
        pset.add_argument(*options,
                          help='Sets the property "{}"'.format(options[1][2:])
                          )

    # TODO: Do we really need that?
    pset.add_argument('--repository',
                      help='Sets the property "repository"'
                      )

    for item in BT_ELEMENTLIST:
        _, option = item.split('/')
        pset.add_argument('--bugtracker-{}'.format(option),
                          help='Set the property "bugtracker/{}" '
                               'for the given documents.'.format(option)
                          )

    pset.add_argument("files", **filesargs)
