[![Python package](https://github.com/scholarly-python-package/scholarly/workflows/Python%20package/badge.svg?branch=main)](https://github.com/scholarly-python-package/scholarly/actions?query=branch%3Amain)
[![codecov](https://codecov.io/gh/scholarly-python-package/scholarly/branch/main/graph/badge.svg?token=0svtI9yVSQ)](https://codecov.io/gh/scholarly-python-package/scholarly)
[![Documentation Status](https://readthedocs.org/projects/scholarly/badge/?version=latest)](https://scholarly.readthedocs.io/en/latest/?badge=latest)
[![DOI](https://zenodo.org/badge/27442991.svg)](https://zenodo.org/badge/latestdoi/27442991)

# scholarly

`scholarly` retrieves author and publication data from [Google Scholar](https://scholar.google.com) and returns plain Python dictionaries. The current public workflow is:

- author profiles by Scholar ID with `search_author_id(...)`
- publication lookup with `search_single_pub(...)`
- publication search iterators with `search_pubs(...)`
- citation traversal with `citedby(...)` and `search_citedby(...)`
- BibTeX export with `bibtex(...)`
- journal ranking and mandate CSV endpoints
- proxy configuration, including automatic `.env.socks5` loading

Google Scholar behavior changes over time, so exact ranking, citation counts, snippets, and query-token URLs can vary between runs. The parsed result examples below are representative outputs from the current code.

## Installation

[![Anaconda-Server Badge](https://anaconda.org/conda-forge/scholarly/badges/version.svg)](https://anaconda.org/conda-forge/scholarly)
[![PyPI version](https://badge.fury.io/py/scholarly.svg)](https://badge.fury.io/py/scholarly)

Install with `conda`:

```bash
conda install -c conda-forge scholarly
```

Install the latest release from PyPI:

```bash
pip3 install scholarly
```

Install from GitHub:

```bash
pip3 install -U git+https://github.com/scholarly-python-package/scholarly.git
```

`scholarly` follows [Semantic Versioning](https://semver.org/).

### Optional dependencies

Tor support is deprecated since v1.5 and is not actively tested or supported. If you still want it:

```bash
pip3 install scholarly[tor]
```

For `zsh`, quote the extra:

```zsh
pip3 install scholarly'[tor]'
```

## Quick Start

```python
from itertools import islice
from scholarly import scholarly

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
from scholarly import scholarly

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
- When Scholar exposes the expanded `Show more` abstract markup, `scholarly` prefers that full abstract.
- For exact DOI or exact-title lookups, this path often returns richer abstracts than a broad search page.

### `search_pubs(...)`

`search_pubs(...)` returns an iterator over search results. `next(...)` gives only the first result. Use `itertools.islice` or a loop if you want more than one.

```python
from itertools import islice
from scholarly import scholarly

results = list(islice(scholarly.search_pubs("machine learning"), 3))
```

Representative parsed results:

```python
[{'container_type': 'Publication',
  'source': <PublicationSource.PUBLICATION_SEARCH_SNIPPET: 'PUBLICATION_SEARCH_SNIPPET'>,
  'bib': {'title': 'Machine learning',
          'author': ['ZH Zhou'],
          'pub_year': '2021',
          'venue': 'NA',
          'abstract': 'from data is called learning or training. The machine learning is to find or approximate ground-truth. In this book, models are sometimes called learners, which are machine learning'},
  'filled': False,
  'gsrank': 1,
  'pub_url': 'https://books.google.com/books?...',
  'author_id': ['rSVIHasAAAAJ'],
  'url_scholarbib': '/scholar?hl=en&q=info:EQ8shYj8Ai8J:scholar.google.com/&output=cite&scirp=0&hl=en',
  'url_add_sclib': '/citations?...&info=EQ8shYj8Ai8J&json=',
  'num_citations': 3609,
  'citedby_url': '/scholar?cites=3387547533016043281&as_sdt=5,33&sciodt=0,33&hl=en',
  'url_related_articles': '/scholar?q=related:EQ8shYj8Ai8J:scholar.google.com/&scioq=machine+learning&hl=en&as_sdt=0,33'},
 {'container_type': 'Publication',
  'source': <PublicationSource.PUBLICATION_SEARCH_SNIPPET: 'PUBLICATION_SEARCH_SNIPPET'>,
  'bib': {'title': 'Machine learning',
          'author': ['E Alpaydin'],
          'pub_year': '2021',
          'venue': 'NA',
          'abstract': 'MIT presents a concise primer on machine learning-computer programs that learn from data and the basis of applications like voice recognition and driverless cars. No in-depth'},
  'filled': False,
  'gsrank': 2,
  'pub_url': 'https://books.google.com/books?...',
  'author_id': [''],
  'url_scholarbib': '/scholar?hl=en&q=info:_zuqxloS2b0J:scholar.google.com/&output=cite&scirp=1&hl=en',
  'url_add_sclib': '/citations?...&info=_zuqxloS2b0J&json=',
  'num_citations': 1611,
  'citedby_url': '/scholar?cites=13679985524203994111&as_sdt=5,33&sciodt=0,33&hl=en',
  'url_related_articles': '/scholar?q=related:_zuqxloS2b0J:scholar.google.com/&scioq=machine+learning&hl=en&as_sdt=0,33',
  'eprint_url': 'https://cs.pomona.edu/~dkauchak/classes/.../lecture12-NN-basics.pdf'},
 {'container_type': 'Publication',
  'source': <PublicationSource.PUBLICATION_SEARCH_SNIPPET: 'PUBLICATION_SEARCH_SNIPPET'>,
  'bib': {'title': 'Machine learning: Trends, perspectives, and prospects',
          'author': ['MI Jordan', 'TM Mitchell'],
          'pub_year': '2015',
          'venue': 'Science',
          'abstract': 'Machine learning addresses the question of how to build computers that improve Recent progress in machine learning has been driven both by the development of new learning'},
  'filled': False,
  'gsrank': 3,
  'pub_url': 'https://www.science.org/doi/abs/10.1126/science.aaa8415',
  'author_id': ['yxUduqMAAAAJ', 'MnfzuPYAAAAJ'],
  'url_scholarbib': '/scholar?hl=en&q=info:pdcI9r5sCJcJ:scholar.google.com/&output=cite&scirp=2&hl=en',
  'url_add_sclib': '/citations?...&info=pdcI9r5sCJcJ&json=',
  'num_citations': 14120,
  'citedby_url': '/scholar?cites=10883068066968164261&as_sdt=5,33&sciodt=0,33&hl=en',
  'url_related_articles': '/scholar?q=related:pdcI9r5sCJcJ:scholar.google.com/&scioq=machine+learning&hl=en&as_sdt=0,33',
  'eprint_url': 'http://www.cs.cmu.edu/~tom/pubs/Science-ML-2015.pdf'}]
```

Notes:

- `search_pubs(...)` returns whatever the live Scholar result page exposes for each row.
- If Scholar serves the expanded abstract markup for a result row, `scholarly` returns the full abstract.
- If Scholar only serves the short snippet, `scholarly` returns the snippet.

### `fill(...)` on a publication

Use `fill(...)` when you want additional publication metadata after the initial search result.

```python
from scholarly import scholarly

pub = scholarly.search_single_pub("10.1007/s11266-018-00057-5")
filled_pub = scholarly.fill(pub)
```

Representative filled result:

```python
{'container_type': 'Publication',
 'source': <PublicationSource.PUBLICATION_SEARCH_SNIPPET: 'PUBLICATION_SEARCH_SNIPPET'>,
 'bib': {'title': 'A century of nonprofit studies: Scaling the knowledge of the field',
         'author': 'Ma, Ji and Konrath, Sara',
         'pub_year': '2018',
         'venue': 'VOLUNTAS: International Journal of Voluntary and ...',
         'abstract': 'This empirical study examines knowledge production between 1925 and 2015 in nonprofit and philanthropic studies from quantitative and thematic perspectives. Quantitative results suggest that scholars in this field have been actively generating a considerable amount of literature and a solid intellectual base for developing this field toward a new discipline. Thematic analyses suggest that knowledge production in this field is also growing in cohesion-several main themes have been formed and actively advanced since 1980s, and',
         'publisher': 'Cambridge University Press',
         'pages': '1139--1158',
         'number': '6',
         'volume': '29',
         'journal': 'VOLUNTAS: International Journal of Voluntary and Nonprofit Organizations',
         'pub_type': 'article',
         'bib_id': 'ma2018century'},
 'filled': True,
 'gsrank': 1,
 'pub_url': 'https://www.cambridge.org/core/journals/voluntas/article/century-of-nonprofit-studies-scaling-the-knowledge-of-the-field/...',
 'author_id': ['iVGd04UAAAAJ', '-bDW1IwAAAAJ'],
 'url_scholarbib': '/scholar?hl=en&q=info:veUUt9BplfoJ:scholar.google.com/&output=cite&scirp=0&hl=en',
 'num_citations': 124,
 'citedby_url': '/scholar?cites=18056454626157585853&as_sdt=2005&sciodt=0,5&hl=en'}
```

`fill(...)` is where publication objects usually gain fields such as `publisher`, `journal`, `pages`, `volume`, `number`, `pub_type`, and `bib_id`.

### `search_author_id(...)`

Anonymous Google Scholar author-name discovery is not part of the current public workflow. Start from a stable Scholar profile ID.

```python
from scholarly import scholarly

author = scholarly.search_author_id("Smr99uEAAAAJ")
```

Representative parsed result:

```python
{'container_type': 'Author',
 'filled': ['basics'],
 'scholar_id': 'Smr99uEAAAAJ',
 'source': <AuthorSource.AUTHOR_PROFILE_PAGE: 'AUTHOR_PROFILE_PAGE'>,
 'name': 'Martin Banks',
 'affiliation': 'Professor of Vision Science, UC Berkeley',
 'organization': 11816294095661060495,
 'interests': ['vision science', 'psychology', 'human factors', 'neuroscience'],
 'email_domain': '@berkeley.edu',
 'homepage': 'http://bankslab.berkeley.edu/',
 'citedby': 28208}
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

### Abstract behavior

- `search_single_pub(...)` often gets the richer best-match page for exact titles and DOIs.
- `search_pubs(...)` returns the best abstract available in each live result row.
- Full abstracts are best-effort, not guaranteed.

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
from scholarly import scholarly

pub = scholarly.search_single_pub("Creating correct blur and its effect on accommodation")
print(pub["author_id"])
# ['4bahYMkAAAAJ', '3xJXtlwAAAAJ', 'Smr99uEAAAAJ']
```

The `author_id` list is positionally aligned with the `author` list in `pub["bib"]["author"]`.

## Citations and BibTeX

Get citations for a publication:

```python
from itertools import islice
from scholarly import scholarly

pub = scholarly.search_single_pub("10.1007/s11266-018-00057-5")
first_citations = list(islice(scholarly.citedby(pub), 3))
```

Look up a cited-by cluster directly:

```python
from scholarly import scholarly

cited = scholarly.search_citedby("18056454626157585853")
```

Export BibTeX:

```python
from scholarly import scholarly

pub = scholarly.search_single_pub("10.1007/s11266-018-00057-5")
print(scholarly.bibtex(pub))
```

Representative BibTeX:

```bibtex
@article{ma2018century,
 abstract = {This empirical study examines knowledge production between 1925 and 2015 in nonprofit and philanthropic studies from quantitative and thematic perspectives. Quantitative results suggest that scholars in this field have been actively generating a considerable amount of literature and a solid intellectual base for developing this field toward a new discipline. Thematic analyses suggest that knowledge production in this field is also growing in cohesion-several main themes have been formed and actively advanced since 1980s, and},
 author = {Ma, Ji and Konrath, Sara},
 journal = {VOLUNTAS: International Journal of Voluntary and Nonprofit Organizations},
 number = {6},
 pages = {1139--1158},
 pub_year = {2018},
 publisher = {Cambridge University Press},
 title = {A century of nonprofit studies: Scaling the knowledge of the field},
 url = {https://www.cambridge.org/core/services/aop-cambridge-core/content/view/...pdf},
 venue = {VOLUNTAS: International Journal of Voluntary and ...},
 volume = {29}
}
```

## Proxies

Google Scholar rate-limits aggressively. If you make enough requests, you should expect blocking and captcha pages. Use proxies for anything non-trivial.

### Automatic `.env.socks5` loading

If a `.env.socks5` file exists in your working directory, `scholarly` loads it automatically at import time. Put one proxy per line in:

```text
USER:PASS@HOST:PORT
```

Example:

```text
user1:password1@127.0.0.1:1080
user2:password2@proxy.example.com:2080
```

See [.env.socks5.example](.env.socks5.example) for the expected format.

### Manual proxy setup

```python
from scholarly import ProxyGenerator, scholarly

pg = ProxyGenerator()
pg.FreeProxies()
scholarly.use_proxy(pg)

pub = scholarly.search_single_pub("10.1007/s11266-018-00057-5")
```

`scholarly` also supports several paid proxy services through `ProxyGenerator`.

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

- [API reference](https://scholarly.readthedocs.io/en/stable/scholarly.html)
- [Quickstart](https://scholarly.readthedocs.io/en/stable/quickstart.html)

## Disclaimer

The developers use `ScraperAPI` to run tests in GitHub Actions.
The developers of `scholarly` are not affiliated with any proxy service and do not profit from them. If your preferred service is not supported, please open an issue or submit a pull request.

## Contributing

Contributions are welcome. Please create an issue, fork the repository, and submit a pull request. See [.github/CONTRIBUTING.md](.github/CONTRIBUTING.md) for details.

## Acknowledging `scholarly`

If you use this codebase in a scientific publication, please cite:

```bibtex
@software{cholewiak2021scholarly,
  author  = {Cholewiak, Steven A. and Ipeirotis, Panos and Silva, Victor and Kannawadi, Arun},
  title   = {{SCHOLARLY: Simple access to Google Scholar authors and citation using Python}},
  year    = {2021},
  doi     = {10.5281/zenodo.5764801},
  license = {Unlicense},
  url = {https://github.com/scholarly-python-package/scholarly},
  version = {1.5.1}
}
```

## License

The original code that this project was forked from was released by [Luciano Bello](https://github.com/lbello/chalmers-web) under a [WTFPL](http://www.wtfpl.net/) license. In keeping with that spirit, all code is released under the [Unlicense](http://unlicense.org/).
