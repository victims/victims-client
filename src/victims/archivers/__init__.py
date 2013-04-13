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
Special archiving items.
"""

__docformat__ = 'restructuredtext'

import os
import subprocess
import zipfile

from StringIO import StringIO

import cpioarchive


class Archive(object):
    """
    Gets names, fileobjects and parent for file archives.
    """

    __slots__ = ['__file_path', '__name_func', '__open_func',
        '__archive_obj']

    def __init__(self, path):
        """
        Create an archive instance.

        :Parameters:
           - `path`: path to the archive
        """
        self.__file_path = path
        self.__name_func = None
        self.__open_func = None

        lower_file = os.path.basename(self.__file_path.lower())
        if (lower_file.endswith('.jar') or lower_file.endswith('.zip') or
            lower_file.endswith('.war')):
            self.__handle_zip()
        elif lower_file.endswith('.tar.gz'):
            self.__handle_tarball()
        elif lower_file.endswith('.rpm'):
            self.__handle_rpm()

    def __handle_zip(self):
        """
        Handle mapping methods for zipfiles.
        """
        self.__archive_obj = zipfile.ZipFile(self.__file_path)
        self.__name_func = self.__archive_obj.namelist
        self.__open_func = self.__archive_obj.open

    def __handle_tarball(self):
        """
        Handle mapping methods for tarballs.
        """
        import tarfile
        self.__archive_obj = tarfile.open(self.__file_path, 'r:gz')
        self.__name_func = self.__archive_obj.getnames
        self.__open_func = self.__archive_obj.extractfile

    def __handle_rpm(self):
        """
        Handle mapping methods for rpms.
        """
        self.__archive_obj = RPMArchive(self.__file_path)
        self.__name_func = self.__archive_obj.getnames
        self.__open_func = self.__archive_obj.extractfile

    def open(self, name):
        """
        Get a file like object from the archive.

        :Paramters:
           - `name`: name/path to the internal file
        """
        return self.__open_func(name)

    # Read-only properties
    file_list = property(lambda s: s.__name_func())
    handleable = property(
        lambda s: callable(s.__name_func) and callable(s.__open_func))


class RPMFile(StringIO):
    """
    Abstration of a file inside of the RPM making it look and feel like the
    results that would come from zip or tarballs.
    """

    def __init__(self, info, parent_name):
        """
        Creates an instance of the internal file based on the data in the
        intenral file.

        :Paramters:
           - `info`: cpioarchive item from ._infos
           - `parent_name`: name of the parent file
        """
        StringIO.__init__(self, info.read())
        self.name = info.name

        class Dummy(object):
            pass

        self.fileobj = Dummy()
        self.fileobj.name = parent_name


class RPMArchive(object):
    """
    An archive abstrator for RPM.
    """

    def __init__(self, path):
        """
        Creates an instance.

        :Paramteres:
           - `path`: path to the rpm
        """
        # XXX: HACK, but couldn't find a better way :-(
        p = subprocess.Popen(["rpm2cpio", path], stdout=subprocess.PIPE)
        self.__cpio_data = cpioarchive.CpioArchive(
            fileobj=StringIO(p.communicate()[0][:-1]))
        self.__file_map = {}
        for idx in range(len(self.__cpio_data._infos)):
            self.__file_map[self.__cpio_data._infos[idx].name] = (
                RPMFile(self.__cpio_data._infos[idx], path))

    def getnames(self):
        """
        Returns a list of all file names inside the rpm.
        """
        return self.__file_map.keys()

    def extractfile(self, path):
        """
        Extracts a file from the rpm archive.

        :Paramteres:
           - `path`: path to the internal file
        """
        if path in self.__file_map.keys():
            return self.__file_map[path]
        raise Exception('File not found')

    # Read-only properties
    names = property(getnames)
