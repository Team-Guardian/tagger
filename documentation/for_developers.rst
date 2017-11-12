For Developers
==============

This section takes a deep dive into the internal workings of Tagger source. It is intended for developers looking to modify or add functionality to the application.

Writing Documentation
---------------------

**Dependencies** This documentation is created with `Sphinx <http://www.sphinx-doc.org/en/stable/index.html>`_. To make any changes to it, you will need to get Sphinx and ReadTheDocs theme on your machine. Both Sphinx and ReadTheDocs theme can be installed using Pip:

.. code-block:: bash

	pip install Sphinx
	pip install sphinx_rtd_theme

You're now all set up to contribute to this documentation!

**Documentation folder structure** All the files are stored under ``./documentation`` in the Tagger source directory. Files ending with ``.rst`` are the 'source files' for documentation, written in reStructuredText. These files store all the content and special syntax that defines the appearance. You can find more information on reStructuredText `in this tutorial <https://brandons-sphinx-tutorial.readthedocs.io/en/latest/>`_. From these source files, Sphinx generates a set of HTML files that are stored in ``./documentation/_build/html``. 

Once you've finished making changes to any of the ``.rst`` files, you need to update HTML files with a simple command:

.. code-block:: bash

	make html