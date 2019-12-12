.. _how_to:

****************
 How-to guides
****************

.. _get_started:

Get started
===========

.. toctree::
   :maxdepth: 1

   get_started/plugins
   get_started/computers
   get_started/codes
   verdi
   python_api
   scripting
   daemon_service


Manage data
===========

Data types
----------

.. toctree::
    :maxdepth: 4

    datatypes/index
    datatypes/kpoints
    datatypes/bands
    datatypes/functionality

Groups
------

.. toctree::
    :maxdepth: 4

    groups

Querying data
-------------

.. toctree::
    :maxdepth: 4

    querying/querybuilder/intro
    querying/querybuilder/append
    querying/querybuilder/queryhelp
    querying/backend

Result manager
--------------

.. toctree::
    :maxdepth: 4

    resultmanager


Delete nodes
------------

.. toctre::

    deleting_nodes

Provenance graphs
-----------------
.. toctree::
    :maxdepth: 2

    visualising_graphs/visualising_graphs

Backups
-------

.. toctree::
    :maxdepth: 4

    backup/index.rst

Import and export
-----------------

.. toctree::
    :maxdepth: 4

    import_export/main
    import_export/external_dbs

Caching
=======

.. toctree::
    :maxdepth: 4

    caching.rst


Schedulers
==========

Instances of ``CalcJobNode`` instances are submitted by the daemon to an external scheduler.
For this functionality to work, AiiDA needs to be able to interact with these schedulers.
Interfaces have been written for some of the most used schedulers.

.. toctree::
    :maxdepth: 4

    scheduler/index

Troubleshooting
===============

.. toctree::
    :maxdepth: 4

    troubleshooting.rst

Cookbook
========

.. toctree::
    :maxdepth: 4

    cookbook.rst
