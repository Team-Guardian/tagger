Getting Started
===============

By following the steps on this page, you will get your system ready for running and developing Tagger.

Collect Dependencies
--------------------

Tagger uses `Pipenv <https://docs.pipenv.org/>`_ to manage Python package dependencies. A tool inspired by packaging managers from other languages, Pipenv has an additional benefit of automatically creating and managing a virtual environment for your project to keep package dependencies isolated - you can read more about the tool in the :doc:`guide for developers <./for_developers>`.

Another set of dependencies that must be installed are system packages. Included in the repository is an installation script, ``install.sh``, that takes care of system-wide and Python dependencies. Simply run the script to finish collecting dependencies for Tagger.

.. code-block:: bash

    sudo sh install.sh

Output of the script is written to the log file, ``.install.log``.

Running Tagger
--------------

Because Pipenv installed dependencies in a virtual environment that it has created, to run Tagger you would first need to activate the virtual environment. To do that, start a Pipenv "shell".

.. code-block:: bash

    pipenv shell

If the virtual environment is activated successfully, you should see the terminal prompt prepended with the name of the virtual environment.

You should now be able to launch the Tagger GUI with the following command.

.. code-block:: bash

    python3 main.py