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

def analyze_subcmd(subparsers, queryformat, filters, sort, quiet, stop_on_error, default_output, filesargs):
    """Create the 'analyze' subcommand

    :param subparsers:           Subparser for all subcommands
    :param queryformat:          The queryformat
    :param dict filesargs:       Dict for FILE argument

    """
    panalyze = subparsers.add_parser('analyze',
                        aliases=['a'],
                        help='Analyzes the given XML files.'
                    )
    panalyze.add_argument('-qf', '--queryformat', **queryformat)
    panalyze.add_argument('-f', '--filter', **filters)
    panalyze.add_argument('-s', '--sort', **sort)
    panalyze.add_argument('--stop-on-error', **stop_on_error)
    panalyze.add_argument('-q', '--quiet', **quiet)
    panalyze.add_argument('-do', '--default-output', **default_output)
    panalyze.add_argument("files", **filesargs)
