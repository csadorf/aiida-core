.. _concepts_processes:

*********
Processes
*********

=======
Concept
=======

Anything that runs in AiiDA is an instance of the :py:class:`~aiida.engine.processes.process.Process` class.
The ``Process`` class contains all the information and logic to tell, whoever is handling it, how to run it to completion.
Typically the one responsible for running the processes is an instance of a :py:class:`~aiida.engine.runners.Runner`.
This can be a local runner or one of the daemon runners in case of the daemon running the process.

In addition to those run instructions, any ``Process`` that has been executed needs some sort of record in the database to store what happened during its execution.
For example it needs to record what its exact inputs were, the log messages that were reported and what the final outputs were.
For this purpose, every process will utilize an instance of a sub class of the :py:class:`~aiida.orm.nodes.process.ProcessNode` class.
This ``ProcessNode`` class is a sub class of :py:class:`~aiida.orm.nodes.Node` and serves as the record of the process' execution in the database and by extension the provenance graph.

It is very important to understand this division of labor.
A ``Process`` describes how something should be run, and the ``ProcessNode`` serves as a mere record in the database of what actually happened during execution.
A good thing to remember is that while it is running, we are dealing with the ``Process`` and when it is finished we interact with the ``ProcessNode``.

.. _concepts_process_types:

Process types
=============

Processes in AiiDA come in two flavors:

 * Calculation-like
 * Workflow-like

The calculation-like processes have the capability to *create* data, whereas the workflow-like processes orchestrate other processes and have the ability to *return* data produced by calculations.
Again, this is a distinction that plays a big role in AiiDA and is crucial to understand.
For this reason, these different types of processes also get a different sub class of the ``ProcessNode`` class.
The hierarchy of these node classes and the link types that are allowed between them and ``Data`` nodes, is explained in detail in the :ref:`provenance implementation<concepts_provenance_implementation>` documentation.

Currently, there are four types of processes in ``aiida-core`` and the following table shows with which node class it is represented in the provenance graph and what the process is used for.

===================================================================   ==============================================================================  ===============================================================
Process class                                                         Node class                                                                      Used for
===================================================================   ==============================================================================  ===============================================================
:py:class:`~aiida.engine.processes.calcjobs.calcjob.CalcJob`          :py:class:`~aiida.orm.nodes.process.calculation.calcjob.CalcJobNode`            Calculations performed by external codes
:py:class:`~aiida.engine.processes.workchains.workchain.WorkChain`    :py:class:`~aiida.orm.nodes.process.workflow.workchain.WorkChainNode`           Workflows that run multiple calculations
:py:class:`~aiida.engine.processes.functions.FunctionProcess`         :py:class:`~aiida.orm.nodes.process.calculation.calcfunction.CalcFunctionNode`  Python functions decorated with the ``@calcfunction`` decorator
:py:class:`~aiida.engine.processes.functions.FunctionProcess`         :py:class:`~aiida.orm.nodes.process.workflow.workfunction.WorkFunctionNode`     Python functions decorated with the ``@workfunction`` decorator
===================================================================   ==============================================================================  ===============================================================

For basic information on the concept of a ``CalcJob`` or ``calcfunction``, refer to the :ref:`calculations concept<concepts_calculations>` and the same for the ``WorkChain`` and ``workfunction`` is described in the :ref:`workflows concept<concepts_workflows>`.
After having read and understood the basic concept of calculation and workflow processes, detailed information on how to implement and use them can be found in the dedicated developing sections for :ref:`calculations<working_calculations>` and :ref:`workflows<working_workflows>`, respectively.

.. note:: A ``FunctionProcess`` is never explicitly implemented but will be generated dynamically by the engine when a python function decorated with a :py:func:`~aiida.engine.processes.functions.calcfunction` or :py:func:`~aiida.engine.processes.functions.workfunction` is run.


.. _concepts_process_state:

Process state
=============
Each instance of a ``Process`` class that is being executed has a process state.
This property tells you about the current status of the process.
It is stored in the instance of the ``Process`` itself and the workflow engine, the ``plumpy`` library, operates only on that value.
However, the ``Process`` instance 'dies' as soon as it is terminated, therefore the process state is also written to the calculation node that the process uses as its database record, under the ``process_state`` attribute.
The process can be in one of six states:

========  ============
*Active*  *Terminated*
========  ============
Created   Killed
Running   Excepted
Waiting   Finished
========  ============

The three states in the left column are 'active' states, whereas the right column displays the three 'terminal' states.
Once a process reaches a terminal state, it will never leave it; its execution is permanently terminated.
When a process is first created, it is put in the ``Created`` state.
As soon as it is picked up by a runner and it is active, it will be in the ``Running`` state.
If the process is waiting for another process, that it called, to be finished, it will be in the ``Waiting`` state.
If a process is in the ``Killed`` state, it means the user issued a command to kill it, or its parent process was killed.
The ``Excepted`` state indicates that during execution an exception occurred that was not caught and the process was unexpectedly terminated.
The final option is the ``Finished`` state, which means that the process was successfully executed, and the execution was nominal.
Note that this does not automatically mean that the result of the process can also be considered to be successful, it was just executed without any problems.

To distinguish between a successful and a failed execution, there is the :ref:`exit status<concepts_process_exit_codes>`.
This is another attribute that is stored in the node of the process and is an integer that can be set by the process.
A ``0`` (zero) means that the result of the process was successful, and a non-zero value indicates a failure.
All the process nodes used by the various processes are sub-classes of :py:class:`~aiida.orm.nodes.process.ProcessNode`, which defines handy properties to query the process state and exit status.

===================   ============================================================================================
Property              Meaning
===================   ============================================================================================
``process_state``     Returns the current process state
``exit_status``       Returns the exit status, or None if not set
``exit_message``      Returns the exit message, or None if not set
``is_terminated``     Returns ``True`` if the process was either ``Killed``, ``Excepted``, or ``Finished``
``is_killed``         Returns ``True`` if the process is ``Killed``
``is_excepted``       Returns ``True`` if the process is ``Excepted``
``is_finished``       Returns ``True`` if the process is ``Finished``
``is_finished_ok``    Returns ``True`` if the process is ``Finished`` and the ``exit_status`` is equal to zero
``is_failed``         Returns ``True`` if the process is ``Finished`` and the ``exit_status`` is non-zero
===================   ============================================================================================

When you load a calculation node from the database, you can use these property methods to inquire about its state and exit status.


.. _concepts_process_exit_codes:

Process exit codes
==================
The previous section about the process state showed that a process that is ``Finished`` does not say anything about whether the result is 'successful' or 'failed'.
The ``Finished`` state means nothing more than that the engine succeeded in running the process to the end of execution, without it encountering exceptions or being killed.
To distinguish between a 'successful' and 'failed' process, an 'exit status' can be defined.
The `exit status is a common concept in programming <https://en.wikipedia.org/wiki/Exit_status>`_ and is a small integer, where zero means that the result of the process was successful, and a non-zero value indicates a failure.
By default a process that terminates nominally will get a ``0`` (zero) exit status.
To mark a process as failed, one can return an instance of the :py:class:`~aiida.engine.processes.exit_code.ExitCode` named tuple, which allows to set an integer ``exit_status`` and a string message as ``exit_message``.
When the engine receives such an ``ExitCode`` as the return value from a process, it will set the exit status and message on the corresponding attributes of the process node representing the process in the provenance graph.
How exit codes can be defined and returned depends on the process type and will be documented in detail in the respective :ref:`calculation<working_calculations>` and :ref:`workflow<working_workflows>` development sections.


.. _concepts_process_lifetime:

Process lifetime
================

The lifetime of a process is defined as the time from the moment it is launched until it reaches a :ref:`terminal state<concepts_process_state>`.

.. _concepts_process_node_distinction:

Process and node distinction
----------------------------
As explained in the :ref:`introduction of this section<concepts_processes>`, there is a clear and important distinction between the 'process' and the 'node' that represents its execution in the provenance graph.
When a process is launched, an instance of the ``Process`` class is created in memory which will be propagated to completion by the responsible runner.
This 'process' instance only exists in the memory of the python interpreter that it is running in, for example that of a daemon runner, and so we cannot directly inspect its state.
That is why the process will write any of its state changes to the corresponding node representing it in the provenance graph.
In this way, the node acts as a 'proxy' or a mirror image that reflects the state of the process in memory.
This means that the output of many of the ``verdi`` commands, such as ``verdi process list``, do not actually show the state of the process instances, but rather the state of the node to which they have last written their state.

Process tasks
-------------
The previous section explained how launching a process means creating an instance of the ``Process`` class in memory.
When the process is being 'ran' (see the section on :ref:`launching processes<working_processes_launch>` for more details) that is to say in a local interpreter, the particular process instance will die as soon as the interpreter dies.
This is what often makes 'submitting' the preferred method of launching a process.
When a process is 'submitted', an instance of the ``Process`` is created, along with the node that represents it in the database, and its state is then persisted to the database.
This is called a 'process checkpoint', more information on which :ref:`will follow later<concepts_process_checkpoints>`.
Subsequently, the process instance is shutdown and a 'continuation task' is sent to the process queue of RabbitMQ.
This task is simply a small message that just contains an identifier for the process.

All the daemon runners, when they are launched, subscribe to the process queue and RabbitMQ will distribute the continuation tasks to them as they come in, making sure that each task is only sent to one runner at a time.
The receiving daemon runner can restore the process instance in memory from the checkpoint that was stored in the database and continue the execution.
As soon as the process reaches a terminal state, the daemon runner will acknowledge to RabbitMQ that the task has been completed.
Until the runner has confirmed that a task is completed, RabbitMQ will consider the task as incomplete.
If a daemon runner is shutdown or dies before it got the chance to finish running a process, the task will automatically be requeued by RabbitMQ and sent to another daemon runner.
Together with the fact that all the tasks in the process queue are persisted to disk by RabbitMQ, guarantees that once a continuation task has been sent to RabbitMQ, it will at some point be finished, while allowing the machine to be shutdown.

Each daemon runner has a maximum number of tasks that it can run concurrently, which means that if there are more active tasks than available slots, some of the tasks will remain queued.
Processes, whose task is in the queue and not with any runner, though technically 'active' as they are not terminated, are not actually being run at the moment.
While a process is not actually being run, i.e. it is not in memory with a runner, one cannot interact with it.
Similarly, as soon as the task disappears, either because the process was intentionally terminated (or unintentionally), the process will never continue running again.


.. _concepts_process_checkpoints:

Process checkpoints
-------------------
A process checkpoint is a complete representation of a ``Process`` instance in memory that can be stored in the database.
Since it is a complete representation, the ``Process`` instance can also be fully reconstructed from such a checkpoint.
At any state transition of a process, a checkpoint will be created, by serializing the process instance and storing it as an attribute on the corresponding process node.
This mechanism is the final cog in the machine, together with the persisted process queue of RabbitMQ as explained in the previous section, that allows processes to continue after the machine they were running on, has been shutdown and restarted.


.. _concepts_process_sealing:

Process sealing
===============
One of the cardinal rules of AiiDA is that once a node is *stored*, it is immutable, which means that its attributes can no longer be changed.
This rule is a problem for processes, however, since in order to be able to start running it, its corresponding process node first has to be stored.
However, at that point its attributes, such as the process state or other mutable attributes, can no longer be changed by the engine throughout the lifetime of the corresponding process.
To overcome this limitation, the concept of *updatable* attributes is introduced.
These are special attributes that are allowed to be changed *even* when the process node is already stored *and* the corresponding process is still active.
To mark the point where a process is terminated and even the updatable attributes on the process node are to be considered immutable, the node is *sealed*.
A sealed process node behaves exactly like a normal stored node, as in *all* of its attributes are immutable.
In addition, once a process node is sealed, no more incoming or outgoing links can be attached to it.
Unsealed process nodes can also not be exported, because they belong to processes that are still active.
Note that the sealing concept does not apply to data nodes and they are exportable as soon as they are stored.
To determine whether a process node is sealed, one can use the property :py:meth:`~aiida.orm.utils.mixins.Sealable.is_sealed`.

==========
Aplication
==========

.. _working_processes:

.. _working_processes_defining:

Defining processes
==================

.. _working_processes_spec:

Process specification
---------------------
How a process defines the inputs that it requires or can optionally take, depends on the process type.
The inputs of :py:class:`~aiida.engine.processes.calcjobs.calcjob.CalcJob` and :py:class:`~aiida.engine.processes.workchains.workchain.WorkChain` are given by the :py:class:`~aiida.engine.processes.process_spec.ProcessSpec` class, which is defined though  the :py:meth:`~aiida.engine.processes.process.Process.define` method.
For process functions, the :py:class:`~aiida.engine.processes.process_spec.ProcessSpec` is dynamically generated by the engine from the signature of the decorated function.
Therefore, to determine what inputs a process takes, one simply has to look at the process specification in the ``define`` method or the function signature.
For the :py:class:`~aiida.engine.processes.calcjobs.calcjob.CalcJob` and :py:class:`~aiida.engine.processes.workchains.workchain.WorkChain` there is also the concept of the :ref:`process builder<working_processes_builder>`, which will allow one to inspect the inputs with tab-completion and help strings in the shell.

The three most important attributes of the :py:class:`~aiida.engine.processes.process_spec.ProcessSpec` are:

    * ``inputs``
    * ``outputs``
    * ``exit_codes``

Through these attributes, one can define what inputs a process takes, what outputs it will produce and what potential exit codes it can return in case of errors.
Just by looking at a process specification then, one will know exactly *what* will happen, just not *how* it will happen.
The ``inputs`` and ``outputs`` attributes are *namespaces* that contain so called *ports*, each one of which represents a specific input or output.
The namespaces can be arbitrarily nested with ports and so are called *port namespaces*.
The port and port namespace are implemented by the :py:class:`~plumpy.Port` and :py:class:`~aiida.engine.processes.ports.PortNamespace` class, respectively.


.. _working_processes_ports_portnamespaces:

Ports and Port namespaces
^^^^^^^^^^^^^^^^^^^^^^^^^
To define an input for a process specification, we only need to add a port to the ``inputs`` port namespace, as follows:

.. code:: python

    spec = ProcessSpec()
    spec.input('parameters')

The ``input`` method, will create an instance of :py:class:`~aiida.engine.processes.ports.InputPort`, a sub class of the base :py:class:`~plumpy.Port`, and will add it to the ``inputs`` port namespace of the spec.
Creating an output is just as easy, but one should use the :py:meth:`~plumpy.ProcessSpec.output` method instead:

.. code:: python

    spec = ProcessSpec()
    spec.output('result')

This will cause an instance of :py:class:`~aiida.engine.processes.ports.OutputPort`, also a sub class of the base :py:class:`~plumpy.Port`, to be created and to be added to the ``outputs`` specifcation attribute.
Recall, that the ``inputs`` and ``output`` are instances of a :py:class:`~aiida.engine.processes.ports.PortNamespace`, which means that they can contain any port.
But the :py:class:`~aiida.engine.processes.ports.PortNamespace` itself is also a port itself, so it can be added to another port namespace, allowing one to create nested port namespaces.
Creating a new namespace in for example the inputs namespace is as simple as:

.. code:: python

    spec = ProcessSpec()
    spec.input_namespace('namespace')

This will create a new ``PortNamespace`` named ``namespace`` in the ``inputs`` namespace of the spec.
You can create arbitrarily nested namespaces in one statement, by separating them with a ``.`` as shown here:

.. code:: python

    spec = ProcessSpec()
    spec.input_namespace('nested.namespace')

This command will result in the ``PortNamespace`` name ``namespace`` to be nested inside another ``PortNamespace`` called ``nested``.

.. note::

    Because the period is reserved to denote different nested namespaces, it cannot be used in the name of terminal input and output ports as that could be misinterpreted later as a port nested in a namespace.

Graphically, this can be visualized as a nested dictionary and will look like the following:

.. code:: python

    'inputs': {
        'nested': {
            'namespace': {}
        }
    }

The ``outputs`` attribute of the ``ProcessSpec`` is also a ``PortNamespace`` just as the ``inputs``, with the only different that it will create ``OutputPort`` instead of ``InputPort`` instances.
Therefore the same concept of nesting through ``PortNamespaces`` applies to the outputs of a ``ProcessSpec``.


.. _working_processes_validation_defaults:

Validation and defaults
^^^^^^^^^^^^^^^^^^^^^^^
In the previous section, we saw that the ``ProcessSpec`` uses the ``PortNamespace``, ``InputPort`` and ``OutputPort`` to define the inputs and outputs structure of the ``Process``.
The underlying concept that allows this nesting of ports is that the ``PortNamespace``, ``InputPort`` and ``OutputPort``, are all a subclass of :py:class:`~plumpy.ports.Port`.
And as different subclasses of the same class, they have more properties and attributes in common, for example related to the concept of validation and default values.
All three have the following attributes (with the exception of the ``OutputPort`` not having a ``default`` attribute):

    * ``default``
    * ``required``
    * ``valid_type``
    * ``validator``

These attributes can all be set upon construction of the port or after the fact, as long as the spec has not been sealed, which means that they can be altered without limit as long as it is within the ``define`` method of the corresponding ``Process``.
An example input port that explicitly sets all these attributes is the following:

.. code:: python

    spec.input('positive_number', required=False, default=Int(1), valid_type=(Int, Float), validator=is_number_positive)

Here we define an input named ``positive_number`` that is not required, if a value is not explicitly passed, the default ``Int(1)`` will be used and if a value *is* passed, it should be of type ``Int`` or ``Float`` and it should be valid according to the ``is_number_positive`` validator.
Note that the validator is nothing more than a free function which takes a single argument, being the value that is to be validated.
If nothing is returned, the value is considered to be valid.
To signal that the value is invalid and to have a validation error raised, simply return a string with the validation error message, for example:

.. code:: python

    def is_number_positive(number):
        if number < 0:
            return 'The number has to be greater or equal to zero'

The ``valid_type`` can define a single type, or a tuple of valid types.

.. note::

    Note that by default all ports are required, but specifying a default value implies that the input is not required and as such specifying ``required=False`` is not necessary in that case.
    It was added to the example above simply for clarity.

The validation of input or output values with respect to the specification of the corresponding port, happens at the instantiation of the process and when it is finalized, respectively.
If the inputs are invalid, a corresponding exception will be thrown and the process instantiation will fail.
When the outputs fail to be validated, likewise an exception will be thrown and the process state will be set to ``Excepted``.


.. _working_processes_dynamic_namespaces:

Dynamic namespaces
^^^^^^^^^^^^^^^^^^
In the previous section we described the various attributes related to validation and claimed that all the port variants share those attributes, yet we only discussed the ``InputPort`` and ``OutputPort`` explicitly.
The statement, however, is still correct and the ``PortNamespace`` has the same attributes.
You might then wonder what the meaning is of a ``valid_type`` or ``default`` for a ``PortNamespace`` if all it does is contain ``InputPorts``, ``OutputPorts`` or other ``PortNamespaces``.
The answer to this question lies in the ``PortNamespace`` attribute ``dynamic``.

Often when designing the specification of a ``Process``, we cannot know exactly which inputs we want to be able to pass to the process.
However, with the concept of the ``InputPort`` and ``OutputPort`` one *does* need to know exactly, how many value one expects at least, as they do have to be defined.
This is where the ``dynamic`` attribute of the ``PortNamespace`` comes in.
By default this is set to ``False``, but by setting it to ``True``, one indicates that that namespace can take a number of values that is unknown at the time of definition of the specification.
This now explains the meaning of the ``valid_type``, ``validator`` and ``default`` attributes in the context of the ``PortNamespace``.
If you do mark a namespace as dynamic, you may still want to limit the set of values that are acceptable, which you can do by specifying the valid type and or validator.
The values that will eventually be passed to the port namespace will then be validated according to these rules exactly as a value for a regular input port would be.


.. _working_processes_non_db:

Non storable inputs
^^^^^^^^^^^^^^^^^^^
In principle, the only valid types for inputs and outputs should be instances of a :py:class:`~aiida.orm.nodes.data.data.Data` node, or one of its sub classes, as that is the only data type that can be recorded in the provenance graph as an input or output of a process.
However, there are cases where you might want to pass an input to a process, whose provenance you do not care about and therefore would want to pass a non-database storable type anyway.

.. note::

    AiiDA allows you to break the provenance as to be not too restrictive, but always tries to urge you and guide you in a direction to keep the provenance.
    There are legitimate reasons to break it regardless, but make sure you think about the implications and whether you are really willing to lose the information.

For this situation, the ``InputPort`` has the attribute ``non_db``.
By default this is set to ``False``, but by setting it to ``True`` the port is marked that the values that are passed to it should not be stored as a node in the provenance graph and linked to the process node.
This allows one to pass any normal value that one would also be able to pass to a normal function.


.. _working_processes_serialize_inputs:

Automatic input serialization
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Quite often, inputs which are given as python data types need to be cast to the corresponding AiiDA type before passing them to a process.
Doing this manually can be cumbersome, so you can define a function when defining the process specification, which does the conversion automatically.
This function, passed as ``serializer`` parameter to ``spec.input``, is invoked if the given input is *not* already an AiiDA type.

For inputs which are stored in the database (``non_db=False``), the serialization function should return an AiiDA data type.
For ``non_db`` inputs, the function must be idempotent because it might be applied more than once.

The following example work chain takes three inputs ``a``, ``b``, ``c``, and simply returns the given inputs. The :func:`aiida.orm.nodes.data.base.to_aiida_type` function is used as serialization function.

.. include:: include/snippets/workflows/workchains/workchain_serialize.py
    :code: python

This work chain can now be called with native Python types, which will automatically converted to AiiDA types by the :func:`aiida.orm.nodes.data.base.to_aiida_type` function. Note that the module which defines the corresponding AiiDA type must be loaded for it to be recognized by :func:`aiida.orm.nodes.data.base.to_aiida_type`.

.. include:: include/snippets/workflows/workchains/run_workchain_serialize.py
    :code: python

Of course, you can also use the serialization feature to perform a more complex serialization of the inputs.


.. _working_processes_exit_codes:

Exit codes
^^^^^^^^^^
Any ``Process`` most likely will have one or multiple expected failure modes.
To clearly communicate to the caller what went wrong, the ``Process`` supports setting its ``exit_status``.
This ``exit_status``, a positive integer, is an attribute of the process node and by convention, when it is zero means the process was successful, whereas any other value indicates failure.
This concept of an exit code, with a positive integer as the exit status, `is a common concept in programming <https://shapeshed.com/unix-exit-codes/>`_ and a standard way for programs to communicate the result of their execution.

Potential exit codes for the ``Process`` can be defined through the ``ProcessSpec``, just like inputs and ouputs.
Any exit code consists of a positive non-zero integer, a string label to reference it and a more detailed description of the problem that triggers the exit code.
Consider the following example:

.. code:: python

    spec = ProcessSpec()
    spec.exit_code(418, 'ERROR_I_AM_A_TEAPOT', 'the process had an identity crisis')

This defines an exit code for the ``Process`` with exit status ``418`` and exit message ``the work chain had an identity crisis``.
The string ``ERROR_I_AM_A_TEAPOT`` is a label that the developer can use to reference this particular exit code somewhere in the ``Process`` code itself.

Whenever a ``Process`` exits through a particular error code, the caller will be able to introspect it through the ``exit_status`` and ``exit_message`` attributes of the node.
Assume for example that we ran a ``Process`` that threw the exit code described above, the caller would be able to do the following:

.. code:: python

    in[1] node = load_node(<pk>)
    in[2] node.exit_status
    out[2] 418
    in[2] node.exit_message
    out[2] 'the process had an identity crisis'

This is useful, because the caller can now programmatically, based on the ``exit_status``, decide how to proceed.
This is an infinitely more robust way of communcating specific errors to a non-human then parsing text based logs or reports.
Additionally, The exit codes make it also very easy to query for failed processes with specific error codes.


.. _working_processes_exit_code_conventions:

Exit code conventions
.....................
In principle, the only restriction on the exit status of an exit code is that it should be a positive integer or zero.
However, to make effective use of exit codes, there are some guidelines and conventions as to decide what integers to use.
Note that since the following rules are *guidelines* you can choose to ignore them and currently the engine will not complain, but this might change in the future.
Regardless, we advise you to follow the guidelines since it will improve the interoperability of your code with other existing plugins.
The following integer ranges are reserved or suggested:

    *   0 -  99: Reserved for internal use by `aiida-core`
    * 100 - 199: Reserved for errors parsed from scheduler output of calculation jobs (note: this is not yet implemented)
    * 200 - 299: Suggested to be used for process input validation errors
    * 300 - 399: Suggested for critical process errors

For any other exit codes, one can use the integers from 400 and up.


.. _working_processes_metadata:

Process metadata
----------------

Each process, in addition to the normal inputs defined through its process specifcation, can take optional 'metadata'.
These metadata differ from inputs in the sense that they are not nodes that will show up as inputs in the provenance graph of the executed process.
Rather, these are inputs that slightly modify the behavior of the process or allow to set attributes on the process node that represents its execution.
The following metadata inputs are available for *all* process classes:

    * ``label``: will set the label on the ``ProcessNode``
    * ``description``: will set the description on the ``ProcessNode``
    * ``store_provenance``: boolean flag, by default ``True``, that when set to ``False``, will ensure that the execution of the process **is not** stored in the provenance graph

Sub classes of the :py:class:`~aiida.engine.processes.process.Process` class can specify further metadata inputs, refer to their specific documentation for details.
To pass any of these metadata options to a process, simply pass them in a dictionary under the key ``metadata`` in the inputs when launching the process.
How a process can be launched is explained the following section.


.. _working_processes_launching:

Launching processes
===================
Any process can be launched by 'running' or 'submitting' it.
Running means to run the process in the current python interpreter in a blocking way, whereas submitting means to send it to a daemon worker over RabbitMQ.
For long running processes, such as calculation jobs or complex workflows, it is best advised to submit to the daemon.
This has the added benefit that it will directly return control to your interpreter and allow the daemon to save intermediate progress during checkpoints and reload the process from those if it has to restart.
Running processes can be useful for trivial computational tasks, such as simple calcfunctions or workfunctions, or for debugging and testing purposes.


.. _working_processes_launch:

Process launch
--------------

To launch a process, one can use the free functions that can be imported from the :py:mod:`aiida.engine` module.
There are four different functions:

    * :py:func:`~aiida.engine.launch.run`
    * :py:func:`~aiida.engine.launch.run_get_node`
    * :py:func:`~aiida.engine.launch.run_get_pk`
    * :py:func:`~aiida.engine.launch.submit`

As the name suggest, the first three will 'run' the process and the latter will 'submit' it to the daemon.
Running means that the process will be executed in the same interpreter in which it is launched, blocking the interpreter, until the process is terminated.
Submitting to the daemon, in contrast, means that the process will be sent to the daemon for execution, and the interpreter is released straight away.

All functions have the exact same interface ``launch(process, **inputs)`` where:

    * ``process`` is the process class or process function to launch
    * ``inputs`` are the inputs as keyword arguments to pass to the process.

What inputs can be passed depends on the exact process class that is to be launched.
For example, when we want to run an instance of the :py:class:`~aiida.calculations.plugins.arithmetic.add.ArithmeticAddCalculation` process, which takes two :py:class:`~aiida.orm.nodes.data.int.Int` nodes as inputs under the name ``x`` and ``y`` [#f1]_, we would do the following:

.. include:: include/snippets/processes/launch/launch_submit.py
    :code: python

The function will submit the calculation to the daemon and immediately return control to the interpreter, returning the node that is used to represent the process in the provenance graph.

.. warning::
    Process functions, i.e. python functions decorated with the ``calcfunction`` or ``workfunction`` decorators, **cannot be submitted** but can only be run.

The ``run`` function is called identically:

.. include:: include/snippets/processes/launch/launch_run.py
    :code: python

except that it does not submit the process to the daemon, but executes it in the current interpreter, blocking it until the process is terminated.
The return value of the ``run`` function is also **not** the node that represents the executed process, but the results returned by the process, which is a dictionary of the nodes that were produced as outputs.
If you would still like to have the process node or the pk of the process node you can use one of the following variants:

.. include:: include/snippets/processes/launch/launch_run_alternative.py
    :code: python

Finally, the :py:func:`~aiida.engine.launch.run` launcher has two attributes ``get_node`` and ``get_pk`` that are simple proxies to the :py:func:`~aiida.engine.launch.run_get_node` and :py:func:`~aiida.engine.launch.run_get_pk` methods.
This is a handy shortcut, as now you can choose to use any of the three variants with just a single import:

.. include:: include/snippets/processes/launch/launch_run_shortcut.py
    :code: python

If you want to launch a process class that takes a lot more inputs, often it is useful to define them in a dictionary and use the python syntax ``**`` that automatically expands it into keyword argument and value pairs.
The examples used above would look like the following:

.. include:: include/snippets/processes/launch/launch_submit_dictionary.py
    :code: python

Process functions, i.e. :ref:`calculation functions<concepts_calcfunctions>` and :ref:`work functions<concepts_workfunctions>`, can be launched like any other process as explained above, with the only exception that they **cannot be submitted**.
In addition to this limitation, process functions have two additional methods of being launched:

 * Simply *calling* the function
 * Using the internal run method attributes

Using a calculation function to add two numbers as an example, these two methods look like the following:

.. include:: include/snippets/processes/launch/launch_process_function.py
    :code: python


.. _working_processes_builder:

Process builder
---------------
As explained in a :ref:`previous section<working_processes_spec>`, the inputs for a :py:class:`~aiida.engine.processes.calcjobs.calcjob.CalcJob` and :py:class:`~aiida.engine.processes.workchains.workchain.WorkChain` are defined in the :py:meth:`~aiida.engine.processes.process.Process.define` method.
To know then what inputs they take, one would have to read the implementation, which can be annoying if you are not a developer.
To simplify this process, these two process classes provide a utility called the 'process builder'.
The process builder is essentially a tool that helps you build the inputs for the specific process class that you want to run.
To get a *builder* for a particular ``CalcJob`` or a ``WorkChain`` implementation, all you need is the class itself, which can be loaded through the :py:class:`~aiida.plugins.factories.CalculationFactory` and :py:class:`~aiida.plugins.factories.WorkflowFactory`, respectively.
Let's take the :py:class:`~aiida.calculations.plugins.arithmetic.add.ArithmeticAddCalculation` as an example::

    ArithmeticAddCalculation = CalculationFactory('arithmetic.add')
    builder = ArithmeticAddCalculation.get_builder()

The string ``arithmetic.add`` is the entry point of the ``ArithmeticAddCalculation`` and passing it to the ``CalculationFactory`` will return the corresponding class.
Calling the ``get_builder`` method on that class will return an instance of the :py:class:`~aiida.engine.processes.builder.ProcessBuilder` class that is tailored for the ``ArithmeticAddCalculation``.
The builder will help you in defining the inputs that the ``ArithmeticAddCalculation`` requires and has a few handy tools to simplify this process.

To find out which inputs the builder exposes, you can simply use tab completion.
In an interactive python shell, by simply typing ``builder.`` and hitting the tab key, a complete list of all the available inputs will be shown.
Each input of the builder can also show additional information about what sort of input it expects.
In an interactive shell, you can get this information to display as follows::

    builder.code?
    Type:        property
    String form: <property object at 0x7f04c8ce1c00>
    Docstring:
        "name": "code",
        "required": "True"
        "non_db": "False"
        "valid_type": "<class 'aiida.orm.nodes.data.code.Code'>"
        "help": "The Code to use for this job.",

In the ``Docstring`` you will see a ``help`` string that contains more detailed information about the input port.
Additionally, it will display a ``valid_type``, which when defined shows which data types are expected.
If a default value has been defined, that will also be displayed.
The ``non_db`` attribute defines whether that particular input will be stored as a proper input node in the database, if the process is submitted.

Defining an input through the builder is as simple as assigning a value to the attribute.
The following example shows how to set the ``parameters`` input, as well as the ``description`` and ``label`` metadata inputs::

    builder.metadata.label = 'This is my calculation label'
    builder.metadata.description = 'An example calculation to demonstrate the process builder'
    builder.x = Int(1)
    builder.y = Int(2)

If you evaluate the ``builder`` instance, simply by typing the variable name and hitting enter, the current values of the builder's inputs will be displayed::

    builder
    {
        'metadata': {
            'description': 'An example calculation to demonstrate the process builder',
            'label': 'This is my calculation label',
            'options': {},
        },
        'x': Int<uuid='a1798492-bbc9-4b92-a630-5f54bb2e865c' unstored>,
        'y': Int<uuid='39384da4-6203-41dc-9b07-60e6df24e621' unstored>
    }

In this example, you can see the value that we just set for the ``description`` and the ``label``.
In addition, it will also show any namespaces, as the inputs of processes support nested namespaces, such as the ``metadata.options`` namespace in this example.
Note that nested namespaces are also all autocompleted, and you can traverse them recursively with tab-completion.

All that remains is to fill in all the required inputs and we are ready to launch the process builder.
When all the inputs have been defined for the builder, it can be used to actually launch the ``Process``.
The process can be launched by passing the builder to any of the free functions :py:mod:`~aiida.engine.launch` module, just as you would do a normal process as :ref:`described above<working_processes_launching>`, i.e.:

.. include:: include/snippets/processes/launch/launch_builder.py
    :code: python

Note that the process builder is in principle designed to be used in an interactive shell, as there is where the tab-completion and automatic input documentation really shines.
However, it is perfectly possible to use the same builder in scripts where you simply use it as an input container, instead of a plain python dictionary.


.. _working_processes_monitoring:

Monitoring processes
====================
When you have launched a process, you may want to investigate its status, progression and the results.
The :ref:`verdi<verdi_overview>` command line tool provides various commands to do just this.


.. _working_processes_monitoring_list:

verdi process list
------------------
Your first point of entry will be the ``verdi`` command ``verdi process list``.
This command will print a list of all active processes through the ``ProcessNode`` stored in the database that it uses to represent its execution.
A typical example may look something like the following:

.. code-block:: bash

      PK  Created     State           Process label                 Process status
    ----  ----------  ------------    --------------------------    ----------------------
     151  3h ago      ⏵ Running       ArithmeticAddCalculation
     156  1s ago      ⏹ Created       ArithmeticAddCalculation


    Total results: 2

The 'State' column is a concatenation of the ``process_state`` and the ``exit_status`` of the ``ProcessNode``.
By default, the command will only show active items, i.e. ``ProcessNodes`` that have not yet reached a terminal state.
If you want to also show the nodes in a terminal states, you can use the ``-a`` flag and call ``verdi process list -a``:

.. code-block:: bash

      PK  Created     State              Process label                  Process status
    ----  ----------  ---------------    --------------------------     ----------------------
     143  3h ago      ⏹ Finished [0]     add
     146  3h ago      ⏹ Finished [0]     multiply
     151  3h ago      ⏵ Running          ArithmeticAddCalculation
     156  1s ago      ⏹ Created          ArithmeticAddCalculation


    Total results: 4

For more information on the meaning of the 'state' column, please refer to the documentation of the :ref:`process state <concepts_process_state>`.
The ``-S`` flag let's you query for specific process states, i.e. issuing ``verdi process list -S created`` will return:

.. code-block:: bash

      PK  Created     State           Process label                  Process status
    ----  ----------  ------------    --------------------------     ----------------------
     156  1s ago      ⏹ Created       ArithmeticAddCalculation


    Total results: 1

To query for a specific exit status, one can use ``verdi process list -E 0``:

.. code-block:: bash

      PK  Created     State             Process label                 Process status
    ----  ----------  ------------      --------------------------    ----------------------
     143  3h ago      ⏹ Finished [0]    add
     146  3h ago      ⏹ Finished [0]    multiply


    Total results: 2

This simple tool should give you a good idea of the current status of running processes and the status of terminated ones.
For a complete list of all the available options, please refer to the documentation of :ref:`verdi process<verdi_process>`.

If you are looking for information about a specific process node, the following three commands are at your disposal:

 * ``verdi process report`` gives a list of the log messages attached to the process
 * ``verdi process status`` print the call hierarchy of the process and status of all its nodes
 * ``verdi process show`` print details about the status, inputs, outputs, callers and callees of the process

In the following sections, we will explain briefly how the commands work.
For the purpose of example, we will show the output of the commands for a completed ``PwBaseWorkChain`` from the ``aiida-quantumespresso`` plugin, which simply calls a ``PwCalculation``.


.. _working_processes_monitoring_report:

verdi process report
--------------------
The developer of a process can attach log messages to the node of a process through the :py:meth:`~aiida.engine.processes.process.Process.report` method.
The ``verdi process report`` command will display all the log messages in chronological order:

.. code-block:: bash

    2018-04-08 21:18:51 [164 | REPORT]: [164|PwBaseWorkChain|run_calculation]: launching PwCalculation<167> iteration #1
    2018-04-08 21:18:55 [164 | REPORT]: [164|PwBaseWorkChain|inspect_calculation]: PwCalculation<167> completed successfully
    2018-04-08 21:18:56 [164 | REPORT]: [164|PwBaseWorkChain|results]: work chain completed after 1 iterations
    2018-04-08 21:18:56 [164 | REPORT]: [164|PwBaseWorkChain|on_terminated]: remote folders will not be cleaned

The log message will include a timestamp followed by the level of the log, which is always ``REPORT``.
The second block has the format ``pk|class name|function name`` detailing information about, in this case, the work chain itself and the step in which the message was fired.
Finally, the message itself is displayed.
Of course how many messages are logged and how useful they are is up to the process developer.
In general they can be very useful for a user to understand what has happened during the execution of the process, however, one has to realize that each entry is stored in the database, so overuse can unnecessarily bloat the database.


.. _working_processes_monitoring_status:

verdi process status
--------------------
This command is most useful for ``WorkChain`` instances, but also works for ``CalcJobs``.
One of the more powerful aspect of work chains, is that they can call ``CalcJobs`` and other ``WorkChains`` to create a nested call hierarchy.
If you want to inspect the status of a work chain and all the children that it called, ``verdi process status`` is the go-to tool.
An example output is the following:

.. code-block:: bash

    PwBaseWorkChain <pk=164> [ProcessState.FINISHED] [4:results]
        └── PwCalculation <pk=167> [FINISHED]

The command prints a tree representation of the hierarchical call structure, that recurses all the way down.
In this example, there is just a single ``PwBaseWorkChain`` which called a ``PwCalculation``, which is indicated by it being indented one level.
In addition to the call tree, each node also shows its current process state and for work chains at which step in the outline it is.
This tool can be very useful to inspect while a work chain is running at which step in the outline it currently is, as well as the status of all the children calculations it called.


.. _working_processes_monitoring_show:

verdi process show
------------------
Finally, there is a command that displays detailed information about the ``ProcessNode``, such as its inputs, outputs and the optional other processes it called and or was called by.
An example output for a ``PwBaseWorkChain`` would look like the following:

.. code-block:: bash

    Property       Value
    -------------  ------------------------------------
    type           WorkChainNode
    pk             164
    uuid           08bc5a3c-da7d-44e0-a91c-dda9ddcb638b
    label
    description
    ctime          2018-04-08 21:18:50.850361+02:00
    mtime          2018-04-08 21:18:50.850372+02:00
    process state  ProcessState.FINISHED
    exit status    0
    code           pw-v6.1

    Inputs            PK  Type
    --------------  ----  -------------
    parameters       158  Dict
    structure        140  StructureData
    kpoints          159  KpointsData
    pseudo_family    161  Str
    max_iterations   163  Int
    clean_workdir    160  Bool
    options          162  Dict

    Outputs              PK  Type
    -----------------  ----  -------------
    output_band         170  BandsData
    remote_folder       168  RemoteData
    output_parameters   171  Dict
    output_array        172  ArrayData

    Called      PK  Type
    --------  ----  -------------
    CALL       167  PwCalculation

    Log messages
    ---------------------------------------------
    There are 4 log messages for this calculation
    Run 'verdi process report 164' to see them

This overview should give you all the information if you want to inspect a process' inputs and outputs in closer detail as it provides you their pk's.


.. _working_processes_manipulating:

Manipulating processes
======================
To understand how one can manipulate running processes, one has to understand the principles of the :ref:`process/node distinction<concepts_process_node_distinction>` and a :ref:`process' lifetime<concepts_process_lifetime>` first, so be sure to have read those sections first.


.. _working_processes_manipulating_pause_play_kill:

verdi process pause/play/kill
-----------------------------
The ``verdi`` command line interface provides three commands to interact with 'live' processes.

    * ``verdi process pause``
    * ``verdi process play``
    * ``verdi process kill``

The first pauses a process temporarily, the second resumes any paused processes and the third one permanently kills them.
The sub command names might seem to tell you this already and it might look like that is all there is to know, but the functionality underneath is quite complicated and deserves additional explanation nonetheless.

As the section on :ref:`the distinction between the process and the node<concepts_process_node_distinction>` explained, manipulating a process means interacting with the live process instance that lives in the memory of the runner that is running it.
By definition, these runners will always run in a different system process then the one from which you want to interact, because otherwise, you would *be* the runner, given that there can only be a single runner in an interpreter and if it is running, the interpreter would be blocked from performing any other operations.
This means that in order to interact with the live process, one has to interact with another interpreter running in a different system process.
This is once again facilitated by the RabbitMQ message broker.
When a runner starts to run a process, it will also add listeners for incoming messages that are being sent for that specific process over RabbitMQ.

.. note::

    This does not just apply to daemon runners, but also normal runners.
    That is to say that if you were to launch a process in a local runner, that interpreter will be blocked, but it will still setup the listeners for that process on RabbitMQ.
    This means that you can manipulate the process from another terminal, just as if you would do with a process that is being run by a daemon runner.

In the case of 'pause', 'play' and 'kill', one is sending what is called a Remote Procedure Call (RPC) over RabbitMQ.
The RPC will include the process identifier for which the action is intended and RabbitMQ will send it to whoever registered itself to be listening for that specific process, in this case the runner that is running the process.
This immediately reveals a potential problem: the RPC will fall on deaf ears if there is no one listening, which can have multiple causes.
For example, as explained in the section on a :ref:`process' lifetime<concepts_process_lifetime>`, this can be the case for a submitted process, where the corresponding task is still queued, as all available process slots are occupied.
But even if the task *were* to be with a runner, it might be too busy to respond to the RPC and the process appears to be unreachable.
Whenever a process is unreachable for an RPC, the command will return an error:

.. code:: bash

    Error: Process<100> is unreachable

Depending on the cause of the process being unreachable, the problem may resolve itself automatically over time and one can try again at a later time, as for example in the case of the runner being too busy to respond.
However, to prevent this from happening, the runner has been designed to have the communication happen over a separate thread and to schedule callbacks for any necessary actions on the main thread, which performs all the heavy lifting.
This should make occurrences of the runner being too busy to respond very rare.
If you think the
The problem is, however, there is unfortunately no way of telling what the actual problem is for the process not being reachable.
The problem will manifest itself identically if the runner just could not respond in time or if the task has accidentally been lost forever due to a bug, even though these are two completely separate situations.

This brings us to another potential unintuitive aspect of interacting with processes.
The previous paragraph already mentioned it in passing, but when a remote procedure call is sent, it first needs to be answered by the responsible runner, if applicable, but it will not *directly execute* the call.
This is because the call will be incoming on the communcation thread who is not allowed to have direct access to the process instance, but instead it will schedule a callback on the main thread who can perform the action.
The callback will however not necessarily be executed directly, as there may be other actions waiting to be performed.
So when you pause, play or kill a process, you are not doing so directly, but rather you are *scheduling* a request to do so.
If the runner has successfully received the request and scheduled the callback, the command will therefore show something like the following:

.. code:: bash

    Success: scheduled killing Process<100>

The 'scheduled' indicates that the actual killing might not necessarily have happened just yet.
This means that even after having called ``verdi process kill`` and getting the success message, the corresponding process may still be listed as active in the output of ``verdi process list``.

By default, the ``pause``, ``play`` and ``kill`` commands will only ask for the confirmation of the runner that the request has been scheduled and not actually wait for the command to have been executed.
This is because, as explained, the actual action being performed might not be instantaneous as the runner may be busy working with other processes, which would mean that the command would block for a long time.
If you want to send multiple requests to a lot of processes in one go, this would be ineffective, as each one would have to wait for the previous one to be completed.
To change the default and actually wait for the action to be completed and await its response, you can use the ``--wait`` flag.
If you know that your daemon runners may be experiencing a heavy load, you can also increase the time that the command waits before timing out, with the ``-t/--timeout`` flag.


.. rubric:: Footnotes

.. [#f1] Note that the :py:class:`~aiida.calculations.plugins.arithmetic.add.ArithmeticAddCalculation` process class also takes a ``code`` as input, but that has been omitted for the purposes of the example.
