# Copyright 2010
# Steve 'Ashcrow' Milner <stevem@gnulinux.net>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
Yum plugin which scans packages at install/update time.
"""

import subprocess

from yum.plugins import TYPE_CORE, Errors
from yum.constants import *

requires_api_version = '2.4'
plugin_type = (TYPE_CORE,)


def postdownload_hook(conduit):
    """
    Hook to catch after download but before installation.

    :Parameters:
       - `conduit`: DownloadPluginConduit instance
    """
    # Only trigger on installs or updates
    (options, commands) = conduit.getCmdLine()
    if 'install' in commands or 'update' in commands:
        # Create an executable command based off the package paths
        exec_command = ['victims-scan', '-l'] + [
            x.localpath for x in conduit.getDownloadPackages()]
        # Execute and check the return code ... 1 means issues found
        ret = subprocess.call(exec_command)
        if ret == 1:
            # Warn the user and hope they don't continue ...
            install = conduit.promptYN(("At least one security issue has been "
                "detected. Installing this set of packages could compromise "
                "the security of your system."))
            # If they are not dumb they will stop :-)
            if not install:
                raise Errors.InstallError('Stopping install')
