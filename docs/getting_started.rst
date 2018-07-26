Getting Started
===============

By following the steps on this page, you will get your system ready for running and developing Tagger.

System Requirements
-------------------

Tagger was developed and tested on Ubuntu 16.04 and 18.04. It will likely work on other OSes similar to Ubuntu, like Linux Mint and Pop!_OS, but that's not guaranteed.

Downloading Tagger
------------------

You can download Tagger source code from Guardian's `GitHub repository <https://github.com/Team-Guardian/tagger>`_. Although you can download the files as a zip file using your browser, it's better to learn how to use ``git`` because GitHub is designed to be used with it. 

Ubuntu distributions don't include ``git`` out-of-the-box, so you would need to install that first. From your terminal, run the following command.

.. code-block:: bash

    sudo apt-get install git

If you're confused with what is happening and you're just starting to use Ubuntu, stop reading this guide and go through this great `command-line tutorial <https://www.learnenough.com/command-line-tutorial>`_ before continuing.

After you install Git, use it to download Tagger with this command.

.. code-block:: bash

    git clone https://github.com/Team-Guardian/tagger.git

If Tagger was downloaded successfully, there will now be a folder called ``tagger`` in your current directory (hint: use ``pwd`` to get the full path of the directory you're in and ``ls`` to list the files and folders that are in it). For the rest of the steps in this guide, you need to be inside the ``tagger`` folder.

.. code-block:: bash

    cd tagger

Also, when you download a project from GitHub, by default it shows the files on the master branch (confused? here's another great `tutorial <https://www.learnenough.com/git-tutorial>`_ that explains Git. Change to the ``development`` branch before continuing.

.. code-block:: bash

    git checkout development
    git pull

Collecting Dependencies
-----------------------

Tagger uses `Pipenv <https://docs.pipenv.org/>`_ to manage Python package dependencies. A tool inspired by packaging managers from other languages, Pipenv has an additional benefit of automatically creating and managing a virtual environment for your project to keep package dependencies isolated - you can read more about the tool in the :doc:`guide for developers <./for_developers>`.

Another set of dependencies that must be installed are system packages. Included in the repository is an installation script, ``install.sh``, that takes care of system-wide and Python dependencies. Simply run the script to finish collecting dependencies for Tagger.

.. code-block:: bash

    sudo sh install.sh

Output of the script is written to the log file, ``.install.log``.

Setup PostgreSQL
----------------

PostgreSQL is a database management software that Tagger uses to organize its data about flights, images, targets, etc. Before running Tagger, we have to create a local instance of the database (confused? there's no tutorial this time - it's a difficult topic, but you don't really need to know it to work with Tagger).

Start by logging in as user ``postgres``.

.. code-block:: bash

    sudo -i -u postgres

Next, launch the PostgreSQL terminal interface, ``psql``.

.. code-block:: bash

    psql

Your terminal prompt should be changing after running each of these two commands. After you launch ``psql``, change the default password to ``postgres`` (note: commands in ``psql`` are prepended with ``\`` and to change the password you will be prompted to enter it twice; and remember, you won't see the password you're typing).

.. code-block:: bash

    \password
    postgres
    postgres

After you change the password, create a database called ``tagger`` with user ``postgres``.

.. code-block:: bash

    create database tagger with owner postgres;
    \q

Log out of the user ``postgres``.

.. code-block:: bash

    exit

Finally, restart the PostgreSQL service.

.. code-block:: bash

    sudo service postgresql restart

Running Tagger
--------------

Because Pipenv installed dependencies in a virtual environment that it has created, to run Tagger you would first need to activate the virtual environment. To do that, start a Pipenv "shell".

.. code-block:: bash

    sudo python3 -m pipenv shell

If the virtual environment is activated successfully, you should see the terminal prompt prepended with the name of the virtual environment.

In the previous step, we created an empty database. Now we need to tell it how we want it to be laid out (in other words, what kind of data we want to store in and how it should be organized).

.. code-block:: bash

    python3 manage.py migrate

You should now be able to launch the Tagger GUI with the following command.

.. code-block:: bash

    python3 main.py