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

Methods for ``scholar``
-----------------------

Author-name search via Google Scholar Citations is not available in
``scholarly2`` because Google gates that endpoint behind sign-in. Use
``search_author_id`` when you need to start from an author profile.

``search_author_id``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Search for an author by the id visible in the url of an Authors profile.
########################################################################

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

``search_author_by_organization``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Search for authors by organization ID.
########################################################################

.. note::

   This endpoint may require a signed-in Google Scholar Citations session.

.. code:: python

    >>> scholarly.search_org('Princeton University')
    [{'Organization': 'Princeton University', 'id': '4836318610601440500'}]

    >>> search_query = scholarly.search_author_by_organization(4836318610601440500)
    >>> author = next(search_query)
    >>> scholarly.pprint(author)
        {'affiliation': 'Princeton University (Emeritus)',
         'citedby': 438891,
         'email_domain': '@princeton.edu',
         'filled': False,
         'interests': ['Daniel Kahneman'],
         'name': 'Daniel Kahneman',
         'scholar_id': 'ImhakoAAAAAJ',
         'source': 'SEARCH_AUTHOR_SNIPPETS',
         'url_picture': 'https://scholar.google.com/citations?view_op=medium_photo&user=ImhakoAAAAAJ'}

``search_keyword``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Search by keyword and return a generator of Author objects.
###########################################################

.. note::

   This endpoint may require a signed-in Google Scholar Citations session.

.. code:: python

    >>> search_query = scholarly.search_keyword('Haptics')
    >>> scholarly.pprint(next(search_query))
    {'affiliation': 'Postdoctoral research assistant, University of Bremen',
     'citedby': 56666,
     'email_domain': '@collision-detection.com',
     'filled': False,
     'interests': ['Computer Graphics',
                   'Collision Detection',
                   'Haptics',
                   'Geometric Data Structures'],
     'name': 'Rene Weller',
     'scholar_id': 'lHrs3Y4AAAAJ',
     'source': 'SEARCH_AUTHOR_SNIPPETS',
     'url_picture': 'https://scholar.google.com/citations?view_op=medium_photo&user=lHrs3Y4AAAAJ'}

``search_pubs``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Search for articles/publications and return generator of Publication objects.
#############################################################################

.. code:: python

    >>> search_query = scholarly.search_pubs('Perception of physical stability and center of mass of 3D objects')
    >>> scholarly.pprint(next(search_query))
    {'author_id': ['4bahYMkAAAAJ', 'ruUKktgAAAAJ', ''],
     'bib': {'abstract': 'Humans can judge from vision alone whether an object is '
                         'physically stable or not. Such judgments allow observers '
                         'to predict the physical behavior of objects, and hence '
                         'to guide their motor actions. We investigated the visual '
                         'estimation of physical stability of 3-D objects (shown '
                         'in stereoscopically viewed rendered scenes) and how it '
                         'relates to visual estimates of their center of mass '
                         '(COM). In Experiment 1, observers viewed an object near '
                         'the edge of a table and adjusted its tilt to the '
                         'perceived critical angle, ie, the tilt angle at which '
                         'the object',
             'author': ['SA Cholewiak', 'RW Fleming', 'M Singh'],
             'pub_year': '2015',
             'title': 'Perception of physical stability and center of mass of 3-D '
                      'objects',
             'venue': 'Journal of vision'},
     'citedby_url': '/scholar?cites=15736880631888070187&as_sdt=5,33&sciodt=0,33&hl=en',
     'eprint_url': 'https://jov.arvojournals.org/article.aspx?articleID=2213254',
     'filled': False,
     'gsrank': 1,
     'num_citations': 23,
     'pub_url': 'https://jov.arvojournals.org/article.aspx?articleID=2213254',
     'source': 'PUBLICATION_SEARCH_SNIPPET',
     'url_scholarbib': '/scholar?q=info:K8ZpoI6hZNoJ:scholar.google.com/&output=cite&scirp=0&hl=en'}

Please note that the ``author_id`` array is positionally matching with
the ``author`` array. You can use the ``author_id`` to get further
details about the author using the ``search_author_id`` method.

When Google Scholar includes a ``Show more`` abstract expander for a result,
``scholarly2`` prefers that expanded abstract markup automatically. In those
cases, ``pub["bib"]["abstract"]`` contains the full Scholar abstract rather
than the collapsed preview text.

``search_single_pub``
^^^^^^^^^^^^^^^^^^^^^

Search for one best-match publication result and optionally fill it in
immediately.
##############################################################

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
##################################################################

.. code:: python

    >>> pubs = scholarly.search_citedby(2244396665447968936)
    >>> first = next(pubs)
    >>> first["bib"]["title"]
    'Precision medicine, AI, and the future of personalized health care'

``fill``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Fill the Author and Publications container objects with additional information.
###############################################################################

About the Publications:
'''''''''''''''''''''''

By default, scholarly2 returns only a lightly filled object for
publication, to avoid overloading Google Scholar. If necessary to get
more information for the publication object, we call this method.

About the Authors:
''''''''''''''''''

If the container object passed to this method is an Author, the sections
desired to be filled can be selected to populate the author with
information from their profile, via the ``sections`` parameter.

The optional ``sections`` parameter takes a list of the portions of
author information to fill, as follows:

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

This is a method for the Publication container objects. It searches
Google Scholar for other articles that cite this Publication and returns
a Publication generator.

.. code:: python

    >>> pub = scholarly.search_single_pub("Machine learning")
    >>> citing_pubs = scholarly.citedby(pub)
    >>> next(citing_pubs)["bib"]["title"]
    'Artificial Intelligence in urban design: A systematic review'

``bibtex``
^^^^^^^^^^

You can export a publication to Bibtex by using the ``bibtex`` property.
Here's a quick example:

.. code:: python

    >>> query = scholarly.search_pubs("A density-based algorithm for discovering clusters in large spatial databases with noise")
    >>> pub = next(query)
    >>> scholarly.bibtex(pub)

by running the code above you should get the following Bibtex entry:

.. code:: bib

    @inproceedings{ester1996density,
     abstract = {Clustering algorithms are attractive for the task of class identification in spatial databases. However, the application to large spatial databases rises the following requirements for clustering algorithms: minimal requirements of domain knowledge to determine the input},
     author = {Ester, Martin and Kriegel, Hans-Peter and Sander, J{\"o}rg and Xu, Xiaowei and others},
     booktitle = {Kdd},
     number = {34},
     pages = {226--231},
     pub_year = {1996},
     title = {A density-based algorithm for discovering clusters in large spatial databases with noise.},
     venue = {Kdd},
    volume = {96}
    }

``search_pubs_custom_url``
^^^^^^^^^^^^^^^^^^^^^^^^^^

Run a publication query from a custom Scholar URL.
##################################################

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
#####################################################################

.. code:: python

    >>> pub = scholarly.search_single_pub("Planck 2018 results-VI. Cosmological parameters")
    >>> related = scholarly.get_related_articles(pub)
    >>> next(related)["bib"]["title"]
    'Planck 2018 results-VI. Cosmological parameters'

Using proxies
-------------

In general, Google Scholar does not like bots, and can often block
scholarly2, especially those pages that contain ``scholar?`` in the URL.

There is a class in the scholarly2 library, which handles all these
different types of connections for you, called ``ProxyGenerator``.

To use this class simply import it from the scholarly2 package:

.. code:: python

    from scholarly2 import ProxyGenerator

Then you need to initialize an object:

.. code:: python

    pg = ProxyGenerator()

Only SOCKS5 workflows are recommended. Use one of the following:

-  ``Socks5Proxies()``
-  ``Socks5ProxyFile()``
-  ``scholarly.load_socks5_proxy_file()``

The legacy methods ``ScraperAPI()``, ``Luminati()``, ``FreeProxies()``,
``SingleProxy()``, ``Tor_Internal()``, and ``Tor_External()`` remain
available for compatibility, but they are deprecated and should not be
used for new setups.

``Automatic .env.socks5 loading``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If a ``.env.socks5`` file exists in your working directory, ``scholarly2``
loads it automatically at import time. Use one proxy per line in the format
``USER:PASS@HOST:PORT``.

.. code:: text

    user1:password1@127.0.0.1:1080
    user2:password2@proxy.example.com:2080

See ``.env.socks5.example`` in the repository root for the expected format.

``Socks5Proxies``
^^^^^^^^^^^^^^^^^
pg.Socks5Proxies()
##################

Use this when you want to define the SOCKS5 proxy pool directly in code.

.. code:: python

    from scholarly2 import scholarly, ProxyGenerator

    pg = ProxyGenerator()
    success = pg.Socks5Proxies([
        "user1:password1@127.0.0.1:1080",
        "user2:password2@proxy.example.com:2080",
    ])
    scholarly.use_proxy(pg)

    author = scholarly.search_author_id('4bahYMkAAAAJ')
    scholarly.pprint(author)

If you pass only one proxy generator to ``scholarly.use_proxy(pg)``, that
same SOCKS5 pool is reused for all requests.

``Socks5ProxyFile``
^^^^^^^^^^^^^^^^^^^
pg.Socks5ProxyFile()
####################

Use this when you already have a proxy file and want to attach it through a
``ProxyGenerator`` instance.

.. code:: python

    from scholarly2 import scholarly, ProxyGenerator

    pg = ProxyGenerator()
    success = pg.Socks5ProxyFile("/path/to/my.env.socks5")
    scholarly.use_proxy(pg)

    author = scholarly.search_author_id('4bahYMkAAAAJ')
    scholarly.pprint(author)

``load_socks5_proxy_file``
^^^^^^^^^^^^^^^^^^^^^^^^^^

Load a SOCKS5 proxy file from an explicit path at runtime.
##########################################################

This is useful when the proxy file lives outside the working directory or
has a non-standard name. The file format is the same as ``.env.socks5``:
one ``USER:PASS@HOST:PORT`` entry per line, blank lines and ``#`` comments
are ignored.

.. code:: python

    from scholarly2 import scholarly

    ok = scholarly.load_socks5_proxy_file("/path/to/my.env.socks5")
    if ok:
        print("Proxies loaded")

``Deprecated legacy proxy methods``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following compatibility methods are deprecated and may be removed in a
future release:

-  ``pg.ScraperAPI()``
-  ``pg.Luminati()``
-  ``pg.FreeProxies()``
-  ``pg.SingleProxy()``
-  ``pg.Tor_External()``
-  ``pg.Tor_Internal()``

Prefer ``Socks5Proxies()``, ``Socks5ProxyFile()``, or
``scholarly.load_socks5_proxy_file()`` instead.


Setting up environment for proxy testing
----------------------------------------

For local testing, the recommended setup is a ``.env.socks5`` file in your
working directory. ``scholarly2`` will automatically load it on import.
Use one proxy per line in the format ``USER:PASS@HOST:PORT``. See
``.env.socks5.example`` in the repository root for an example.

.. code:: text

    user1:password1@127.0.0.1:1080
    user2:password2@proxy.example.com:2080

You can also load a proxy file explicitly at runtime using
``scholarly.load_socks5_proxy_file(path)``.

Legacy compatibility tests can still use ``CONNECTION_METHOD`` in a ``.env``
file, but all non-SOCKS5 options are deprecated:

-  ``luminati`` (deprecated)
-  ``scraperapi`` (deprecated)
-  ``freeproxy`` (deprecated)
-  ``tor`` (deprecated)
-  ``tor_internal`` (deprecated)
-  ``none``
