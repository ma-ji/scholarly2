[![Python package](https://github.com/ma-ji/scholarly2/workflows/Python%20package/badge.svg?branch=main)](https://github.com/ma-ji/scholarly2/actions?query=branch%3Amain)

# scholarly2

`scholarly2` is a fork of [scholarly](https://github.com/scholarly-python-package/scholarly), maintained independently by [Ji Ma](mailto:ma47@iu.edu) **strictly for academic and nonprofit purposes**. It retrieves author and publication data from [Google Scholar](https://scholar.google.com) and returns plain Python dictionaries. The current public workflow is:

- author profiles by Scholar ID with `search_author_id(...)`
- publication lookup with `search_single_pub(...)`
- publication search iterators with `search_pubs(...)`
- citation traversal with `citedby(...)` and `search_citedby(...)`
- BibTeX export with `bibtex(...)`
- journal ranking and mandate CSV endpoints
- proxy configuration, including automatic `.env.socks5` loading and explicit `load_socks5_proxy_file(path)`

Google Scholar behavior changes over time, so exact ranking, citation counts, snippets, and query-token URLs can vary between runs. The parsed result examples below are representative outputs from the current code.

## Installation

Install the latest release from PyPI:

```bash
pip3 install scholarly2
```

Install from GitHub:

```bash
pip3 install -U git+https://github.com/ma-ji/scholarly2.git
```

`scholarly2` follows [Semantic Versioning](https://semver.org/).

### Optional dependencies

Tor support is deprecated since v1.5 and is not actively tested or supported. If you still want it:

```bash
pip3 install scholarly2[tor]
```

For `zsh`, quote the extra:

```zsh
pip3 install scholarly2'[tor]'
```

## Quick Start

```python
from itertools import islice
from scholarly2 import scholarly

# Best-match publication lookup.
pub = scholarly.search_single_pub("10.1007/s11266-018-00057-5")
print(pub["bib"]["title"])

# Publication search returns an iterator, not a list.
results = list(islice(scholarly.search_pubs("machine learning"), 3))
for item in results:
    print(item["gsrank"], item["bib"]["title"])

# Author profile lookup is ID-first.
author = scholarly.search_author_id("Smr99uEAAAAJ")
print(author["name"], author["citedby"])
```

## What You Get Back

All main APIs return plain dictionaries.

Common publication fields:

- `container_type`
- `source`
- `bib`
- `filled`
- `gsrank`
- `pub_url`
- `author_id`
- `num_citations`
- `citedby_url`
- `url_related_articles`
- `url_scholarbib`
- `eprint_url`

Common author fields:

- `container_type`
- `scholar_id`
- `source`
- `name`
- `affiliation`
- `interests`
- `email_domain`
- `homepage`
- `citedby`
- `filled`

`filled` is important:

- `filled: False` means the object only contains the fields parsed from the current search result or profile page.
- `filled: True` means `scholarly.fill(...)` fetched and merged extra metadata.

## Parsed Result Examples

### `search_single_pub(...)`

Best-match publication lookup is useful for exact titles and DOIs.

```python
from scholarly2 import scholarly

pub = scholarly.search_single_pub("10.1007/s11266-018-00057-5")
```

Representative parsed result:

```python
{'container_type': 'Publication',
 'source': <PublicationSource.PUBLICATION_SEARCH_SNIPPET: 'PUBLICATION_SEARCH_SNIPPET'>,
 'bib': {'title': 'A century of nonprofit studies: Scaling the knowledge of the field',
         'author': ['J Ma', 'S Konrath'],
         'pub_year': '2018',
         'venue': 'VOLUNTAS: International Journal of Voluntary and ...',
         'abstract': 'This empirical study examines knowledge production between 1925 and 2015 in nonprofit and philanthropic studies from quantitative and thematic perspectives. Quantitative results suggest that scholars in this field have been actively generating a considerable amount of literature and a solid intellectual base for developing this field toward a new discipline. Thematic analyses suggest that knowledge production in this field is also growing in cohesion-several main themes have been formed and actively advanced since 1980s, and the study of volunteering can be identified as a unique core theme of this field. The lack of geographic and cultural diversity is a critical challenge for advancing nonprofit studies. New paradigms are needed for developing this research field and mitigating the tension between academia and practice. Methodological and pedagogical implications, limitations, and future studies are discussed.'},
 'filled': False,
 'gsrank': 1,
 'pub_url': 'https://www.cambridge.org/core/journals/voluntas/article/century-of-nonprofit-studies-scaling-the-knowledge-of-the-field/...',
 'author_id': ['iVGd04UAAAAJ', '-bDW1IwAAAAJ'],
 'url_scholarbib': '/scholar?hl=en&q=info:veUUt9BplfoJ:scholar.google.com/&output=cite&scirp=0&hl=en',
 'url_add_sclib': '/citations?...&info=veUUt9BplfoJ&json=',
 'num_citations': 124,
 'citedby_url': '/scholar?cites=18056454626157585853&as_sdt=2005&sciodt=0,5&hl=en',
 'url_related_articles': '/scholar?q=related:veUUt9BplfoJ:scholar.google.com/&scioq=10.1007/s11266-018-00057-5&hl=en&as_sdt=0,5',
 'eprint_url': 'https://www.cambridge.org/core/services/aop-cambridge-core/content/view/...pdf'}
```

Notes:

- `search_single_pub(...)` returns one best-match publication.
- When Scholar exposes the expanded `Show more` abstract markup, `scholarly2` prefers that full abstract.
- For exact DOI or exact-title lookups, this path often returns richer abstracts than a broad search page.

### `search_pubs(...)`

`search_pubs(...)` returns an iterator over search results. `next(...)` gives only the first result. Use `itertools.islice` or a loop if you want more than one.

```python
from itertools import islice
from scholarly2 import scholarly

results = list(islice(scholarly.search_pubs("machine learning"), 3))
```

Notes:

- `search_pubs(...)` returns whatever the live Scholar result page exposes for each row.
- If Scholar serves the expanded abstract markup for a result row, `scholarly2` returns the full abstract.
- If Scholar only serves the short snippet, `scholarly2` returns the snippet.

### `fill(...)` on a publication

Use `fill(...)` when you want additional publication metadata after the initial search result.

```python
from scholarly2 import scholarly

pub = scholarly.search_single_pub("10.1007/s11266-018-00057-5")
filled_pub = scholarly.fill(pub)
```

`fill(...)` is where publication objects usually gain fields such as `publisher`, `journal`, `pages`, `volume`, `number`, `pub_type`, and `bib_id`.

### `search_author_id(...)`

Anonymous Google Scholar author-name discovery is not part of the current public workflow. Start from a stable Scholar profile ID.

```python
from scholarly2 import scholarly

author = scholarly.search_author_id("Smr99uEAAAAJ")
```

You can then fetch more sections:

```python
author = scholarly.fill(author, sections=['basics', 'indices', 'counts', 'publications'])
```

## Search Semantics

### `search_single_pub(...)` vs `search_pubs(...)`

- `search_single_pub(query)` returns one best-match result.
- `search_pubs(query)` returns an iterator over search result rows.
- `next(scholarly.search_pubs(...))` returns only the first result.
- Use `itertools.islice(...)` or a loop to consume more results.

### `filled`

- `filled: False` means initial parsed result.
- `filled: True` means additional metadata was fetched.
- Authors use a list of filled sections, such as `['basics']` or `['basics', 'indices', 'counts']`.

## Finding Author IDs

If you have a Scholar profile URL like:

```text
https://scholar.google.com/citations?user=4bahYMkAAAAJ&hl=en
```

Use the `user` parameter value with `search_author_id(...)`.

You can also collect author IDs from publication results:

```python
from scholarly2 import scholarly

pub = scholarly.search_single_pub("Creating correct blur and its effect on accommodation")
print(pub["author_id"])
# ['4bahYMkAAAAJ', '3xJXtlwAAAAJ', 'Smr99uEAAAAJ']
```

## Citations and BibTeX

Get citations for a publication:

```python
from itertools import islice
from scholarly2 import scholarly

pub = scholarly.search_single_pub("10.1007/s11266-018-00057-5")
first_citations = list(islice(scholarly.citedby(pub), 3))
```

Export BibTeX:

```python
from scholarly2 import scholarly

pub = scholarly.search_single_pub("10.1007/s11266-018-00057-5")
print(scholarly.bibtex(pub))
```

## Proxies

Google Scholar rate-limits aggressively. If you make enough requests, you should expect blocking and captcha pages. Use proxies for anything non-trivial.

There are many proxy providers available, I often use [IPRoyal](https://iproyal.com/?r=scholarly2) (disclaimer: this is a referral link). You are welcome to use your own, but make sure you choose `Residential Proxies` (may named differently depending on provider).

For simplicity, only SOCKS5 workflows are recommended. The legacy methods `ScraperAPI()`, `Luminati()`, `FreeProxies()`, `SingleProxy()`, `Tor_External()`, and `Tor_Internal()` remain for compatibility but are deprecated and will be removed in future releases.

### Automatic `.env.socks5` loading

If a `.env.socks5` file exists in your working directory, `scholarly2` loads it automatically at import time. Put one proxy per line in:

```text
USER:PASS@HOST:PORT
```

Example:

```text
user1:password1@127.0.0.1:1080
user2:password2@proxy.example.com:2080
```

See [.env.socks5.example](.env.socks5.example) for the expected format.

### Direct SOCKS5 configuration

Use `ProxyGenerator.Socks5Proxies(...)` when you want to configure the proxy pool in code:

```python
from scholarly2 import ProxyGenerator, scholarly

pg = ProxyGenerator()
pg.Socks5Proxies([
    "user1:password1@127.0.0.1:1080",
    "user2:password2@proxy.example.com:2080",
])
scholarly.use_proxy(pg)

pub = scholarly.search_single_pub("10.1007/s11266-018-00057-5")
```

If you pass only one proxy generator to `scholarly.use_proxy(pg)`, that same SOCKS5 pool is reused for all requests.

### Explicit file loading

Use `load_socks5_proxy_file(path)` to load a proxy file from any location at runtime:

```python
from scholarly2 import scholarly

ok = scholarly.load_socks5_proxy_file("/path/to/my.env.socks5")
if ok:
    print("Proxies loaded")
```

This is useful when your proxy file lives outside the working directory or has a non-standard name. The file format is the same one-proxy-per-line format as `.env.socks5`.

### Deprecated legacy proxy methods

`ProxyGenerator.ScraperAPI()`, `Luminati()`, `FreeProxies()`, `SingleProxy()`, `Tor_External()`, and `Tor_Internal()` are deprecated compatibility paths. Existing code can still call them, but new setups should use `.env.socks5`, `Socks5Proxies(...)`, `Socks5ProxyFile(...)`, or `load_socks5_proxy_file(path)`.

## Availability Notes

Generally usable anonymously:

- `search_author_id`
- `search_pubs`
- `search_single_pub`
- `search_citedby`
- `fill`
- `citedby`
- `bibtex`
- journal endpoints
- mandates CSV retrieval

Google may gate these Citations author-discovery endpoints behind sign-in:

- `search_keyword`
- `search_keywords`
- `search_author_custom_url`
- `search_org`
- `search_author_by_organization`

If you need a reliable author workflow, prefer `search_author_id(...)`.

## Tests

From the repository root:

```bash
python -m unittest -v testdata.test_module
```

Target a smaller subset while iterating:

```bash
python -m unittest -v testdata.test_module.TestPublicationParser
python -m unittest -v testdata.test_module.TestNavigator
```

## Documentation

See the hosted docs for the full API reference and quickstart:

- [API reference](https://scholarly2.readthedocs.io/en/stable/scholarly.html)
- [Quickstart](https://scholarly2.readthedocs.io/en/stable/quickstart.html)

## Contributing

Contributions are welcome. Please create an issue, fork the repository, and submit a pull request. See [.github/CONTRIBUTING.md](.github/CONTRIBUTING.md) for details.

## License

The original code that this project was forked from was released by [Luciano Bello](https://github.com/lbello/chalmers-web) under a [WTFPL](http://www.wtfpl.net/) license. In keeping with that spirit, all code is released under the [Unlicense](http://unlicense.org/).
