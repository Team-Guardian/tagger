For Developers
==============

This section takes a deep dive into the internal workings of Tagger source. It is intended for developers looking to modify or add functionality to the application.

Writing Documentation
---------------------

**Dependencies.** This documentation is created with `Sphinx <http://www.sphinx-doc.org/en/stable/index.html>`_. To make any changes to it, you will need to get Sphinx and ReadTheDocs theme on your machine. Both Sphinx and ReadTheDocs theme can be installed using Pip:

.. code-block:: bash

	pip install Sphinx
	pip install sphinx_rtd_theme

You're now all set up to contribute to this documentation!

**Documentation folder structure.** All the files are stored under ``./documentation`` in the Tagger source directory. Files ending with ``.rst`` are the 'source files' for documentation, written in reStructuredText. These files store all the content and special syntax that defines the appearance. You can find more information on reStructuredText `in this tutorial <https://brandons-sphinx-tutorial.readthedocs.io/en/latest/>`_. From these source files, Sphinx generates a set of HTML files that are stored in ``./documentation/_build/html``.

Once you've finished making changes to any of the ``.rst`` files, you need to update HTML files with a simple command:

.. code-block:: bash

	make html

Targets Tab
-----------

View all the images that contain a target in the **Targets** tab. This tab acts as a dashboard for tagging process, and thus features minimal controls.

What information it shows
~~~~~~~~~~~~~~~~~~~~~~~~~

Information displayed in the Targets tab depends on *tags*, *markers*, and *images* stored in the database.

**Tagged Images.** Select a tag to see a list of images that contain the selected tag. An image appears on the list if:

- Image was marked with one or more instances of the selected tag;
- Geographic bounding box captured by the image encloses one or more existing instances of the selected tag;

**Image Viewer.** Select an image from the list to have it appear in the viewer pane.

What controls there are
~~~~~~~~~~~~~~~~~~~~~~~

**Image Context Menu.** Right-click on the image in the viewer pane to bring up the context menu. Through the context menu, you can:

- Go to the current image in the **Tagging** tab;

Interface
~~~~~~~~~

Targets tab must provide an interface to update the tab when a table in the database containing *tags*, *markers*, or *images* is changed. Updates are triggered by each of these events:

- New image has been added to the database;
- New tag was created;
- Tag was edited;
- Tag was deleted;
- New marker was created;
- Marker was deleted;

Tagging Tab
-----------
The tagging tab allows the user to review images and tag objects in images.

What information it shows
~~~~~~~~~~~~~

**Tags**
The tags created by the user are stored here for easy access. The tags can be sorted by their following characteristics: Type, Subtype, Current (Total), and Icon. Tags can be edited or removed in this section, and will also be removed on the big map showing all tags. Tags can also be added to images and new additions will be added here.

**Images**
The Images section shows all the images taken and they can come in in real time. The images are seperated into three main groups: images that have been reviewed, images that have not been reviewed, and all images. 

**Map**
If an image is selected for review, it is displayed onto the right portion of the window where the user can add or remove tags on the image.

What controls there are
~~~~~~~~~~~~~~~~~~~~~~~

**Adding Tags**
To add tag an object in the image, first click add under the Tags section and fill in corresponding characteristics. Then hover over object in the image and right click to tag it. 

**Determining Geolocation**
If the cursor is on the image, the bottom left of the window indicates the latitude, longitude, elevation, and the UAV's rotation about three axis.  

**Zoom and Pan Images**
To zoom, use the scroll wheel then click and drag to pan around the image. 
