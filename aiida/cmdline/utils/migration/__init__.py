# -*- coding: utf-8 -*-
###########################################################################
# Copyright (c), The AiiDA team. All rights reserved.                     #
# This file is part of the AiiDA code.                                    #
#                                                                         #
# The code is hosted on GitHub at https://github.com/aiidateam/aiida_core #
# For further information on the license, see the LICENSE.txt file        #
# For further information please visit http://www.aiida.net               #
###########################################################################
"""Migration from v0.1 to v0.2, used by `verdi export migrate` command."""
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from aiida.cmdline.utils import echo
from aiida.common.exceptions import DanglingLinkError

from .utils import verify_metadata_version, update_metadata
from .v01_to_v02 import migrate_v1_to_v2
from .v02_to_v03 import migrate_v2_to_v3
from .v03_to_v04 import migrate_v3_to_v4

__all__ = ('migrate_recursive', 'verify_metadata_version', 'update_metadata')


def migrate_recursive(metadata, data, folder):
    """
    Recursive migration of export files from v0.1 to newest version,
    See specific migration functions for detailed descriptions.

    :param metadata: the content of an export archive metadata.json file
    :param data: the content of an export archive data.json file
    """
    from aiida.orm.importexport import EXPORT_VERSION as newest_version

    old_version = verify_metadata_version(metadata)

    try:
        if old_version == newest_version:
            echo.echo_critical('Your export file is already at the newest export version {}'.format(newest_version))
        elif old_version == '0.1':
            migrate_v1_to_v2(metadata, data)
        elif old_version == '0.2':
            migrate_v2_to_v3(metadata, data)
        elif old_version == '0.3':
            migrate_v3_to_v4(metadata, data, folder)
        else:
            echo.echo_critical('Cannot migrate from version {}'.format(old_version))
    except ValueError as exception:
        echo.echo_critical(exception)
    except DanglingLinkError:
        echo.echo_critical('Export file is invalid because it contains dangling links')

    new_version = verify_metadata_version(metadata)

    if new_version < newest_version:
        migrate_recursive(metadata, data, folder)

    return new_version
