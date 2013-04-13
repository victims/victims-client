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
Database related classes.
"""

__docformat__ = 'restructuredtext'

import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.ext.declarative

# Create the base class
Base = sqlalchemy.ext.declarative.declarative_base()


class CVEMap(Base):
    """
    CVEMap database binding.
    """
    __tablename__ = 'cvemap'

    hash = sqlalchemy.Column(sqlalchemy.String(512), primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    version = sqlalchemy.Column(sqlalchemy.String)
    vendor = sqlalchemy.Column(sqlalchemy.String)
    cves = sqlalchemy.Column(sqlalchemy.String)
    db_version = sqlalchemy.Column(sqlalchemy.Integer)
    format = sqlalchemy.Column(sqlalchemy.String(10), index=True)

    def __init__(self, hash, name, version, vendor, cves, db_version, format):
        """
        Creates the CVEMap instance.

        :Parameters:
           - `hash`: unique hash to identify the item with.
           - `name`: name of the project/package.
           - `version`: version of the project/package.
           - `vendor`: vendor name.
           - `cves`: comma seperated list of CVE's
           - `db_version`: the db_version this hash is part of
           - `format`: the package format
        """
        self.hash = hash
        self.name = name
        self.version = version
        self.vendor = vendor
        self.cves = cves
        self.db_version = db_version
        self.format = format

    def __repr__(self):
        """
        String representation of the instance.
        """
        return "<CVEMap(%s)>" % self.hash


class Connection(object):
    """
    Database connection.
    """

    def __init__(self, config):
        """
        Creates an instance of the database connection.

        :Parameters:
           - `config`: the configuration object.
        """
        # Connect to the database using the configuration file
        self.engine = sqlalchemy.engine_from_config(
            config['database'], prefix='')
        self.metadata = Base.metadata
        self.metadata.create_all(self.engine)
        self.session = sqlalchemy.orm.sessionmaker(
            autoflush=True, autocommit=True, bind=self.engine)()
