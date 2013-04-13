# Copyright 2010-2013,
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

import json
import urllib

from argparse import ArgumentParser

import sqlalchemy.orm
import sqlalchemy.sql.expression

from victims.config import Config
from victims.db import CVEMap, Connection
from victims.scripts import _get_default_conf_loc, _require_conf


def main():
    """
    Updates the database.
    """
    default_conf = _get_default_conf_loc()
    parser = ArgumentParser()
    parser.add_argument(
        "-c", "--config", dest="config",
        default=default_conf, help="what config file to use",
        metavar="CONFIG")
    parser.add_argument(
        "-f", "--force-version", dest="version",
        help="Force update from a specific version",
        metavar="VERSION")

    args = parser.parse_args()
    _require_conf(args, parser)

    conf = Config(args.config)
    c = Connection(conf)

    if args.version:
        current_db = int(args.version)
    else:
        try:
            current_db = c.session.query(CVEMap).order_by(
                sqlalchemy.sql.expression.desc(
                    CVEMap.db_version))[0].db_version
        except (IndexError, sqlalchemy.orm.exc.NoResultFound):
            current_db = 0

    # Get the update data
    try:
        data = urllib.urlopen(
            conf['service']['updateurl'] + str(current_db) + "/").read()
        for hash in [x['fields'] for x in json.loads(data)]:
            try:
                c.session.add(CVEMap(
                    hash['hash'], hash['name'], hash['version'],
                    hash['vendor'], hash['cves'], hash['db_version'],
                    hash['format']))
                c.session.flush()
            except sqlalchemy.exc.IntegrityError:
                # Hash already exists ... update it
                cvemap = c.session.query(CVEMap).filter(
                    CVEMap.hash == hash['hash']).one()
                cvemap.name = hash['name']
                cvemap.version = hash['version']
                cvemap.vendor = hash['vendor']
                cvemap.cves = hash['cves']
                cvemap.db_version = hash['db_version']
                cvemap.format = hash['format']
                c.session.add(cvemap)
                c.session.flush()
    except Exception, ex:
        print("An error occured while trying to update.\n\nError:\n" + str(ex))

    try:
        # Get the data to remove
        rm_url = conf['service']['removeurl'] + str(current_db) + "/"
        rm_data = urllib.urlopen(rm_url).read()
        for rm_hash in [x['fields'] for x in json.loads(rm_data)]:
            try:
                cvemap = c.session.query(CVEMap).filter(
                    CVEMap.hash == hash['hash']).one()
                c.session.delete(cvemap)
                c.flush()
            except Exception, ex:
                # Could not remove an item ... already removed?
                pass
    except KeyError:
        # Removing is not configured
        pass


if __name__ == '__main__':
    main()
