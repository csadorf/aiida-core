# -*- coding: utf-8 -*-
###########################################################################
# Copyright (c), The AiiDA team. All rights reserved.                     #
# This file is part of the AiiDA code.                                    #
#                                                                         #
# The code is hosted on GitHub at https://github.com/aiidateam/aiida_core #
# For further information on the license, see the LICENSE.txt file        #
# For further information please visit http://www.aiida.net               #
###########################################################################
"""Utility functions for migration of export-files."""
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import


def verify_metadata_version(metadata, version=None):
    """
    Utility function to verify that the metadata has the correct version number.
    If no version number is passed, it will just extract the version number
    and return it.

    :param metadata: the content of an export archive metadata.json file
    :param version: string version number that the metadata is expected to have
    """
    try:
        metadata_version = metadata['export_version']
    except KeyError:
        raise ValueError('could not find the export_version field in the metadata')

    if version is None:
        return metadata_version

    if metadata_version != version:
        raise ValueError('expected export file with version {} but found version {}'.format(version, metadata_version))

    return None


def update_metadata(metadata, version):
    """
    Update the metadata with a new version number and a notification of the
    conversion that was executed

    :param metadata: the content of an export archive metadata.json file
    :param version: string version number that the updated metadata should get
    """
    from aiida import get_version

    old_version = metadata['export_version']
    conversion_info = metadata.get('conversion_info', [])

    conversion_message = 'Converted from version {} to {} with external script'.format(old_version, version)
    conversion_info.append(conversion_message)

    metadata['aiida_version'] = get_version()
    metadata['export_version'] = version
    metadata['conversion_info'] = conversion_info
