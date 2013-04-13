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
Package for package scanning.
"""

__docformat__ = 'restructuredtext'
__version__ = '0.0.2.1'
__author__ = "Steve 'Ashcrow' Milner"
__license__ = 'GPLv3+'

import hashlib
import os

from victims.archivers import Archive


class HashGenerator(object):
    """
    Generates a hash baed on filename.
    """
    __slots__ = ['__hash_cls']

    def __init__(self, hash_cls=hashlib.sha512):
        """
        Creates an instance of the generator.

        :Parameters:
           - `hash_cls`: hashlib hash generating class to use.
        """
        self.__hash_cls = hash_cls

    def __call__(self, input):
        """
        Generates the hash based off the filename.

        :Parameters:
           - `input`: the path to the file or a file like obj for hashing.
        """
        if getattr(input, 'read', False):
            f_obj = input
        else:
            f_obj = open(input, 'r')
        hash = self.__hash_cls(f_obj.read()).hexdigest()
        f_obj.close()
        return hash


class Packages(dict):
    """
    Container for multiple packages.
    """

    def append(self, hash, package):
        """
        Override append to take the hash string and package instance.

        :Parameters:
           - `hash`: hash which the package matches
           - `package`: package to associate with the hash
        """
        if hash in self.keys():
            self[hash] = self[hash] + [package]
        else:
            self[hash] = [package]


class Package(object):
    """
    General abstraction of a package, either inside or out.
    """

    def __init__(self, name, path, parent=None):
        """
        Creates an instance of a packge information object.

        :Parameters:
           - `name`: name of the package
           - `path`: full path of the package
           - `parent`: full path of the parent package if one exists
        """
        self.name = name
        self.path = path
        self.parent = parent

    def __repr__(self):
        """
        String representation of the instance.
        """
        if self.parent:
            return unicode(self.name + " (inside " + self.parent + ")")
        return unicode(self.path)

    # Aliases
    __str__ = __repr__
    __unicode__ = __repr__

    # Read-only properties
    internal = property(lambda s: bool(s.parent))


class PackageFinder(object):
    """
    Finds package files starting from a root directory.
    """

    __slots__ = ['__packages', '__look_inside']

    def __init__(
            self,
            packages=('jar', 'war', 'egg', 'zip', 'tar.gz', 'rpm'),
            look_inside=False):
        """
        Creates the PackageFinder instance with suffix to look for.

        :Parameters:
           - `packages`: package suffixes to look for.
           - `look_inside`: Boolean on if we should look inside packages
        """
        self.__packages = packages
        self.__look_inside = look_inside

    def __call__(self, path):
        """
        Looks for the packages.

        :Parameters:
           - `path`: the path to start looking from.
        """
        formats = []
        if os.path.isfile(path):
            return self._scan('', [path])
        else:
            found = []
            for root, dirs, files in os.walk(path):
                found_in_scan, formats_found = self._scan(root, files)
                formats += formats_found
                found += found_in_scan
            # Remove dupes
            formats = [x for x in set(formats)]
            return (found, formats)

    def _look_inside(self, path):
        """
        Handles looking inside of the package or archive.

        :Parameters:
           - `path`: path to the package or archive
        """
        found = []
        archive = Archive(path)
        # If we can not handle it as an archive, then we don't handle
        # it as an archive to look inside of
        if not archive.handleable:
            return found

        for file_name in archive.file_list:
            if file_name.endswith(self.__packages):
                internal_file = archive.open(file_name)
                # Zips use fileobj.name
                try:
                    found.append(Package(
                        internal_file.name, internal_file,
                        internal_file.fileobj.name))
                # Tarballs use fileobj.fileobj.name
                except:
                    found.append(Package(
                        internal_file.name, internal_file,
                        internal_file.fileobj.fileobj.name))
        return found

    def _scan(self, root, files):
        """
        Does the heavy lifting looking for files.

        :Parameters:
           - `root`: path to where we are looking.
           - `files`: list of files in the path.
        """
        found = []
        # for each package, check it
        for name in files:
            full_path = os.path.realpath(os.path.join(root, name))
            if name.endswith(self.__packages):
                found.append(Package(name, full_path))
                if self.__look_inside:
                    found += self._look_inside(full_path)
        formats = self._find_formats(found)
        return (found, formats)

    def _find_formats(self, found):
        """
        Finds the formats in a list of packages.

        :Parameters:
           - `found`: packages found
        """
        formats = []
        for package in self.__packages:
            for name in [x.name for x in found]:
                if package in name:
                    formats.append(package)
        return [x.upper() for x in set(formats)]
