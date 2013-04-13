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
Functions which will be exposed as command line scripts.
"""

__docformat__ = 'restructuredtext'

from optparse import OptionParser

import sqlalchemy.orm
import sqlalchemy.sql.expression

from victims import PackageFinder, HashGenerator, Packages
from victims.config import Config
from victims.db import CVEMap, Connection
from victims.scripts import _get_default_conf_loc, _require_conf


OK_EXIT = 0
FOUND_VULNERABILITIES_EXIT = 1
INTERNAL_ERROR_EXIT = 2


def main():
    """
    Scans packages.
    """
    # Default items which must be generated
    default_conf = _get_default_conf_loc()

    parser = OptionParser()
    parser.add_option(
        "-c", "--config", dest="config",
        default=default_conf, help="what config file to use",
        metavar="CONFIG")
    parser.add_option(
        "-l", "--look-inside", dest="look_inside",
        action="store_true", default=False,
        help="If packages should be scanned for hidden packages")

    (options, args) = parser.parse_args()
    _require_conf(options, parser)

    conf = Config(options.config)
    c = Connection(conf)

    finder = PackageFinder(look_inside=options.look_inside)
    hasher = HashGenerator()

    count = 0
    # For each path ...
    for check_path in args:
        data, formats = finder(check_path)
        count += len(data)
        # Add each package in a packages object so we can query faster
        packages = Packages()
        for package in data:
            packages.append(hasher(package.path), package)

        # Run the query in one execution
        results = c.session.query(CVEMap).filter(CVEMap.hash.in_(
            packages.keys())).filter(CVEMap.format.in_(formats))

        try:
            # Print result if we have a match
            if results.count():
                # For each result we have ...
                for result in results:
                    # For each package that matches the hash (as we may have
                    # copies of the same package ... I'm looking at you JAVA)
                    for package in packages[result.hash]:
                        print(str(package) + ": " + result.cves)
        except sqlalchemy.exc.OperationalError, oe:
            print("\nError occured (bad database?)\n\nError:\n" + str(oe))
            raise SystemExit(INTERNAL_ERROR_EXIT)

    print("Scanned " + str(count) + " packages")
    if results.count() > 0:
        raise SystemExit(FOUND_VULNERABILITIES_EXIT)
    raise SystemExit(OK_EXIT)


if __name__ == '__main__':
    main()
