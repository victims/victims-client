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

import os.path
import unittest

from victims.config import Config


class TestConfig(unittest.TestCase):
    """
    Unittests for the configuraiton module.
    """

    conf_path = os.path.sep.join([
        os.path.realpath(os.path.curdir), 'conf', 'example.cfg'])

    def test_basic_interface(self):
        """
        Verifies the way we load content works as expected.
        """
        conf = Config({'a': 'b'})
        assert conf

        conf = Config(self.conf_path)
        assert conf

    def test_loading(self):
        """
        Make sure the loading of data works correctly.
        """
        conf = Config(self.conf_path)
        for key in ('database', 'service'):
            assert key in conf.keys()

        for key in ('url', 'convert_unicode', 'echo'):
            assert key in conf['database'].keys()

        for key in ('updateurl', 'removeurl'):
            assert key in conf['service'].keys()

        assert conf['database']['url'] == 'sqlite:////tmp/victims.db'
        # Hrrm, I don't much like this ...
        assert conf['database']['convert_unicode'] == 'True'
        assert conf['database']['echo'] == 'False'

        assert conf['service']['updateurl'] == (
            'http://victi.ms/service/v1/update/')
        assert conf['service']['removeurl'] == (
            'http://victi.ms/service/v1/remove/')
