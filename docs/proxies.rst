Using Proxies
=============

In general, Google Scholar strictly limits automated requests and blocks scrapers with CAPTCHAs. For anything beyond trivial local testing, you must configure a proxy.

``scholarly2`` requires a SOCKS5 proxy pool.

Automatic ``.env.socks5`` loading
---------------------------------

If a ``.env.socks5`` file exists in your working directory, ``scholarly2`` loads it automatically at import time. This is the recommended setup for both local testing and production. 

Use one proxy per line in the format ``USER:PASS@HOST:PORT``.

.. code:: text

    user1:password1@127.0.0.1:1080
    user2:password2@proxy.example.com:2080

See ``.env.socks5.example`` in the repository root for an example.

Direct Configuration (ProxyGenerator)
-------------------------------------

If you need to manage connections manually, use the ``ProxyGenerator`` class.

.. code:: python

    from scholarly2 import ProxyGenerator

    pg = ProxyGenerator()

``Socks5Proxies``
^^^^^^^^^^^^^^^^^

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

If you pass only one proxy generator to ``scholarly.use_proxy(pg)``, that same SOCKS5 pool is reused for all requests.

``Socks5ProxyFile``
^^^^^^^^^^^^^^^^^^^

Use this when you already have a proxy file and want to attach it through a ``ProxyGenerator`` instance.

.. code:: python

    from scholarly2 import scholarly, ProxyGenerator

    pg = ProxyGenerator()
    success = pg.Socks5ProxyFile("/path/to/my.env.socks5")
    scholarly.use_proxy(pg)

``load_socks5_proxy_file``
^^^^^^^^^^^^^^^^^^^^^^^^^^

Load a SOCKS5 proxy file from an explicit path at runtime. This is a top-level convenience method.

This is useful when the proxy file lives outside the working directory or has a non-standard name. The file format is the same as ``.env.socks5``: one ``USER:PASS@HOST:PORT`` entry per line. Blank lines and ``#`` comments are ignored.

.. code:: python

    from scholarly2 import scholarly

    ok = scholarly.load_socks5_proxy_file("/path/to/my.env.socks5")
    if ok:
        print("Proxies loaded")


Deprecated Legacy Proxies
-------------------------

The following compatibility methods are deprecated and may be removed in a future release. All new setups should use SOCKS5 workflows.

-  ``pg.ScraperAPI()``
-  ``pg.Luminati()``
-  ``pg.FreeProxies()``
-  ``pg.SingleProxy()``
-  ``pg.Tor_External()``
-  ``pg.Tor_Internal()``
