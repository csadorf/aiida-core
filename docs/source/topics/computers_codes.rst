.. _setup_computer:

****************************
Setting up computers & codes
****************************

================
Setup a computer
================

A computer in AiiDA denotes any computational resource (with a batch job scheduler) on which you will run your calculations.
Computers typically are clusters or supercomputers.

Remote computer requirements
============================

Requirements for a computer are:

* It must run a Unix-like operating system
* It must have ``bash`` installed
* It should have a batch scheduler installed (see :doc:`here <scheduler>`
  for a list of supported batch schedulers)
* It must be accessible from the machine that runs AiiDA using one of the
  available transports (see below).

.. note::
    AiiDA will use ``bash`` on the remote computer, regardless of the default shell.
    Please ensure that your remote ``bash`` configuration does not load a different shell.

The first step is to choose the transport to connect to the computer. Typically,
you will want to use the SSH transport, apart from a few special cases where
SSH connection is not possible (e.g., because you cannot setup a password-less
connection to the computer). In this case, you can install AiiDA directly on
the remote cluster, and use the ``local`` transport (in this way, commands to
submit the jobs are simply executed on the AiiDA machine, and files are simply
copied on the disk instead of opening an SFTP connection).

If you plan to use the ``local`` transport, you can skip to the next section.

If you plan to use the ``SSH`` transport, you have to configure a password-less
login from your user to the cluster. To do so type first (only if you do not
already have some keys in your local ``~/.ssh`` directory - i.e. files like
``id_rsa.pub``)::

    ssh-keygen -t rsa -b 4096 -m PEM

.. note:: The ``-m PEM`` flag is necessary in newer versions of OpenSSL that switched to a different key format by default.
   As of 2019-08, the paramiko library used by AiiDA `only supports the PEM format <https://github.com/paramiko/paramiko/issues/340>`_.

Then copy your keys to the remote computer (in ~/.ssh/authorized_keys) with::

    ssh-copy-id YOURUSERNAME@YOURCLUSTERADDRESS

replacing ``YOURUSERNAME`` and ``YOURCLUSTERADDRESS`` by respectively your username
and cluster address. Finally add the following lines to ~/.ssh/config (leaving an empty
line before and after)::

  Host YOURCLUSTERADDRESS
    User YOURUSERNAME
    IdentityFile YOURRSAKEY

replacing ``YOURRSAKEY`` by the path to the rsa private key you want to use
(it should look like ``~/.ssh/id_rsa``).

.. note:: In principle you don't have to put the ``IdentityFile`` line if you have
  only one rsa key in your ``~/.ssh`` folder.

Before proceeding to setup the computer, be sure that you are able to
connect to your cluster using::

   ssh YOURCLUSTERADDRESS

without the need to type a password. Moreover, make also sure you can connect
via ``sftp`` (needed to copy files). The following command::

   sftp YOURCLUSTERADDRESS

should show you a prompt without errors (possibly with a message saying
``Connected to YOURCLUSTERADDRESS``).

.. note:: If the ``ssh`` command works, but the ``sftp`` command does not
  (e.g. it just prints ``Connection closed``), a possible reason can be
  that there is a line in your ``~/.bashrc`` (on the cluster) that either produces text output
  or an error. Remove/comment it until no output or error is produced: this
  should make ``sftp`` work again.

Finally, try also::

   ssh YOURCLUSTERADDRESS QUEUE_VISUALIZATION_COMMAND

replacing ``QUEUE_VISUALIZATION_COMMAND`` by the scheduler command that prints on screen the
status of the queue on the cluster (i.e. ``qstat`` for PBSpro scheduler, ``squeue`` for SLURM, etc.).
It should print a snapshot of the queue status, without any errors.

.. note:: If there are errors with the previous command, then
  edit your ~/.bashrc file in the remote computer and add a line at the beginning
  that adds the path to the scheduler commands, typically (here for
  PBSpro)::

     export PATH=$PATH:/opt/pbs/default/bin

  Or, alternatively, find the path to the executables (like using ``which qsub``).

.. note:: If you need your remote .bashrc to be sourced before you execute the code
  (for instance to change the PATH), make sure the .bashrc file **does not** contain
  lines like::

     [ -z "$PS1" ] && return

  or::

     case $- in
         *i*) ;;
         *) return;;
     esac

  in the beginning (these would prevent the bashrc to be executed when you ssh
  to the remote computer). You can check that e.g. the PATH variable is correctly
  set upon ssh, by typing (in your local computer)::

     ssh YOURCLUSTERADDRESS 'echo $PATH'


.. note:: If you need to ssh to a computer *A* first, from which you can then
     connect to computer *B* you wanted to connect to, you can use the
     ``proxy_command`` feature of ssh, that we also support in
     AiiDA. For more information, see :ref:`ssh_proxycommand`.


.. _computer_setup:

Computer setup and configuration
================================
The configuration of computers happens in two steps.

.. note:: The commands use some ``readline`` extensions to provide default
  answers, that require an advanced terminal. Therefore, run the commands from
  a standard terminal, and not from embedded terminals as the ones included in
  text editors, unless you know what you are doing. For instance, the
  terminal embedded in ``emacs`` is known to give problems.

1. **Setup of the computer**, using the::

    verdi computer setup

   command. This command allows to create a new computer instance in the DB.

   .. tip:: The code will ask you a few pieces of information. At every prompt, you can
     type the ``?`` character and press ``<enter>`` to get a more detailed
     explanation of what is being asked.

   .. tip:: You can press ``<CTRL>+C`` at any moment to abort the setup process.
     Nothing will be stored in the DB.

   Here is a list of what is asked, together with an explanation.

   * **Computer label**: the (user-friendly) label of the new computer instance
     which is about to be created in the DB (the label is used for instance when
     you have to pick a computer to launch a calculation on it). Labels must
     be unique. This command should be thought as a AiiDA-wise configuration of
     computer, independent of the AiiDA user that will actually use it.

   * **Fully-qualified hostname**: the fully-qualified hostname of the computer
     to which you want to connect (i.e., with all the dots: ``bellatrix.epfl.ch``,
     and not just ``bellatrix``). Type ``localhost`` for the local transport.

   * **Description**:  A human-readable description of this computer; this is
     useful if you have a lot of computers and you want to add some text to
     distinguish them (e.g.: "cluster of computers at EPFL, installed in 2012,
     2 GB of RAM per CPU")

   * **Enabled**: either True or False; if False, the computer is disabled
     and calculations associated with it will not be submitted. This allows to
     disable temporarily a computer if it is giving problems or it is down for
     maintenance, without the need to delete it from the DB.

   * **Transport plugin**: The type of the transport to be used. A list of valid
     transport types can be obtained typing ``?``

   * **Scheduler plugin**: The name of the plugin to be used to manage the
     job scheduler on the computer. A list of valid
     scheduler plugins can be obtained typing ``?``. See
     :doc:`here <../scheduler/index>` for a documentation of scheduler plugins
     in AiiDA.

   * **shebang line** This is the first line in the beginning of the submission script.
     The default is ``#!/bin/bash``. You can change this in order, for example, to add options,
     such as the ``-l`` flag. Note that AiiDA only supports bash at this point!

   * **Work directory on the computer**: The absolute path of the directory on the
     remote computer where AiiDA will run the calculations
     (often, it is the scratch of the computer). You can (should) use the
     ``{username}`` replacement, that will be replaced by your username on the
     remote computer automatically: this allows the same computer to be used
     by different users, without the need to setup a different computer for
     each one. Example::

       /scratch/{username}/aiida_work/

   * **Mpirun command**: The ``mpirun`` command needed on the cluster to run parallel MPI
     programs. You can (should) use the ``{tot_num_mpiprocs}`` replacement,
     that will be replaced by the total number of cpus, or the other
     scheduler-dependent fields (see the :doc:`scheduler docs <../scheduler/index>`
     for more information). Some examples::

        mpirun -np {tot_num_mpiprocs}
        aprun -n {tot_num_mpiprocs}
        poe

   * **Default number of CPUs per machine**: The number of MPI processes per machine that
     should be executed if it is not otherwise specified. Use ``0`` to specify no default value.

   At the end, the command will open your default editor on a file containing a summary
   of the configuration up to this point, and the possibility to add ``bash``
   commands that will be executed either *before* the actual execution of the job
   (under 'pre-execution script') or *after* the script submission (under 'Post execution script').
   These additional lines need may set up the environment on the computer,
   for example loading modules or exporting environment variables, for example::

        export NEWVAR=1
        source some/file

   .. note:: Don't specify settings here that are specific to a code, calculation or scheduler --
      you can set further pre-execution commands at the ``Code`` and ``CalcJob`` level.

   When you are done editing, save and quit (e.g. ``<ESC>:wq<ENTER>`` in ``vim``).
   The computer has now been created in the database but you still need to *configure* access to it
   using your credentials.

   In order to avoid having to retype the setup information the next time round, it is also possible provide some (or all) of the information
   described above via a configuration file using::

        verdi computer setup --config computer.yml

   where ``computer.yml`` is a configuration file in the
   `YAML format <https://en.wikipedia.org/wiki/YAML#Syntax>`_.
   This file contains the information in a series of key:value pairs:

   .. code-block:: yaml

      ---
      label: "localhost"
      hostname: "localhost"
      transport: local
      scheduler: "direct"
      work_dir: "/home/max/.aiida_run"
      mpirun_command: "mpirun -np {tot_num_mpiprocs}"
      mpiprocs_per_machine: "2"
      prepend_text: |
        module load mymodule
        export NEWVAR=1

  .. tip:: The list of the keys that can be used is available from the options flags of the command: ::

        verdi computer setup --help

     Note the syntax differences: remove the ``--`` prefix
     and replace ``-`` within the keys by the underscore ``_``.



2. **Configuration of the computer**, using the::

    verdi computer configure TRANSPORTTYPE COMPUTERNAME

   command, with the appropriate transport type (``ssh`` or ``local``) and computer label.

   The configuration allows to access more detailed configurations, that are
   often user-dependent and  depend on the specific transport.

   The command will try to provide automatically default answers,
   that can be selected by pressing enter.

   For ``local`` transport, the only information required is the minimum
   time interval between conections to the computer.

   For ``ssh`` transport, the following will be asked:

   * **User name**: your username on the remote machine
   * **port Nr**: the port to connect to (the default SSH port is 22)
   * **Look_for_keys**: automatically look for the private key in ``~/.ssh``.
     Default: False.
   * **SSH key file**: the absolute path to your private SSH key. You can leave
     it empty to use the default SSH key, if you set ``look_for_keys`` to True.
   * **Connection timeout**: A timeout in seconds if there is no response (e.g., the
     machine is down. You can leave it empty to use the default value.)
   * **Allow_ssh agent**: If True, it will try to use an SSH agent.
   * **SSH proxy_command**: Leave empty if you do not need a proxy command (i.e.,
     if you can directly connect to the machine). If you instead need to connect
     to an intermediate computer first, you need to provide here the
     command for the proxy: see documentation :ref:`here <ssh_proxycommand>`
     for how to use this option, and in particular the notes
     :ref:`here <ssh_proxycommand_notes>` for the format of this field.
   * **Compress file transfer**: True to compress the traffic (recommended)
   * **GSS auth**: yes when using Kerberos token to connect
   * **GSS kex**: yes when using Kerberos token to connect, in some cases
     (depending on your ``.ssh/config`` file)
   * **GSS deleg_creds**: yes when using Kerberos token to connect, in
     some cases (depending on your ``.ssh/config`` file)
   * **GSS host**: hostname when using Kerberos token to connect (defaults
     to the remote computer hostname)
   * **Load system host keys**: True to load the known hosts keys from the
     default SSH location (recommended)
   * **key policy**: What is the policy in case the host is not known.
     It is a string among the following:

     * ``RejectPolicy`` (default, recommended): reject the connection if the
       host is not known.
     * ``WarningPolicy`` (*not* recommended): issue a warning if the
       host is not known.
     * ``AutoAddPolicy`` (*not* recommended): automatically add the host key
       at the first connection to the host.
   * **Connection cooldown time (s)**: The minimum time interval between consecutive
     connection openings to the remote machine.

After setup and configuration have been completed, your computer is ready to go!

.. note:: If the cluster you are using requires authentication through a Kerberos
    token (that you need to obtain before using ssh), you typically need to install
    ``libffi`` (``sudo apt-get install libffi-dev`` under Ubuntu), and make sure you install
    the ``ssh_kerberos`` :ref:`optional dependencies<install_optional_dependencies>` during the installation process of AiiDA.
    Then, if your ``.ssh/config`` file is configured properly (in particular includes
    all the necessary ``GSSAPI`` options), ``verdi computer configure`` will
    contain already the correct suggestions for all the gss options needed to support Kerberos.

.. note:: To check if you set up the computer correctly,
  execute::

    verdi computer test COMPUTERNAME

  that will run a few tests (file copy, file retrieval, check of the jobs in
  the scheduler queue) to verify that everything works as expected.

.. note:: If you are not sure if your computer is already set up, use the command::

     verdi computer list

   to get a list of existing computers, and::

     verdi computer show COMPUTERNAME

   to get detailed information on the specific computer named ``COMPUTERNAME``.
   You have also the::

     verdi computer rename OLDCOMPUTERNAME NEWCOMPUTERNAME

   and::

     verdi computer delete COMPUTERNAME

   commands, to rename a computer or remove it from the database.

.. note:: You can delete computers **only if** no entry in the database is linked to
  them (as for instance Calculations, or RemoteData objects). Otherwise, you
  will get an error message.

.. note:: It is possible to **disable** a computer.

  Doing so will prevent AiiDA
  from connecting to the given computer to check the state of calculations or
  to submit new calculations. This is particularly useful if, for instance,
  the computer is under maintenance but you still want to use AiiDA with
  other computers, or submit the calculations in the AiiDA database anyway.

  The relevant commands are::

     verdi computer enable COMPUTERNAME
     verdi computer disable COMPUTERNAME

  Note that the above commands will disable the computer for all AiiDA users.


On not bombarding the remote computer with requests
---------------------------------------------------

Some machine (particularly at supercomputing centres) may not tolerate opening
connections and executing scheduler commands with a high frequency.  To limit this
AiiDA currently has two settings:

 * The transport safe open interval, and,
 * the minimum job poll interval

Neither of these can ever be violated.  AiiDA will not try to update the jobs list
on a remote machine until the job poll interval has elapsed since the last update
(the first update will be immediate) at which point it will request a transport.
Because of this the maximum possible time before a job update could be the sum of
the two intervals, however this is unlikely to happen in practice.

The transport open interval is currently hardcoded by the transport plugin;
typically for SSH it's longer than for local transport.

The job poll interval can be set programmatically on the corresponding ``Computer``
object in verdi shell::

    load_computer('localhost').set_minimum_job_poll_interval(30.0)


would set the transport interval on a computer called 'localhost' to 30 seconds.

.. note:: All of these intervals apply *per worker*, meaning that a daemon with
   multiple workers will not necessarily, overall, respect these limits.
   For the time being there is no way around this and if these limits must be
   respected then do not run with more than one worker.
.. _setup_code:

============
Setup a code
============

Once you have at least one computer configured, you can configure the codes.
In AiiDA, for full reproducibility of each calculation, we store each code in
the database, and attach to each calculation a given code. This has the further
advantage to make very easy to query for all calculations that were run with
a given code (for instance because I am looking for phonon calculations, or
because I discovered that a specific version had a bug and I want to rerun
the calculations).

In AiiDA, we distinguish two types of codes: **remote** codes and **local** codes,
where the distinction between the two is described here below.

Remote codes
------------
With remote codes we denote codes that are installed/compiled
on the remote computer. Indeed, this is very often the case for codes installed
in supercomputers for high-performance computing applications, because the
code is typically installed and optimized on the supercomputer.

In AiiDA, a remote code is identified by two mandatory pieces of information:

* A computer on which the code is (that must be a previously configured computer);
* The absolute path of the code executable on the remote computer.

Local codes
-----------
With local codes we denote codes for which the code is not
already present on the remote machine, and must be copied for every submission.
This is the case if you have for instance a small, machine-independent Python
script that you did not copy previously in all your clusters.

In AiiDA, a local code can be set up by specifying:

* A folder, containing all files to be copied over at every submission
* The name of executable file among the files inside the folder specified above

Setting up a code
-----------------

The::

  verdi code

command allows to manage codes in AiiDA.

To setup a new code, you execute::

  verdi code setup

and you will be guided through a process to setup your code.


.. tip:: The setup will ask you a few pieces of information. At every prompt, you can
   type the ``?`` character and press ``<enter>`` to get a more detailed
   explanation of what is being asked.

You will be asked for:

* **Label**:  A label to refer to this code. Note: this label is not enforced
  to be unique. However, if you try to keep it unique, at least within
  the same computer, you can use it later
  to refer and use to your code. Otherwise, you need to remember its ``ID`` or ``UUID``.

* **Description**: A human-readable description of this code (for instance "Quantum
  Espresso v.5.0.2 with 5.0.3 patches, pw.x code, compiled with openmpi").

* **Default calculation input plugin**: A string that identifies the default input plugin to
  be used to generate new calculations to use with this code.
  This string has to be a valid string recognized by the ``CalculationFactory``
  function. To get the list of all available Calculation plugin strings,
  use the ``verdi plugin list aiida.calculations`` command.

* **Installed on target computer**: either True (for local codes) or False (for remote
  codes). For the meaning of the distinction, see above. Depending
  on your choice, you will be asked for:

  * REMOTE CODES:

    * **Remote computer name**: The computer name on which the code resides,
      as configured and stored in the AiiDA database.

    * **Remote absolute path**: The (full) absolute path of the code executable
      on the remote machine, *including the name of the executable*.

  * LOCAL CODES:

    * **Local directory containing the code**: The absolute path where the executable and all other
      files needed to run the code are stored; these will be copied over to
      the remote computers for every submitted calculation.
    * **Relative path of executable inside code folder**: The relative path of the executable
      file inside the folder entered in the previous step.


At the end of these steps, you will be prompted to edit a script,
and you will have the opportunity to include ``bash`` commands that will
be executed *before* running the submission script (after the
'pre execution script' lines) and *after* running the submission script
(after the 'Post execution script' separator).
This is intended for code-dependent settings, for instance to load modules or set variables
that are needed by the code. For example::

  module load intelmpi


At the end, you will get a confirmation command, and also the ID of the code in the
database (the ``pk``, i.e. the principal key, and the ``uuid``).

In a manner analogous to a computer setup, it is also possible to provide some (or all) the information
described above via a configuration file using ::

  verdi code setup --config code.yml

where ``code.yml`` is a configuration file in the
`YAML format <https://en.wikipedia.org/wiki/YAML#Syntax>`_.

This file contains the information in a series of key:value pairs:

.. code-block:: yaml

    ---
    label: "qe-6.3-pw"
    description: "quantum_espresso v6.3"
    input_plugin: "quantumespresso.pw"
    on_computer: true
    remote_abs_path: "/path/to/code/pw.x"
    computer: "localhost"
    prepend_text: |
      module load module1
      module load module2
    append_text: " "

.. tip:: The keys mirror the available options of the command, which you can print using: ::

    verdi code setup --help

  Note the syntax differences: remove the ``--`` prefix
  and replace ``-`` within the keys by the underscore ``_``.


.. note:: Codes are a subclass of the :py:class:`Node <aiida.orm.nodes.Node>` class,
   and as such you can attach any set of attributes to the code. These can
   be extremely useful for querying: for instance, you can attach the version
   of the code as an attribute, or the code family (for instance: "pw.x code of
   Quantum Espresso") to later query for all runs done with a pw.x code and
   version more recent than 5.0.0, for instance.  However, in the
   present AiiDA version you cannot add attributes from the command line using
   ``verdi``, but you have to do it using Python code.

.. note:: You can change the label of a code by using the following command::

   verdi code relabel "ID" "new-label"

  (Without the quotation marks!) "ID" can either be the numeric ID (PK) of
  the code (preferentially), or possibly its label (or ``label@computername``),
  if this string uniquely identifies a code.

  You can also list all available codes (and their relative IDs) with::

   verdi code list

  which also accepts some flags to filter only codes on a
  given computer, only codes using a specific plugin, etc.; use the ``-h``
  command line option to see the documentation of all possible options.

  You can then get the information of a specific code with::

   verdi code show "ID"

  Finally, to delete a code use::

   verdi code delete "ID"

  (only if it wasn't used by any calculation, otherwise an exception
  is raised).

And now, you are ready to launch your calculations!
