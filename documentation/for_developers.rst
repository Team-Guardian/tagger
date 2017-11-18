For Developers
==============

This section takes a deep dive into the internal workings of Tagger source. It is intended for developers looking tomodify or add functionality to the application.

Writing Documentation
---------------------

**Dependencies**
This documentation is created with `Sphinx <http://www.sphinx-doc.org/en/stable/index.html>`_. To make any changes to it, you will need to get Sphinx and ReadTheDocs theme on your machine. Both Sphinx and ReadTheDocs theme can be installed using Pip:

.. code-block:: bash

	pip install Sphinx
	pip install sphinx_rtd_theme

You're now all set up to contribute to this documentation!

**Documentation folder structure**
All the files are stored under ``./documentation`` in the Tagger source directory. Files ending with ``.rst`` are the 'source files' for documentation, written in reStructuredText. These files store all the content and special syntax that defines the appearance. You can find more information on reStructuredText `in this tutorial <https://brandons-sphinx-tutorial.readthedocs.io/en/latest/>`_. From these source files, Sphinx generates a set of HTML files that are stored in ``./documentation/_build/html``.

Once you've finished making changes to any of the ``.rst`` files, you need to update HTML files with a simple command:

.. code-block:: bash

	make html


Setup Tab
---------

The setup tab is the first tab shown when starting up Tagger, and is primarily responsible for creating a new mission or loading an existing one. Since this is the first tab presented to the user, this is probably the best location to add features that the user would want to set before using the application. The full functionality of this tab is described below.


What it shows
~~~~~~~~~~~~~~~~~

**General:**
At the top of the tab, we have access to viewing and changing the current watch directory, as well as enabling and disabling Interop connection and Folder watching.

**Open Existing Flight:**
If a flight has previously been created, the user can select and load that previous flight here.

**Create Flight:**
If no flights exist, a new flight can be created after defining a few details, including location, site elevation, etc.


What controls there are
~~~~~~~~~~~~~~~~~~~~~~~

**Add new flight:**
A new flight can be created after defining required variables, including the flight location, site elevation (MSL), current date, selecting the area map, and choosing the intrinsic matrix for the camera used.

**Load previous flight:**
If a previous flight exists, it can be selected and loaded from a drop-down list here.

**Select Watch Directory:**
Defining the Watch directory folder is required so that Tagger knows where to look when receiving new photos from the aircraft. This can be selected by browsing to the specified folder.

**Enable Interop:**
Interop is the service through which Tagger communicates with the competition judges' servers. From here, we can connect or disconnect from the Interop server. For more information on the AUVSI SUAS Interop, check here: https://github.com/auvsi-suas/interop

Map Tab
-------

The map tab displays an overview of the surrounding flight area, as well as displaying a visual representation of the area already covered by aerial photography. This provides a great overview of the current progress the drone has made in capturing images.

What it shows
~~~~~~~~~~~~~

**Map:**
A high-altitude view of the current flight area is displayed on the right side of the map tab, which also shows an overlay of the area covered by aerial photography. Moving the mouse over the map also displays the approximate latitude and longitude in the lower left corner of the Tagger window.

**Images:**
A list of received images is shown on the left. (TODO: add details about what happens when you click these, etc)


What controls there are
~~~~~~~~~~~~~~~~~~~~~~~

**Latitude and Longitude Search**
By inputting specified coordinates here, Tagger returns the list of images that contain those coordinates.