User Guide
==========

This guide covers the primary methods available in ``scholarly2`` for discovering and retrieving author profiles, publications, and citation networks.

Author Search Methods
---------------------

``search_author_id``
^^^^^^^^^^^^^^^^^^^^
Search for an author by the ID visible in the URL of a Google Scholar author profile.

.. code:: python

    >>> author = scholarly.search_author_id('Smr99uEAAAAJ')
    >>> scholarly.pprint(author)
    {'affiliation': 'Professor of Vision Science, UC Berkeley',
     'email_domain': '@berkeley.edu',
     'filled': False,
     'homepage': 'http://bankslab.berkeley.edu/',
     'interests': ['vision science', 'psychology', 'human factors', 'neuroscience'],
     'name': 'Martin Banks',
     'organization': 11816294095661060495,
     'scholar_id': 'Smr99uEAAAAJ',
     'source': 'AUTHOR_PROFILE_PAGE'}

``search_org``
^^^^^^^^^^^^^^
Search by organization name and return a list of possible disambiguate organizations and their IDs.

.. note::

   This endpoint may require a signed-in Google Scholar Citations session.

.. code:: python

    >>> scholarly.search_org('Princeton University')
    [{'Organization': 'Princeton University', 'id': '4836318610601440500'}]


``search_author_by_organization``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Search for authors belonging to a specific organization ID.

.. note::

   This endpoint may require a signed-in Google Scholar Citations session.

.. code:: python

    >>> search_query = scholarly.search_author_by_organization(4836318610601440500)
    >>> author = next(search_query)

``search_keyword``
^^^^^^^^^^^^^^^^^^
Search by keyword and return a generator of Author objects.

.. note::

   This endpoint may require a signed-in Google Scholar Citations session.

.. code:: python

    >>> search_query = scholarly.search_keyword('Haptics')
    >>> scholarly.pprint(next(search_query))

``search_keywords``
^^^^^^^^^^^^^^^^^^^
Search by multiple keywords and return a generator of Author objects.

.. note::

   This endpoint may require a signed-in Google Scholar Citations session.

.. code:: python

    >>> search_query = scholarly.search_keywords(['crowdsourcing', 'privacy'])
    >>> scholarly.pprint(next(search_query))

``search_author_custom_url``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Search by custom URL and return a generator of Author objects.
The URL should target a Google Scholar Citations author-discovery page.

.. note::

    This endpoint may require a signed-in Google Scholar Citations session.

.. code:: python

    >>> authors = scholarly.search_author_custom_url('/citations?hl=en&view_op=search_authors&mauthors=haptics')
    >>> next(authors)["name"]


Publication Search Methods
--------------------------

``search_pubs``
^^^^^^^^^^^^^^^
Search for articles/publications and return a generator of Publication objects.

.. code:: python

    >>> search_query = scholarly.search_pubs('Perception of physical stability')
    >>> scholarly.pprint(next(search_query))

Please note that the ``author_id`` array is positionally matching with the ``author`` array. You can use the ``author_id`` to get further details about the author using the ``search_author_id`` method.

When Google Scholar includes a ``Show more`` abstract expander for a result, ``scholarly2`` prefers that expanded abstract markup automatically.

``search_single_pub``
^^^^^^^^^^^^^^^^^^^^^
Search for one best-match publication result and optionally fill it in immediately.

.. code:: python

    >>> pub = scholarly.search_single_pub("Machine-learned epidemiology: real-time detection of foodborne illness at scale")
    >>> pub["bib"]["title"]
    'Machine-learned epidemiology: real-time detection of foodborne illness at scale'

    >>> filled_pub = scholarly.search_single_pub(
    ...     "Machine-learned epidemiology: real-time detection of foodborne illness at scale",
    ...     filled=True,
    ... )
    >>> filled_pub["bib"]["publisher"]
    'Nature Publishing Group'

``search_citedby``
^^^^^^^^^^^^^^^^^^
Search by the Google Scholar publication ID from a cited-by URL.

.. code:: python

    >>> pubs = scholarly.search_citedby(2244396665447968936)
    >>> first = next(pubs)
    >>> first["bib"]["title"]
    'Precision medicine, AI, and the future of personalized health care'

``search_pubs_custom_url``
^^^^^^^^^^^^^^^^^^^^^^^^^^
Run a publication query from a custom Scholar URL.

.. code:: python

    >>> pubs = scholarly.search_pubs_custom_url(
    ...     '/scholar?as_q=&as_epq=&as_oq=SFDI+"modulated+imaging"&as_eq=&'
    ...     'as_occt=any&as_sauthors=&as_publication=&as_ylo=2005&as_yhi=2020&'
    ...     'hl=en&as_sdt=0%2C31'
    ... )
    >>> next(pubs)["bib"]["title"]
    'Angle correction for small animal tumor imaging with spatial frequency domain imaging (SFDI)'

``get_related_articles``
^^^^^^^^^^^^^^^^^^^^^^^^
Fetch publications from the "related articles" link of a publication.

.. code:: python

    >>> pub = scholarly.search_single_pub("Planck 2018 results-VI. Cosmological parameters")
    >>> related = scholarly.get_related_articles(pub)
    >>> next(related)["bib"]["title"]
    'Planck 2018 results-VI. Cosmological parameters'


Object Operations
-----------------

``fill``
^^^^^^^^
Fill the Author and Publications container objects with additional information.

**About the Publications:**
By default, scholarly2 returns only a lightly filled object for a publication, to avoid overloading Google Scholar. Call this method when you need complete metadata (e.g., publisher, volume, full abstract).

**About the Authors:**
If the container object passed is an Author, the ``sections`` parameter controls which profile areas to fetch:

-  ``'basics'`` = name, affiliation, and interests;
-  ``'indices'`` = h-index, i10-index, and 5-year analogues;
-  ``'counts'`` = number of citations per year;
-  ``'coauthors'`` = co-authors;
-  ``'publications'`` = publications;
-  ``'public_access'`` = public_access;
-  ``'[]'`` = all of the above (this is the default)

.. code:: python

    >>> author = scholarly.search_author_id('4bahYMkAAAAJ')
    >>> scholarly.pprint(scholarly.fill(author, sections=['basics', 'indices', 'coauthors']))

``citedby``
^^^^^^^^^^^
This is a method for Publication container objects. It searches Google Scholar for other articles that cite this Publication and returns a Publication generator.

.. code:: python

    >>> pub = scholarly.search_single_pub("Machine learning")
    >>> citing_pubs = scholarly.citedby(pub)
    >>> next(citing_pubs)["bib"]["title"]
    'Artificial Intelligence in urban design: A systematic review'

``bibtex``
^^^^^^^^^^
You can export a publication to BibTeX by using the ``bibtex`` property.

.. code:: python

    >>> query = scholarly.search_pubs("A density-based algorithm for discovering clusters...")
    >>> pub = next(query)
    >>> scholarly.bibtex(pub)

This outputs a standard BibTeX entry ready for inclusion in your citation manager.


Journals and Funding Mandates
-----------------------------

``get_journal_categories``
^^^^^^^^^^^^^^^^^^^^^^^^^^
Get a dictionary of journal categories and subcategories.

.. code:: python

    >>> categories = scholarly.get_journal_categories()
    >>> print(list(categories.keys())[:3])
    ['Business, Economics & Management', 'Chemical & Material Sciences', 'Engineering & Computer Science']

``get_journals``
^^^^^^^^^^^^^^^^
Fetch top-ranking journals for a specific category and subcategory.

.. code:: python

    >>> journals = scholarly.get_journals(category='Engineering & Computer Science', subcategory='Computer Vision & Pattern Recognition')
    >>> print(journals)

``save_journals_csv``
^^^^^^^^^^^^^^^^^^^^^
Save a list of top-ranking journals to a file in CSV format.

.. code:: python

    >>> scholarly.save_journals_csv("journals.csv", category="English", subcategory="Computer Vision & Pattern Recognition")

``download_mandates_csv``
^^^^^^^^^^^^^^^^^^^^^^^^^
Download a table of funding agencies as a CSV file with URLs to the funding mandates included.

.. code:: python

    >>> scholarly.download_mandates_csv("mandates.csv")
