Quickstart
==========

.. note::

   ``scholarly2`` is a fork of `scholarly <https://github.com/scholarly-python-package/scholarly>`. Many major updates and fixes have been made to the original package.

Installation
------------

Use ``pip`` to install from PyPI:

.. code:: bash

    pip3 install scholarly2

or install from GitHub:

.. code:: bash

    pip install git+https://github.com/ma-ji/scholarly2.git


Usage
-----

Because ``scholarly2`` does not use an official API, no key is required.
Simply:

.. code:: python

    from scholarly2 import scholarly

    print(scholarly.search_author_id('4bahYMkAAAAJ'))

Example
-------

Here's a quick example demonstrating how to retrieve an author's profile
then retrieve the titles of the papers that cite his most popular
(cited) paper.

.. code:: python

    from scholarly2 import scholarly

    # Retrieve the author's data, fill-in, and print
    author = scholarly.search_author_id('4bahYMkAAAAJ')
    author = scholarly.fill(author)
    print(author)

    # Print the titles of the author's publications
    print([pub['bib']['title'] for pub in author['publications']])

    # Take a closer look at the first publication
    pub = scholarly.fill(author['publications'][0])
    print(pub)

    # Which papers cited that publication?
    print([citation['bib']['title'] for citation in scholarly.citedby(pub)])

Availability notes
------------------

The following methods work well with anonymous access:

- ``search_author_id``
- ``search_pubs``
- ``search_single_pub``
- ``search_citedby``
- ``fill``
- ``citedby``
- ``bibtex``
- ``get_journal_categories`` / ``get_journals`` / ``save_journals_csv``
- ``download_mandates_csv``

The following methods use Google Scholar Citations author-discovery
pages and Google may gate them behind sign-in for anonymous sessions:

- ``search_keyword``
- ``search_keywords``
- ``search_author_custom_url``
- ``search_org``
- ``search_author_by_organization``

Finding author IDs
------------------

If you have a Google Scholar profile URL, use the ``user`` query
parameter directly:

.. code:: text

    https://scholar.google.com/citations?user=4bahYMkAAAAJ&hl=en

In the example above, the author ID is ``4bahYMkAAAAJ``.

You can also discover author IDs from publication results:

.. code:: python

    >>> pub = scholarly.search_single_pub("Creating correct blur and its effect on accommodation")
    >>> pub["author_id"]
    ['4bahYMkAAAAJ', '3xJXtlwAAAAJ', 'Smr99uEAAAAJ']
