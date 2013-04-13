# Copyright 2010-2013,
# Steve Milner <stevem@gnulinux.net>
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

import json

from argparse import ArgumentParser

import sqlalchemy.orm
import sqlalchemy.sql.expression

from victims.config import Config
from victims.db import CVEMap, Connection
from victims.scripts import _get_default_conf_loc, _require_conf


def main():
    """
    Prints out metadata for a specific package-version.
    """
    default_conf = _get_default_conf_loc()
    parser = ArgumentParser()
    parser.add_argument(
        "-c", "--config", dest="config",
        default=default_conf, help="what config file to use",
        metavar="CONFIG")
    parser.add_argument(
        "-p", "--package-name", dest="name",
        help="Name of the package", metavar="NAME")
    parser.add_argument(
        "-v", "--package-version", dest="version",
        help="Version of the package", metavar="VERSION")
    parser.add_argument(
        "-j", "--json-output", dest="json",
        action="store_true", help="Outout as json")

    args = parser.parse_args()

    if not args.name or not args.version:
        parser.print_help()
        parser.error('You must provide a name and version')

    _require_conf(args, parser)

    conf = Config(args.config)
    c = Connection(conf)

    try:
        results = c.session.query(CVEMap).filter(
            CVEMap.name == args.name).filter(
                CVEMap.version == args.version)
        if args.json:
            data = []
            for result in results:
                inst = result.__dict__
                del inst['_sa_instance_state']
                data.append(inst)
            print json.dumps(data)
        else:
            for result in results:
                print("Hash: %s\nVendor: %s\nCVES: %s" % (
                    result.hash, result.vendor, result.cves))
    except (IndexError, sqlalchemy.orm.exc.NoResultFound), ex:
        print('An error has occured: %s' % ex)
        raise SystemExit(1)


if __name__ == '__main__':
    main()
