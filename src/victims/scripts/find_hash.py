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
Searches for files and produces hashes from an archive.
"""

__docformat__ = 'restructuredtext'

import os
import re

from optparse import OptionParser

from victims import PackageFinder, HashGenerator


def main():
    """
    Find sha512sum's in archives.
    """
    parser = OptionParser()
    parser.add_option("-n", "--name", dest="name",
        help="name or regex of the file(s) to look for", metavar="NAME")

    (options, args) = parser.parse_args()

    try:
        rx = re.compile(options.name)
    except Exception, ex:
        parser.print_help()
        print('\nYou must provide a string or valid regex with --name/-n')
        raise SystemExit(1)

    finder = PackageFinder(look_inside=True)
    hasher = HashGenerator()

    # For each path ...
    for check_path in args:
        data, formats = finder(check_path)
        for package in data:
            result = rx.findall(os.path.basename(package.name))
            if result:
                print("- " + " ".join([hasher(package.path), str(package)]))


if __name__ == '__main__':
    main()
