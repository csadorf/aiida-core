Tips & Tricks / Troubleshooting
===============================

This section is a collection of tips and tricks as well as short scripts and code snippets that may be useful in the everyday usage of AiiDA.
Please read carefully the notes (if any) before running the scripts!

Checking the queued jobs on a scheduler
---------------------------------------

If you want to know if which jobs are currently on the scheduler (e.g.
to dynamically decide on which computer to submit, or to delay submission, etc.)
you can use a modification of the following script::

    from __future__ import print_function


    def get_scheduler_jobs(only_current_user=True):
        """
        Return a list of all current jobs in the scheduler.

        .. note:: an SSH connection is open and closed at every
            launch of this function.

        :param only_current_user: if True, filters by these
            considering only those of the current user (if this
            feature is supported by the scheduler plugin). Otherwise,
            if False show all jobs.
        """
        from aiida import orm

        computer = Computer.get(name='deneb')
        transport = computer.get_transport()
        scheduler = computer.get_scheduler()
        scheduler.set_transport(transport)

        # this opens the SSH connection, for SSH transports
        with transport:
            if only_current_user:
                remote_username = transport.whoami()
                all_jobs = scheduler.get_jobs(
                    user=remote_username,
                    as_dict=True)
            else:
                all_jobs = scheduler.get_jobs(
                    as_dict=True)

        return all_jobs

    if __name__ == "__main__":
        all_jobs = get_scheduler_jobs(only_current_user=False)
        user_jobs = get_scheduler_jobs(only_current_user=True)

        print("Current user has {} jobs out of {} in the scheduler".format(
            len(user_jobs), len(all_jobs)
        ))

        print ("Detailed (user's) job view:")
        for job_id, job_info in user_jobs.items():
            print ("Job ID: {}".format(job_id))
            for k, v in job_info.items():
                if k == "raw_data":
                    continue
                print("  {}: {}".format(k, v))
            print("")

Use ``verdi run`` to execute it::

  verdi run file_with_script.py

.. note:: Every time you call the function, an ssh connection
  is executed! So be careful and run this function
  sparsely, or your supercomputer centre might block your account.

  Another alternative if you want to call many times the function
  is to pass the transport as a parameter, and keep it open from the outside.

An example output would be::

    Current user has 5 jobs out of 1425 in the scheduler
    Detailed (user's) job view:
    Job ID: 1658497
      job_id: 1658497
      wallclock_time_seconds: 38052
      title: aiida-2324985
      num_machines: 4
      job_state: RUNNING
      queue_name: parallel
      num_mpiprocs: 64
      allocated_machines_raw: r02-node[17-18,53-54]
      submission_time: 2018-03-28 09:21:35
      job_owner: some_remote_username
      dispatch_time: 2018-03-28 09:21:35
      annotation: None
      requested_wallclock_time_seconds: 82800

    (...)

Getting an AuthInfo knowing the computer and the user
-----------------------------------------------------

If you have an ORM ``Computer`` and and ORM ``User``, the way to get
an ``AuthInfo`` object is the following::

    AuthInfo.objects.get(dbcomputer_id=computer.id, aiidauser_id=user.id)

This might be useful, for instance, to then get a transport to connect to the
computer.

Here is, as an example, an useful utility function::

    def get_authinfo_from_computername(computername):
        from aiida.orm import AuthInfo, User, Computer
        from aiida.manage.manager import get_manager
        manager = get_manager()
        profile = manager.get_profile()
        return AuthInfo.objects.get(
            dbcomputer_id=Computer.get(name=computername).id,
            aiidauser_id=User.get(email=profile.default_user).id
        )

that you can then use, for instance, as follows::

    authinfo = get_authinfo_from_computername('localhost')
    with authinfo.get_transport() as transport:
        print(transport.listdir())

.. _ssh_proxycommand:

Using the proxy_command option with ssh
---------------------------------------

This page explains how to use the ``proxy_command`` feature of ``ssh``. This feature
is needed when you want to connect to a computer ``B``, but you are not allowed to
connect directly to it; instead, you have to connect to computer ``A`` first, and then
perform a further connection from ``A`` to ``B``.


Requirements
++++++++++++
The idea is that you ask ``ssh`` to connect to computer ``B`` by using
a proxy to create a sort of tunnel. One way to perform such an
operation is to use ``netcat``, a tool that simply takes the standard input and
redirects it to a given TCP port.

Therefore, a requirement is to install ``netcat`` on computer A.
You can already check if the ``netcat`` or ``nc`` command is available
on you computer, since some distributions include it (if it is already
installed, the output of the command::

  which netcat

or::

  which nc

will return the absolute path to the executable).

If this is not the case, you will need to install it on your own.
Typically, it will be sufficient to look for a netcat distribution on
the web, unzip the downloaded package, ``cd`` into the folder and
execute something like::

  ./configure --prefix=.
  make
  make install

This usually creates a subfolder ``bin``, containing the ``netcat``
and ``nc`` executables.
Write down the full path to ``nc`` that we will need later.


ssh/config
++++++++++
You can now test the proxy command with ``ssh``. Edit the
``~/.ssh/config`` file on the computer on which you installed AiiDA
(or create it if missing) and add the following lines::

  Host FULLHOSTNAME_B
  Hostname FULLHOSTNAME_B
  User USER_B
  ProxyCommand ssh USER_A@FULLHOSTNAME_A ABSPATH_NETCAT %h %p

where you have to replace:

* ``FULLHOSTNAMEA`` and ``FULLHOSTNAMEB`` with
  the fully-qualified hostnames of computer ``A`` and ``B`` (remembering that ``B``
  is the computer you want to actually connect to, and ``A`` is the
  intermediate computer to which you have direct access)
* ``USER_A`` and ``USER_B`` are the usernames on the two machines (that
  can possibly be the same).
* ``ABSPATH_NETCAT`` is the absolute path to the ``nc`` executable
  that you obtained in the previous step.

Remember also to configure passwordless ssh connections using ssh keys
both from your computer to ``A``, and from ``A`` to ``B``.

Once you add this lines and save the file, try to execute::

  ssh FULLHOSTNAME_B

which should allow you to directly connect to ``B``.


WARNING
+++++++

There are several versions of netcat available on the web.
We found at least one case in which the executable wasn't working
properly.
At the end of the connection, the ``netcat`` executable might still be
running: as a result, you may rapidly
leave the cluster with hundreds of opened ``ssh`` connections, one for
every time you connect to the cluster ``B``.
Therefore, check on both computers ``A`` and ``B`` that the number of
processes ``netcat`` and ``ssh`` are disappearing if you close the
connection.
To check if such processes are running, you can execute::

  ps -aux | grep <username>

Remember that a cluster might have more than one login node, and the ``ssh``
connection will randomly connect to any of them.


AiiDA config
++++++++++++
If the above steps work, setup and configure now the computer as
explained :ref:`here <computer_setup>`.

If you properly set up the ``~/.ssh/config`` file in the previous
step, AiiDA should properly parse the information in the file and
provide the correct default value for the ``proxy_command`` during the
``verdi computer configure`` step.

.. _ssh_proxycommand_notes:

Some notes on the ``proxy_command`` option
++++++++++++++++++++++++++++++++++++++++++

* In the ``~/.ssh/config`` file, you can leave the ``%h`` and ``%p``
  placeholders, that are then automatically replaced by ssh with the hostname
  and the port of the machine ``B`` when creating the proxy.
  However, in the AiiDA ``proxy_command`` option, you need to put the
  actual hostname and port. If you start from a properly configured
  ``~/.ssh/config`` file, AiiDA will already replace these
  placeholders with the correct values. However, if you input the ``proxy_command``
  value manually, remember to write the
  hostname and the port and not ``%h`` and ``%p``.
* In the ``~/.ssh/config`` file, you can also insert stdout and stderr
  redirection, e.g. ``2> /dev/null`` to hide any error that may occur
  during the proxying/tunneling. However, you should only give AiiDA
  the actual command to be executed, without any redirection. Again,
  AiiDA will remove the redirection when it automatically reads the
  ``~/.ssh/config`` file, but be careful if entering manually the
  content in this field.


Increasing the debug level
--------------------------

By default, the logging level of AiiDA is minimal to avoid filling logfiles.
Only warnings and errors are logged to the daemon log files, while info and debug
messages are discarded.

If you are experiencing a problem, you can change the default minimum logging
level of AiiDA messages::

  verdi config logging.aiida_loglevel DEBUG

You might also be interested in circus log messages (the ``circus`` library is the daemonizer that manages the daemon runners) but most often it is used by AiiDA developers::

  verdi config logging.circus_loglevel DEBUG


For each profile that runs a daemon, there will be two unique logfiles, one for
AiiDA log messages (named ``aiida-<profile_name>.log``) and one for the circus logs (named ``circus-<profile_name>.log``). Those files can be found
in the ``~/.aiida/daemon/log`` folder.

After rebooting the daemon (``verdi daemon restart``), the number of messages
logged will increase significantly and may help in understanding
the source of the problem.

.. note:: In the command above, you can use a different level than ``DEBUG``.
  The list of the levels and their order is the same of the `standard python
  logging module <https://docs.python.org/3/library/logging.html#logging-levels>`_.
  In addition to the standard logging levels, we define our custom ``REPORT`` level,
  which, with a value of ``23``, sits between the standard ``INFO`` and ``WARNING``
  levels. The ``REPORT`` level is the default logging level as this is what is used
  by messages from, among other things, the work chain report..

When the problem is solved, we suggest to bring back the default logging level, using the two commands::

    verdi config logging.circus_loglevel --unset
    verdi config logging.aiida_loglevel --unset

to avoid to fill the logfiles.

The config options set for the current profile can be viewed using::

  verdi profile show

in the ``options`` row.

.. _repo_troubleshooting:

Reduce the disk I/O load for large databases
--------------------------------------------

Those tips are useful when your database is very large, i.e. several hundreds of
thousands of nodes or more. With such large databases the hard drive
may be constantly working and the computer slowed down a lot. Below are some
solutions to take care of the most typical reasons.

Repository backup
+++++++++++++++++

The backup of the repository takes an extensively long time if it is done through
a standard rsync or backup software, since it contains as many folders as the number
of nodes (and each folder can contain many files!).
A solution is to use instead the incremental
backup described in the :ref:`repository backup section<repository_backup>`.


mlocate cron job
++++++++++++++++

Under typical Linux distributions, there is a cron job (called
``updatedb.mlocate``) running every day to update a database of files and
folders -- this is to be used by the ``locate`` command. This might become
problematic since the repository contains many folders and
will be scanned everyday. The net effect is a hard drive almost constantly
working.

To avoid this issue, edit as root the file ``/etc/updatedb.conf``
and put in ``PRUNEPATHS`` the name of the repository folder.
