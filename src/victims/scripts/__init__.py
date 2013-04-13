# Copyright 2010,
# Steve 'Ashcrow' Milner <stevem@gnulinux.net>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
Package containing functions which will be exposed as command line scripts.
"""

__docformat__ = 'restructuredtext'


import os.path


def _get_default_conf_loc():
    """
    Returns a default location where the config might be.
    """
    # Default items which must be generated
    home = os.path.sep.join([os.path.expanduser('~'), '.victims'])
    default_conf = os.path.sep.join([home, 'config.ini'])
    return default_conf


def _require_conf(options, parser):
    """
    Checks to verify th config exists, else prints help and exists.

    :Parameters:
       - `options`: the options the parser returned
       - `parser`: the option parser itself
    """
    if not os.path.isfile(options.config):
        parser.print_help()
        print("\n" + options.config + " is not valid or does not exist ...")
        raise SystemExit(1)
