Installation Instructions
=========================

*WIP, please mention in Slack if you are having difficulty getting Tagger installed or if you see anything missing here!*

This section provides a step-by-step guide to get Tagger up and running on Ubuntu. This guide follows what has been described in the ``README.md`` file that accompanies Tagger and from personal experience installing Tagger.
*We don't have a .sh file ready yet to automate this installation, but we'll have one at some point :)*

**1. Cloning Tagger**

*TODO*


**2. Installing Dependancies**


In Ubuntu, pull up the **terminal** window by either clicking the Ubuntu icon in the upper-left corner and typing ``terminal``, or using the keyboard shortcut Ctrl + Alt + T.

In the new terminal window, type or copy-paste the following. This will install the dependancies listed in the ``README.md`` file in the base directory of Tagger.

.. code-block:: bash

    sudo apt-get update
    sudo apt-get install qttools5-dev-tools python-pyqt5 postgresql python-psycopg2  python-pip pgadmin3 python-pyexiv2 python-numpy python-gdal pyqt5-dev-tools
    sudo -H pip install django
    sudo -H pip install setuptools
    sudo -H pip install watchdog

**3. PostgreSQL Installation and Setup**


With Terminal open, log in as user *postgres*:

    ``sudo -i -u postgres``

Run the postgreSQL terminal interface:

    ``psql``

Change password of currently postgres user to *postgres*

    ``\password``

    ``postgres``

    ``postgres``

Create a new database called *tagger* and set owner to *postgres* user.

    ``create database tagger with owner postgres;``

    ``\q``

Log out

    ``exit``

Restart postgreSQL service

    ``sudo service postgresql restart``

**4. Creating Database Schema**

In in the root of the project folder **tagger**


    ``python manage.py makemigrations``

    ``python manage.py migrate``

*This concludes the general installation instructions in the* ``README.md`` *file.*


**5. Setup Interop and Docker**

With a terminal window open, navigate the the directory one down from Tagger. For example, if Tagger is at ``username@Ubuntu:~/tagger$``, use ``cd`` to navigate to ``username@Ubuntu:~$``. Type or copy paste the following into terminal:

	``git clone https://github.com/auvsi-suas/interop``

Next, navigate to inside the Interop folder using the following commands:

	``cd ~/interop``

	``sudo ./tools/setup_docker.sh``

*This may take some time to complete!*

*(TODO: verify that all the steps above are all that is required to begin using Tagger)*

Now, to set up the Interop server,

	``cd ~/interop`` *(if you aren’t already in that directory)*
	``sudo ./server/run.sh``

	*Will also take a long time! Let it run until completion.*

To Stop & Start the server:

	``sudo docker stop interop-server``

	``sudo docker start interop-server``

**6. Run Tagger**
	With a terminal window open, navigate to the Tagger folder you cloned earlier:

	``cd /tagger``

	``python main.py``

Congratulations! Tagger should now be up and running! Again, if you had any difficulty installing Tagger by following this guide, please let us know on Slack so we can adjust the guide accordingly to help out others. Thanks!

*Last updated November 17, 2017 by James Evans*