#!/usr/bin/env python
#
# Copyright 2010-2013
# Steve 'Ashcrow' Milner <stevem@gnulinux.net>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
Standard build script.
"""

__docformat__ = 'restructuredtext'

import sys

from setuptools import setup

sys.path.insert(0, 'src/')

from victims import __version__

setup(
    name="victims",
    version=__version__,
    description="Package scanning tool",
    long_description="Package scanning tools to try to catch bad 'packages'",
    author="Steve 'Ashcrow' Milner",
    author_email='stevem@gnulinux.net',
    url="http://bitbucket.org/ashcrow/victims",
    download_url="http://bitbucket.org/ashcrow/victims/downloads/",
    platforms=['any'],

    license="GPL",

    package_dir={
        'victims': 'src/victims',
    },
    packages=['victims', 'victims.scripts', 'victims.archivers'],

    entry_points={
        'console_scripts': [
            'victims-scan = victims.scripts.scan_packages:main',
            'victims-update-db = victims.scripts.update_db:main',
            'victims-find-hash = victims.scripts.find_hash:main',
            'victims-version-check = victims.scripts.version_check:main'],
    },

    classifiers=[
        'License :: OSI Approved :: Python Software Foundation License',
        'Development Status :: 4 - Beta',
        'Topic :: Security',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Programming Language :: Python'],
)
