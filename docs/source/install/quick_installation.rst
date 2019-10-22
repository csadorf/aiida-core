.. _quick_installation:

************
Installation
************

Install the ``aiida-core`` python package:

.. code-block:: bash

    pip install --pre aiida-core
    reentry scan

Set up your AiiDA profile:

.. code-block:: bash

    verdi quicksetup

Start the AiiDA daemon process:

.. code-block:: bash

    verdi daemon start

Check that all services are up and running:

.. code-block:: bash

    verdi status

     ✓ profile:     On profile quicksetup
     ✓ repository:  /repo/aiida_dev/quicksetup
     ✓ postgres:    Connected to aiida@localhost:5432
     ✓ rabbitmq:    Connected to amqp://127.0.0.1?heartbeat=600
     ✓ daemon:      Daemon is running as PID 2809 since 2019-03-15 16:27:52

If you see all checkmarks, it is time to :ref:`get started<get_started>`!

If the quick installation fails at any point, please refer
to the :ref:`full installation guide<installation>` for more details
or the :ref:`troubleshooting section<troubleshooting>`.

For configuration of tab completion or using AiiDA in jupyter, see the :ref:`configuration instructions <configure_aiida>` before moving on.
