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
Unittest for configuration.
"""

import unittest

from victims.db import CVEMap, Connection


class TestStorage(unittest.TestCase):
    """
    Unittests for the storage (database) module.
    """

    def setUp(self):
        """
        Create an in-memory database for each test.
        """
        self._config = {
            'database': {
                'url': 'sqlite://',
                'convert_unicode': True,
                'echo': False,
            },
        }
        self.connection = Connection(self._config)

    def tearDown(self):
        """
        Delete the database after each test.
        """
        del self.connection

    def test_connection(self):
        """
        Make sure the connection works as expected.
        """
        self.assertRaises(TypeError, Connection, [])
        local_config = self._config
        local_config['database']['echo'] = True
        local_con = Connection(local_config)
        assert local_con.session
        assert local_con.metadata
        assert local_con.engine

    def test_create_and_retrieve_hash(self):
        """
        Verify creation and getting hashes work.
        """
        kwargs = {
            'hash': '1234567890',
            'name': 'SomeApplication',
            'version': '1.2.3',
            'vendor': 'Fake Vendor',
            'cves': 'CVE-1969-0000',
            'db_version': 1,
            'format': 'JAR',
        }
        hash = CVEMap(**kwargs)
        for key, value in kwargs.items():
            assert getattr(hash, key) == value
        self.connection.session.add(hash)
        self.connection.session.flush()

        results = self.connection.session.query(CVEMap).filter(
            CVEMap.hash == kwargs['hash'])
        assert results.count() == 1

        result = results[0]
        for key, value in kwargs.items():
            assert getattr(result, key) == value
