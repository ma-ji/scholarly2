import unittest
import os
import sys
from collections import Counter
import logging
import tempfile
from scholarly import scholarly, ProxyGenerator
from scholarly._navigator import Navigator
from scholarly._scholarly import _Scholarly
from scholarly.data_types import Mandate, PublicationSource
from scholarly.publication_parser import PublicationParser, _SearchScholarIterator
import random
import json
import csv
import requests
from bs4 import BeautifulSoup
from contextlib import contextmanager
from unittest import mock
try:
    import pandas as pd
except ImportError:
    pd = None

RUN_GATED_CITATIONS_TESTS = os.getenv("RUN_GATED_CITATIONS_TESTS") == "1"


class TestLuminati(unittest.TestCase):
    skipUnless = os.getenv("USERNAME") and os.getenv("PASSWORD") and os.getenv("PORT")

    @unittest.skipUnless(skipUnless, reason="No Luminati credentials found.")
    def test_luminati(self):
        """
        Test that we can set up Luminati (Bright Data) successfully
        """
        proxy_generator = ProxyGenerator()
        success = proxy_generator.Luminati(usr=os.getenv("USERNAME"),
                                           passwd=os.getenv("PASSWORD"),
                                           proxy_port=os.getenv("PORT"))
        self.assertTrue(success)
        self.assertEqual(proxy_generator.proxy_mode, "LUMINATI")


class TestScraperAPI(unittest.TestCase):
    skipUnless = os.getenv('SCRAPER_API_KEY')

    @unittest.skipUnless(skipUnless, reason="No ScraperAPI key found")
    def test_scraperapi(self):
        """
        Test that we can set up ScraperAPI successfully
        """
        proxy_generator = ProxyGenerator()
        success = proxy_generator.ScraperAPI(os.getenv('SCRAPER_API_KEY'))
        self.assertTrue(success)
        self.assertEqual(proxy_generator.proxy_mode, "SCRAPERAPI")


class TestTorInternal(unittest.TestCase):
    skipUnless = [_bin for path in sys.path if os.path.isdir(path) for _bin in os.listdir(path)
                  if _bin in ('tor', 'tor.exe')]

    @unittest.skipUnless(skipUnless, reason='Tor executable not found')
    def test_tor_launch_own_process(self):
        """
        Test that we can launch a Tor process
        """
        proxy_generator = ProxyGenerator()
        if sys.platform.startswith("linux") or sys.platform.startswith("darwin"):
            tor_cmd = 'tor'
        elif sys.platform.startswith("win"):
            tor_cmd = 'tor.exe'
        else:
            tor_cmd = None

        tor_sock_port = random.randrange(9000, 9500)
        tor_control_port = random.randrange(9500, 9999)

        result = proxy_generator.Tor_Internal(tor_cmd, tor_sock_port, tor_control_port)
        self.assertTrue(result["proxy_works"])
        self.assertTrue(result["refresh_works"])
        self.assertEqual(result["tor_control_port"], tor_control_port)
        self.assertEqual(result["tor_sock_port"], tor_sock_port)
        scholarly.use_proxy(proxy_generator)
        author = scholarly.search_author_id("PA9La6oAAAAJ")
        self.assertEqual(author["name"], "Panos Ipeirotis")


class TestSocks5ProxyConfig(unittest.TestCase):

    def test_socks5_proxy_file_is_parsed_and_rotated(self):
        with tempfile.NamedTemporaryFile("w", delete=False) as handle:
            handle.write("# ignored comment\n")
            handle.write("alice:secret@127.0.0.1:1080\n")
            handle.write("\n")
            handle.write("bob:hunter2@proxy.example.com:2080\n")
            proxy_file = handle.name

        self.addCleanup(lambda: os.path.exists(proxy_file) and os.remove(proxy_file))

        proxy_generator = ProxyGenerator()
        with mock.patch.object(proxy_generator, "_use_proxy", return_value=True) as mocked_use_proxy:
            success = proxy_generator.Socks5ProxyFile(proxy_file)

        self.assertTrue(success)
        self.assertEqual(proxy_generator.proxy_mode, "SOCKS5_PROXIES")
        mocked_use_proxy.assert_called_once_with("socks5://alice:secret@127.0.0.1:1080")
        self.assertEqual(
            proxy_generator._proxy_gen("socks5://alice:secret@127.0.0.1:1080"),
            "socks5://bob:hunter2@proxy.example.com:2080",
        )

    def test_scholarly_auto_loads_socks5_proxy_file(self):
        class FakeProxyGenerator:
            instances = []

            def __init__(self):
                self.loaded_files = []
                FakeProxyGenerator.instances.append(self)

            def Socks5ProxyFile(self, proxy_file):
                self.loaded_files.append(proxy_file)
                return True

        class FakeNavigator:
            instances = []

            def __init__(self):
                self.logger = logging.getLogger("scholarly-test")
                self.use_proxy_calls = []
                FakeNavigator.instances.append(self)

            def use_proxy(self, primary, secondary=None):
                self.use_proxy_calls.append((primary, secondary))

        proxy_file = os.path.join(tempfile.gettempdir(), ".env.socks5")

        with mock.patch("scholarly._scholarly.find_dotenv", side_effect=["", proxy_file]), \
             mock.patch("scholarly._scholarly.load_dotenv"), \
             mock.patch("scholarly._scholarly.Navigator", FakeNavigator), \
             mock.patch("scholarly._scholarly.ProxyGenerator", FakeProxyGenerator):
            _Scholarly()

        self.assertEqual(len(FakeProxyGenerator.instances), 2)
        self.assertEqual(FakeProxyGenerator.instances[0].loaded_files, [proxy_file])
        self.assertEqual(FakeProxyGenerator.instances[1].loaded_files, [proxy_file])
        self.assertEqual(len(FakeNavigator.instances), 1)
        self.assertEqual(
            FakeNavigator.instances[0].use_proxy_calls,
            [(FakeProxyGenerator.instances[0], FakeProxyGenerator.instances[1])],
        )

    def test_socks5_webdriver_proxy_config_uses_socks_capabilities(self):
        proxy_generator = ProxyGenerator()
        proxy_generator._proxy_works = True
        proxy_generator._proxies = {
            "http://": "socks5://alice:secret@127.0.0.1:1080",
            "https://": "socks5://alice:secret@127.0.0.1:1080",
        }

        proxy = proxy_generator._get_webdriver_proxy()

        self.assertEqual(proxy.socks_proxy, "127.0.0.1:1080")
        self.assertEqual(proxy.socks_version, 5)
        self.assertEqual(proxy.socks_username, "alice")
        self.assertEqual(proxy.socks_password, "secret")


class TestNavigator(unittest.TestCase):

    @staticmethod
    def _build_navigator():
        navigator = object.__new__(Navigator)
        navigator.logger = logging.getLogger("scholarly-test")
        navigator._TIMEOUT = 5
        navigator._max_retries = 1
        navigator.got_403 = False
        navigator._session1 = mock.Mock()
        navigator._session2 = mock.Mock()
        return navigator

    def test_get_soup_uses_http_client(self):
        navigator = self._build_navigator()
        with mock.patch.object(
            navigator,
            "_get_page",
            return_value="<html><body><div id='gs_res_glb' data-sva='/citations?stub=1'></div><div class='fallback'></div></body></html>",
        ) as mocked_get_page:
            soup = navigator._get_soup("/scholar?hl=en&q=test")

        mocked_get_page.assert_called_once_with("https://scholar.google.com/scholar?hl=en&q=test")
        self.assertIsNotNone(soup.find("div", class_="fallback"))
        self.assertEqual(navigator.publib, "/citations?stub=1")


class TestPublicationParser(unittest.TestCase):

    def test_search_result_prefers_expanded_abstract_markup(self):
        html = """
        <div class="gs_r gs_or gs_scl" data-cid="12345" data-rp="0">
          <div class="gs_ri">
            <h3 class="gs_rt">
              <a href="https://example.com/paper">Example paper</a>
            </h3>
            <div class="gs_a">
              <a href="/citations?user=author123&amp;hl=en">A Author</a>, B Author - Journal of Tests, 2024 - example.com
            </div>
            <div class="gs_rs gs_fma_s">Abstract Short version and ...</div>
            <div class="gs_fma gs_fma_p gs_invis">
              <div class="gs_fma_wpr">
                <div class="gs_fma_con gs_fma_sh">
                  <div class="gs_fma_abs">
                    <div class="gs_fma_snp">
                      Abstract Full abstract with the hidden expanded text included.
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="gs_fma_sml">
              <a class="gs_fma_sml_a" href="javascript:void(0)">Show more</a>
            </div>
            <div class="gs_fl">
              <a href="/scholar?cites=12345">Cited by 7</a>
              <a href="/scholar?q=related:abc123">Related articles</a>
            </div>
          </div>
        </div>
        """

        class StubNav:
            publib = "/citations?view_op=add&citation_for_view={id}"

        row = BeautifulSoup(html, "html.parser").find("div", class_="gs_r")
        parser = PublicationParser(StubNav())

        publication = parser.get_publication(row, PublicationSource.PUBLICATION_SEARCH_SNIPPET)

        self.assertEqual(
            publication["bib"]["abstract"],
            "Full abstract with the hidden expanded text included.",
        )

    def test_search_result_uses_expanded_abstract_outside_databox(self):
        html = """
        <div class="gs_r gs_or gs_scl" data-cid="12345" data-rp="0">
          <div class="gs_ri">
            <h3 class="gs_rt">
              <a href="https://example.com/paper">Example paper</a>
            </h3>
            <div class="gs_a">A Author - Journal of Tests, 2024 - example.com</div>
            <div class="gs_rs">Abstract Short version and ...</div>
            <div class="gs_fl">
              <a href="/scholar?cites=12345">Cited by 7</a>
            </div>
          </div>
          <div class="gs_fma">
            <div class="gs_fma_abs">
              <div class="gs_fma_snp">Abstract Full abstract stored outside the main result box.</div>
            </div>
          </div>
        </div>
        """

        class StubNav:
            publib = "/citations?view_op=add&citation_for_view={id}"

        row = BeautifulSoup(html, "html.parser").find("div", class_="gs_r")
        parser = PublicationParser(StubNav())

        publication = parser.get_publication(row, PublicationSource.PUBLICATION_SEARCH_SNIPPET)

        self.assertEqual(
            publication["bib"]["abstract"],
            "Full abstract stored outside the main result box.",
        )

    def test_search_iterator_retries_best_result_pages_for_expanded_abstract(self):
        short_html = """
        <html>
          <body>
            <div class="gs_ab_mdw">About 1 result</div>
            <div class="gs_r gs_or gs_scl" data-cid="12345" data-rp="0">
              <div class="gs_ri">
                <h3 class="gs_rt"><a href="https://example.com/paper">Example paper</a></h3>
                <div class="gs_a">A Author - Journal of Tests, 2024 - example.com</div>
                <div class="gs_rs">Short abstract and ...</div>
                <div class="gs_fl"><a href="/scholar?q=related:abc123">Related articles</a></div>
              </div>
            </div>
            <div>Showing the best result for this search.</div>
          </body>
        </html>
        """
        full_html = """
        <html>
          <body>
            <div class="gs_ab_mdw">About 1 result</div>
            <div class="gs_r gs_or gs_scl" data-cid="12345" data-rp="0">
              <div class="gs_ri">
                <h3 class="gs_rt"><a href="https://example.com/paper">Example paper</a></h3>
                <div class="gs_a">A Author - Journal of Tests, 2024 - example.com</div>
                <div class="gs_rs">Short abstract and ...</div>
                <div class="gs_fma_abs">
                  <div class="gs_fma_snp">Expanded abstract from show more.</div>
                </div>
                <div class="gs_fl"><a href="/scholar?q=related:abc123">Related articles</a></div>
              </div>
            </div>
            <div>Showing the best result for this search.</div>
          </body>
        </html>
        """

        class FakeNav:
            publib = "/citations?view_op=add&citation_for_view={id}"

            def __init__(self):
                self.calls = 0

            def _get_soup(self, url):
                self.calls += 1
                html = full_html if self.calls > 1 else short_html
                return BeautifulSoup(html, "html.parser")

        nav = FakeNav()
        results = _SearchScholarIterator(nav, "/scholar?hl=en&q=10.1000%2Ftest")
        publication = next(results)

        self.assertEqual(nav.calls, 2)
        self.assertEqual(publication["bib"]["abstract"], "Expanded abstract from show more.")

    def test_search_iterator_accepts_extra_result_row_classes_for_expanded_abstract(self):
        short_html = """
        <html>
          <body>
            <div class="gs_ab_mdw">About 1 result</div>
            <div class="gs_r gs_or gs_scl" data-cid="12345" data-rp="0">
              <div class="gs_ri">
                <h3 class="gs_rt"><a href="https://example.com/paper">Example paper</a></h3>
                <div class="gs_a">A Author - Journal of Tests, 2024 - example.com</div>
                <div class="gs_rs">Short abstract and ...</div>
                <div class="gs_fl"><a href="/scholar?q=related:abc123">Related articles</a></div>
              </div>
            </div>
            <div>Showing the best result for this search.</div>
          </body>
        </html>
        """
        full_html = """
        <html>
          <body>
            <div class="gs_ab_mdw">About 1 result</div>
            <div class="gs_r gs_or gs_scl gs_fmar" data-cid="12345" data-rp="0">
              <div class="gs_ri">
                <h3 class="gs_rt"><a href="https://example.com/paper">Example paper</a></h3>
                <div class="gs_a">A Author - Journal of Tests, 2024 - example.com</div>
                <div class="gs_rs">Short abstract and ...</div>
                <div class="gs_fma_abs">
                  <div class="gs_fma_snp">Expanded abstract from a richer Scholar row.</div>
                </div>
                <div class="gs_fl"><a href="/scholar?q=related:abc123">Related articles</a></div>
              </div>
            </div>
            <div>Showing the best result for this search.</div>
          </body>
        </html>
        """

        class FakeNav:
            publib = "/citations?view_op=add&citation_for_view={id}"

            def __init__(self):
                self.calls = 0

            def _get_soup(self, url):
                self.calls += 1
                html = full_html if self.calls > 1 else short_html
                return BeautifulSoup(html, "html.parser")

        nav = FakeNav()
        results = _SearchScholarIterator(nav, "/scholar?hl=en&q=10.1000%2Ftest")
        publication = next(results)

        self.assertEqual(nav.calls, 2)
        self.assertEqual(publication["bib"]["abstract"], "Expanded abstract from a richer Scholar row.")

    def test_search_iterator_retries_empty_search_pages(self):
        empty_html = "<html><body><div class=\"gs_ab_mdw\">About 1 result</div></body></html>"
        result_html = """
        <html>
          <body>
            <div class="gs_ab_mdw">About 1 result</div>
            <div class="gs_r gs_or gs_scl" data-cid="12345" data-rp="0">
              <div class="gs_ri">
                <h3 class="gs_rt"><a href="https://example.com/paper">Example paper</a></h3>
                <div class="gs_a">A Author - Journal of Tests, 2024 - example.com</div>
                <div class="gs_rs">Abstract present after retry.</div>
                <div class="gs_fl"><a href="/scholar?q=related:abc123">Related articles</a></div>
              </div>
            </div>
          </body>
        </html>
        """

        class FakeNav:
            publib = "/citations?view_op=add&citation_for_view={id}"

            def __init__(self):
                self.calls = 0

            def _get_soup(self, url):
                self.calls += 1
                html = result_html if self.calls > 1 else empty_html
                return BeautifulSoup(html, "html.parser")

        nav = FakeNav()
        results = _SearchScholarIterator(nav, "/scholar?hl=en&q=10.1000%2Ftest")
        publication = next(results)

        self.assertEqual(nav.calls, 2)
        self.assertEqual(publication["bib"]["title"], "Example paper")


class TestScholarly(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        scholarly.set_timeout(5)
        scholarly.set_retries(5)

        pg = ProxyGenerator()
        pg.FreeProxies()
        scholarly.use_proxy(pg, ProxyGenerator())

        # Try storing the file temporarily as `scholarly.csv` and delete it.
        # If there exists already a file with that name, generate a random name
        # that does not exist yet, so we can safely delete it.
        cls.mandates_filename = "scholarly.csv"
        while os.path.exists(cls.mandates_filename):
            cls.mandates_filename = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=10)) + ".csv"

    @classmethod
    def tearDownClass(cls):
        """
        Clean up the mandates csv fiile downloaded.
        """
        if os.path.exists(cls.mandates_filename):
            os.remove(cls.mandates_filename)

    @staticmethod
    @contextmanager
    def suppress_stdout():
        with open(os.devnull, "w") as devnull:
            old_stdout = sys.stdout
            sys.stdout = devnull
            try:
                yield
            finally:
                sys.stdout = old_stdout

    @unittest.skipUnless(RUN_GATED_CITATIONS_TESTS, reason="Google may gate Citations author-discovery endpoints behind sign-in.")
    def test_search_keywords(self):
        query = scholarly.search_keywords(['crowdsourcing', 'privacy'])
        author = next(query)
        self.assertEqual(author['scholar_id'], '_cMw1IUAAAAJ')
        self.assertEqual(author['name'], 'Arpita Ghosh')
        self.assertEqual(author['affiliation'], 'Cornell University')

    @unittest.skipUnless(RUN_GATED_CITATIONS_TESTS, reason="Google may gate Citations author-discovery endpoints behind sign-in.")
    def test_search_keyword_empty_keyword(self):
        """
        As of 2020-04-30, there are  6 individuals that match the name 'label'
        """
        # TODO this seems like undesirable functionality for
        # scholarly.search_keyword() with empty string. Surely, no authors
        # should be returned. Consider modifying the method itself.
        authors = [a for a in scholarly.search_keyword('')]
        self.assertGreaterEqual(len(authors), 6)

    @unittest.skipUnless(RUN_GATED_CITATIONS_TESTS, reason="Google may gate Citations author-discovery endpoints behind sign-in.")
    def test_search_keyword(self):
        """
        Test that we can search based on specific keywords

        When we search for the keyword "3d shape" the author
        Steven A. Cholewiak should be among those listed.
        When we search for the keyword "Haptics", Oussama Khatib
        should be listed first.
        """
        # Example 1
        authors = [a['name'] for a in scholarly.search_keyword('3d shape')]
        self.assertIsNot(len(authors), 0)
        self.assertIn(u'Steven A. Cholewiak, PhD', authors)

        # Example 2
        expected_author = {'affiliation': 'Stanford University',
                           'citedby': 43856,
                           'email_domain': '@cs.stanford.edu',
                           'filled': [],
                           'interests': ['Robotics',
                                         'Haptics',
                                         'Human Motion Understanding'],
                           'name': 'Oussama Khatib',
                           'scholar_id': '4arkOLcAAAAJ',
                           'source': 'SEARCH_AUTHOR_SNIPPETS',
                           'url_picture': 'https://scholar.google.com/citations?view_op=medium_photo&user=4arkOLcAAAAJ'
                           }
        search_query = scholarly.search_keyword('Haptics')
        author = next(search_query)
        for key in author:
            if (key not in {"citedby", "container_type", "interests"}) and (key in expected_author):
                self.assertEqual(author[key], expected_author[key])
        self.assertEqual(set(author["interests"]), set(expected_author["interests"]))

        # Example 3
        expected_author = {'affiliation': "CEA, Département d'Astrophysique",
                           'citedby': 98936,
                           'email_domain': '@cea.fr',
                           'filled': [],
                           'interests': ['Cosmology (CMB',
                                         'weak-lensing',
                                         'large scale structure)',
                                         'Statistics',
                                         'Image Processing'],
                           'name': 'Jean-Luc Starck',
                           'scholar_id': 'IAaAiXgAAAAJ',
                           'source': 'SEARCH_AUTHOR_SNIPPETS',
                           'url_picture': 'https://scholar.google.com/citations?view_op=medium_photo&user=IAaAiXgAAAAJ'
                           }
        search_query = scholarly.search_keyword('large-scale structure')
        author = next(search_query)
        for key in author:
            if (key not in {"citedby", "container_type", "interests"}) and (key in expected_author):
                self.assertEqual(author[key], expected_author[key])
        scholarly.pprint(author)
        self.assertEqual(set(author["interests"]), set(expected_author["interests"]))

    def test_search_author_id(self):
        """
        Test the search by author ID. Marie Skłodowska-Curie's ID is
        EmD_lTEAAAAJ and these IDs are permenant
        """
        author = scholarly.search_author_id('EmD_lTEAAAAJ')
        self.assertEqual(author['name'], u'Marie Skłodowska-Curie')
        self.assertEqual(author['affiliation'],
                         u'Institut du radium, University of Paris')

    def test_search_author_id_filled(self):
        """
        Test the search by author ID. Marie Skłodowska-Curie's ID is
        EmD_lTEAAAAJ and these IDs are permenant.
        As of July 2020, Marie Skłodowska-Curie has 1963 citations
        on Google Scholar and 179 publications
        """
        author = scholarly.search_author_id('EmD_lTEAAAAJ', filled=True)
        self.assertEqual(author['name'], u'Marie Skłodowska-Curie')
        self.assertEqual(author['affiliation'],
                         u'Institut du radium, University of Paris')
        self.assertEqual(author['interests'], [])
        self.assertEqual(author['public_access']['available'], 0)
        self.assertEqual(author['public_access']['not_available'], 0)
        self.assertGreaterEqual(author['citedby'], 2090)
        self.assertGreaterEqual(len(author['publications']), 218)
        cpy = {1986:4, 2011: 137, 2018: 100}
        for year, count in cpy.items():
            self.assertEqual(author["cites_per_year"][year], count)
        pub = author['publications'][1]
        self.assertEqual(pub["citedby_url"],
                         "https://scholar.google.com/scholar?oi=bibs&hl=en&cites=9976400141451962702")


    def test_extract_author_id_list(self):
        '''
        This unit test tests the extraction of the author id field from the html to populate the `author_id` field
        in the Publication object.
        '''
        author_html_full = '<a href="/citations?user=4bahYMkAAAAJ&amp;hl=en&amp;oi=sra">SA Cholewiak</a>, <a href="/citations?user=3xJXtlwAAAAJ&amp;hl=en&amp;oi=sra">GD Love</a>, <a href="/citations?user=Smr99uEAAAAJ&amp;hl=en&amp;oi=sra">MS Banks</a> - Journal of vision, 2018 - jov.arvojournals.org'
        pub_parser = PublicationParser(None)
        author_id_list = pub_parser._get_author_id_list(author_html_full)
        self.assertTrue(author_id_list[0] == '4bahYMkAAAAJ')
        self.assertTrue(author_id_list[1] == '3xJXtlwAAAAJ')
        self.assertTrue(author_id_list[2] == 'Smr99uEAAAAJ')

        author_html_partial = "A Bateman, J O'Connell, N Lorenzini, <a href=\"/citations?user=TEndP-sAAAAJ&amp;hl=en&amp;oi=sra\">T Gardner</a>…&nbsp;- BMC psychiatry, 2016 - Springer"
        pub_parser = PublicationParser(None)
        author_id_list = pub_parser._get_author_id_list(author_html_partial)
        self.assertTrue(author_id_list[3] == 'TEndP-sAAAAJ')

    def test_serialiazation(self):
        """
        Test that we can serialize the Author and Publication types

        Note: JSON converts integer keys to strings, resulting in the years
        in `cites_per_year` dictionary as `str` type instead of `int`.
        To ensure consistency with the typing, use `object_hook` option
        when loading to convert the keys to integers.
        """
        # Test that a filled Author with unfilled Publication
        # is serializable.
        def cpy_decoder(di):
            """A utility function to convert the keys in `cites_per_year` to `int` type.

              This ensures consistency with `CitesPerYear` typing.
            """
            if "cites_per_year" in di:
                di["cites_per_year"] = {int(k): v for k,v in di["cites_per_year"].items()}
            return di

        author = scholarly.search_author_id('EmD_lTEAAAAJ', filled=True)
        serialized = json.dumps(author)
        author_loaded = json.loads(serialized, object_hook=cpy_decoder)
        self.assertEqual(author, author_loaded)
        # Test that a loaded publication is still fillable and serializable.
        pub = author_loaded['publications'][0]
        scholarly.fill(pub)
        serialized = json.dumps(pub)
        pub_loaded = json.loads(serialized, object_hook=cpy_decoder)
        self.assertEqual(pub, pub_loaded)

    def test_full_title(self):
        """
        Test if the full title of a long title-publication gets retrieved.
        The code under test gets executed if:
        publication['source'] == PublicationSource.AUTHOR_PUBLICATION_ENTRY
        so the long title-publication is taken from an author object.
        """
        author = scholarly.search_author_id('Xxjj6IsAAAAJ')
        author = scholarly.fill(author, sections=['publications'])
        pub_index = -1
        # Skip this part of the test since u_35RYKgDlwC has vanished from Google Scholar
        if False:
            for i in range(len(author['publications'])):
                if author['publications'][i]['author_pub_id'] == 'Xxjj6IsAAAAJ:u_35RYKgDlwC':
                    pub_index = i
            self.assertGreaterEqual(i, 0)
            # elided title
            self.assertEqual(author['publications'][pub_index]['bib']['title'],
                             u'Evaluation of toxicity of Dichlorvos (Nuvan) to fresh water fish Anabas testudineus and possible modulation by crude aqueous extract of Andrographis paniculata: A preliminary …')
            # full text
            pub = scholarly.fill(author['publications'][pub_index])
            self.assertEqual(pub['bib']['title'],
                             u'Evaluation of toxicity of Dichlorvos (Nuvan) to fresh water fish Anabas testudineus and possible modulation by crude aqueous extract of Andrographis paniculata: A preliminary investigation')

            self.assertEqual(pub['bib']['citation'], "")

        for i in range(len(author['publications'])):
            if author['publications'][i]['author_pub_id'] == 'Xxjj6IsAAAAJ:ldfaerwXgEUC':
                pub_index = i
        self.assertGreaterEqual(i, 0)
        # elided title
        self.assertEqual(author['publications'][pub_index]['bib']['title'],
                         u'Evaluation of toxicity of Dichlorvos (Nuvan) to fresh water fish Anabas testudineus and possible modulation by crude aqueous extract of Andrographis paniculata: A preliminary …')
        # full text
        pub = scholarly.fill(author['publications'][pub_index])
        self.assertEqual(pub['bib']['title'],
                         u'Evaluation of toxicity of Dichlorvos (Nuvan) to fresh water fish Anabas testudineus and possible modulation by crude aqueous extract of Andrographis paniculata: A preliminary …')

        self.assertEqual(pub['bib']['citation'], "Journal of Fisheries and Life Sciences 5 (2), 74-84, 2020")

    @unittest.skipUnless(RUN_GATED_CITATIONS_TESTS, reason="Google may gate Citations author-discovery endpoints behind sign-in.")
    def test_author_organization(self):
        """
        """
        organization_id = 4836318610601440500  # Princeton University
        organizations = scholarly.search_org("Princeton University")
        self.assertEqual(len(organizations), 1)
        organization = organizations[0]
        self.assertEqual(organization['Organization'], "Princeton University")
        self.assertEqual(organization['id'], str(organization_id))

        search_query = scholarly.search_author_by_organization(organization_id)
        author = next(search_query)
        self.assertEqual(author['scholar_id'], "ImhakoAAAAAJ")
        self.assertEqual(author['name'], "Daniel Kahneman")
        self.assertEqual(author['email_domain'], "@princeton.edu")
        self.assertEqual(author['affiliation'], "Princeton University (Emeritus)")
        self.assertGreaterEqual(author['citedby'], 438891)

    def test_coauthors(self):
        """
        Test that we can fetch long (20+) and short list of coauthors
        """
        author = scholarly.search_author_id('7Jl3PIoAAAAJ')
        scholarly.fill(author, sections=['basics', 'coauthors'])
        self.assertEqual(author['name'], "Victor Silva")
        self.assertLessEqual(len(author['coauthors']), 20)
        # If the above assertion fails, pick a different author profile
        self.assertGreaterEqual(len(author['coauthors']), 6)
        self.assertIn('Eleni Stroulia', [_coauth['name'] for _coauth in author['coauthors']])
        self.assertIn('TyM1dLwAAAAJ', [_coauth['scholar_id'] for _coauth in author['coauthors']])
        # Fill co-authors
        for _coauth in author['coauthors']:
            scholarly.fill(_coauth, sections=['basics'])
        self.assertIn(16627554827500071773, [_coauth.get('organization', None) for _coauth in author['coauthors']])

        author = scholarly.search_author_id('PA9La6oAAAAJ')
        scholarly.fill(author, sections=['basics', 'coauthors'])
        self.assertEqual(author['name'], "Panos Ipeirotis")
        self.assertGreaterEqual(len(author['coauthors']), 66)
        # Break the build if the long list cannot be fetched.
        self.assertIn('Eduardo Ruiz', [_coauth['name'] for _coauth in author['coauthors']])
        self.assertIn('hWq7jFQAAAAJ', [_coauth['scholar_id'] for _coauth in author['coauthors']])

    def test_public_access(self):
        """
        Test that we obtain public access information

        We check two cases: 1) when number of public access mandates exceeds
        100, thus requiring fetching information from a second page and 2) fill
        public access counts without fetching publications.
        """
        author = scholarly.search_author_id("f4KlrXIAAAAJ")
        scholarly.fill(author, sections=['basics', 'public_access', 'publications'])
        self.assertGreaterEqual(author["public_access"]["available"], 1150)
        self.assertEqual(author["public_access"]["available"],
                         sum(pub.get("public_access", None) is True for pub in author["publications"]))
        self.assertEqual(author["public_access"]["not_available"],
                         sum(pub.get("public_access", None) is False for pub in author["publications"]))

        author = scholarly.search_author_id("ImhakoAAAAAJ")
        scholarly.fill(author, sections=["public_access"])
        self.assertGreaterEqual(author["public_access"]["available"], 5)

    def test_mandates(self):
        """
        Test that we can fetch the funding information of a paper from an author
        """
        author = scholarly.search_author_id("kUDCLXAAAAAJ")
        scholarly.fill(author, sections=['public_access', 'publications'])
        for pub in author['publications']:
            if pub['author_pub_id'] == "kUDCLXAAAAAJ:tzM49s52ZIMC":
                scholarly.fill(pub)
                break
        # The hard-coded reference mandate may need regular updates.
        mandate = Mandate(agency="European Commission", effective_date="2013/12", embargo="6 months", grant="647112",
                          url_policy="https://erc.europa.eu/sites/default/files/document/file/ERC%20Open%20Access%20guidelines-Version%201.1._10.04.2017.pdf",
                          url_policy_cached="/mandates/horizon2020_eu-2021-02-13-en.pdf",
        )
        self.assertIn(mandate, pub['mandates'])

    @unittest.skipUnless(RUN_GATED_CITATIONS_TESTS, reason="Google may gate Citations author-discovery endpoints behind sign-in.")
    def test_author_custom_url(self):
        """
        Test that we can use custom URLs for retrieving author data
        """
        query_url = "/citations?hl=en&view_op=search_authors&mauthors=label%3A3d_shape"
        authors = scholarly.search_author_custom_url(query_url)
        self.assertIn(u'Steven A. Cholewiak, PhD', [author['name'] for author in authors])

    @unittest.skipIf(sys.platform.startswith("win"), reason="File read is empty in Windows")
    def test_download_mandates_csv(self):
        """
        Test that we can download the mandates CSV and read it.
        """
        if not os.path.exists(self.mandates_filename):
            text = scholarly.download_mandates_csv(self.mandates_filename)
            self.assertGreater(len(text), 0)
        funder, policy, percentage2020, percentageOverall = [], [], [], []
        with open(self.mandates_filename, "r") as f:
            csv_reader = csv.DictReader(f)
            for row in csv_reader:
                funder.append(row['\ufeffFunder'])
                policy.append(row['Policy'])
                percentage2020.append(row['2020'])
                percentageOverall.append(row['Overall'])

        agency_policy = {
            "US National Science Foundation": "https://www.nsf.gov/pubs/2015/nsf15052/nsf15052.pdf",
            "Department of Science & Technology, India": "http://www.dst.gov.in/sites/default/files/APPROVED%20OPEN%20ACCESS%20POLICY-DBT%26DST%2812.12.2014%29_1.pdf",
            "Swedish Research Council": "https://www.vr.se/english/applying-for-funding/requirements-terms-and-conditions/publishing-open-access.html",
            "Swedish Research Council for Environment, Agricultural Sciences and Spatial Planning": ""
        }
        agency_2020 = {
            "US National Science Foundation": "87%",
            "Department of Science & Technology, India": "49%",
            "Swedish Research Council": "89%",
            "Swedish Research Council for Environment, Agricultural Sciences and Spatial Planning": "88%"
        }

        response = requests.get("https://scholar.google.com/citations?view_op=mandates_leaderboard&hl=en")
        soup = BeautifulSoup(response.text, "html.parser")
        agency_overall = soup.find_all("td", class_="gsc_mlt_n gsc_mlt_bd")

        # These hardcoded numbers need some regular updates.
        for agency, index in zip(agency_policy, [5-1,9-1, 21-1, 63-1]):
            agency_index = funder.index(agency)
            self.assertEqual(policy[agency_index], agency_policy[agency])
            # Check that the percentage values from CSV and on the page agree.
            self.assertEqual(percentageOverall[agency_index], agency_overall[index].text)
            # The percentage fluctuates, so we can't check the exact value.
            self.assertAlmostEqual(int(percentage2020[agency_index][:-1]), int(agency_2020[agency][:-1]), delta=2)

    @unittest.skipIf(sys.platform.startswith("win"), reason="File read is empty in Windows")
    @unittest.skipIf(pd is None, reason="pandas is not installed")
    def test_download_mandates_csv_with_pandas(self):
        """
        Test that we can use pandas to read the CSV file
        """
        if not os.path.exists(self.mandates_filename):
            text = scholarly.download_mandates_csv(self.mandates_filename)
            self.assertGreater(len(text), 0)
        df = pd.read_csv(self.mandates_filename, usecols=["Funder", "Policy", "2020", "Overall"]).fillna("")
        self.assertGreater(len(df), 0)

        funders = ["US National Science Foundation",
                   "Department of Science & Technology, India",
                   "Swedish Research Council",
                   "Swedish Research Council for Environment, Agricultural Sciences and Spatial Planning"
                   ]

        policies = ["https://www.nsf.gov/pubs/2015/nsf15052/nsf15052.pdf",
                    "http://www.dst.gov.in/sites/default/files/APPROVED%20OPEN%20ACCESS%20POLICY-DBT%26DST%2812.12.2014%29_1.pdf",
                    "https://www.vr.se/english/applying-for-funding/requirements-terms-and-conditions/publishing-open-access.html",
                    ""
                    ]
        percentage_overall = [84, 54, 83, 83]
        percentage_2020 = [87, 49, 89, 88]

        rows = df["Funder"].isin(funders)
        self.assertEqual(rows.sum(), 4)
        self.assertEqual(df["Policy"][rows].tolist(), policies)
        df_overall = df["Overall"][rows].tolist()
        df_2020 = df["2020"][rows].tolist()
        for idx in range(4):
            self.assertAlmostEqual(int(df_overall[idx][:-1]), percentage_overall[idx], delta=2)
            self.assertAlmostEqual(int(df_2020[idx][:-1]), percentage_2020[idx], delta=2)

    def test_save_journal_leaderboard(self):
        """
        Test that we can save the journal leaderboard to a file
        """
        filename = "journals.csv"
        while os.path.exists(filename):
            filename = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=10)) + ".csv"

        try:
            scholarly.save_journals_csv(category="Physics & Mathematics", subcategory="Astronomy & Astrophysics",
                                        filename=filename, include_comments=True)
            with open(filename, "r") as f:
                csv_reader = csv.DictReader(f)
                for row in csv_reader:
                    # These hard-coded values need regular updates.
                    self.assertEqual(row['Publication'], 'The Astrophysical Journal')
                    self.assertEqual(row['h5-index'], '167')
                    self.assertEqual(row['h5-median'], '234')
                    self.assertEqual(row['Comment'], '#1 Astronomy & Astrophysics; #2 Physics & Mathematics; ')
                    break
        finally:
            if os.path.exists(filename):
                os.remove(filename)

    def test_bin_citations_by_year(self):
        """Test an internal optimization function to bin cites_per_year
           while keeping the citation counts less than 1000 per bin.
        """
        cpy = {2022: 490, 2021: 340, 2020:327, 2019:298, 2018: 115, 2017: 49, 2016: 20, 2015: 8, 2014: 3, 2013: 1, 2012: 1}
        years = scholarly._bin_citations_by_year(cpy, 2022)
        for y_hi, y_lo in years:
            self.assertLessEqual(y_lo, y_hi)
            self.assertLessEqual(sum(cpy[y] for y in range(y_lo, y_hi+1)), 1000)

    def test_cites_per_year(self):
        """Test that the cites_per_year is correctly filled in,
           including any gap years.
        """
        author = scholarly.search_author_id('DW_bVcEAAAAJ')
        scholarly.fill(author, sections=['counts'])
        cpy = {2014: 1, 2015: 2, 2016: 2, 2017: 0, 2018: 2, 2019: 1, 2020: 12, 2021: 21, 2022: 35}
        for year, count in cpy.items():
            self.assertEqual(author['cites_per_year'][year], count)

    def test_redirect(self):
        """Test that we can handle redirects when the scholar_id is approximate.
        """
        author = scholarly.search_author_id("oMaIg8sAAAAJ")
        self.assertEqual(author["scholar_id"], "PEJ42J0AAAAJ")
        scholarly.fill(author, sections=["basics"])
        self.assertEqual(author["name"], "Kiran Bhatia")
        self.assertGreaterEqual(author["citedby"], 135)

class TestScholarlyWithProxy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Setup the proxy methods for unit tests
        """
        scholarly.set_timeout(5)
        scholarly.set_retries(5)

        if "CONNECTION_METHOD" in scholarly.env:
            cls.connection_method = os.getenv("CONNECTION_METHOD")
        else:
            cls.connection_method = "none"
            scholarly.use_proxy(None)
            return

        # Use dual proxies for unit testing
        secondary_proxy_generator = ProxyGenerator()
        secondary_proxy_generator.FreeProxies()

        proxy_generator = ProxyGenerator()
        if cls.connection_method == "tor":
            tor_password = "scholarly_password"
            # Tor uses the 9050 port as the default socks port
            # on windows 9150 for socks and 9151 for control
            if sys.platform.startswith("linux") or sys.platform.startswith("darwin"):
                tor_sock_port = 9050
                tor_control_port = 9051
            elif sys.platform.startswith("win"):
                tor_sock_port = 9150
                tor_control_port = 9151
            else:
                tor_sock_port = None
                tor_control_port = None
            proxy_generator.Tor_External(tor_sock_port, tor_control_port,
                                         tor_password)

        elif cls.connection_method == "tor_internal":
            if sys.platform.startswith("linux") or sys.platform.startswith("darwin"):
                tor_cmd = 'tor'
            elif sys.platform.startswith("win"):
                tor_cmd = 'tor.exe'
            else:
                tor_cmd = None
            proxy_generator.Tor_Internal(tor_cmd = tor_cmd)

        elif cls.connection_method == "luminati":
            scholarly.set_retries(10)
            proxy_generator.Luminati(usr=os.getenv("USERNAME"),
                                     passwd=os.getenv("PASSWORD"),
                                     proxy_port=os.getenv("PORT"))

        elif cls.connection_method == "freeproxy":
            # Use different instances for primary and secondary
            proxy_generator = ProxyGenerator()
            proxy_generator.FreeProxies()

        elif cls.connection_method == "scraperapi":
            proxy_generator.ScraperAPI(os.getenv('SCRAPER_API_KEY'))

        else:
            scholarly.use_proxy(None)

        scholarly.use_proxy(proxy_generator, secondary_proxy_generator)

    def test_search_pubs_empty_publication(self):
        """
        Test that searching for an empty publication returns zero results
        """
        pubs = [p for p in scholarly.search_pubs('')]
        self.assertIs(len(pubs), 0)

    def test_search_pubs_citedby(self):
        """
        Testing that when we retrieve the list of publications that cite
        a publication, the number of citing publication is the same as
        the number of papers that are returned. We use a publication
        with a small number of citations, so that the test runs quickly.
        The 'Machine-learned epidemiology' paper had 11 citations as of
        June 1, 2020.
        """
        query = 'Machine-learned epidemiology: real-time detection of foodborne illness at scale'
        pubs = [p for p in scholarly.search_pubs(query)]
        self.assertGreaterEqual(len(pubs), 1)
        filled = scholarly.fill(pubs[0])
        cites = [c for c in scholarly.citedby(filled)]
        self.assertEqual(len(cites), filled['num_citations'])

    def test_search_pubs_citedby_id(self):
        """
        Test querying for citations by paper ID.

        The 'Machine-learned epidemiology' paper had 11 citations as of
        June 1, 2020.
        """
        # Machine-learned epidemiology: real-time detection of foodborne illness at scale
        publication_id = 2244396665447968936

        pubs = [p for p in scholarly.search_citedby(publication_id)]
        self.assertGreaterEqual(len(pubs), 11)

    def test_bibtex(self):
        """
        Test that we get the BiBTeX entry correctly
        """

        with open("testdata/bibtex.txt", "r") as f:
            expected_result = "".join(f.readlines())

        pub = scholarly.search_single_pub("A distribution-based clustering algorithm for mining in large "
                                          "spatial databases", filled=True)
        result = scholarly.bibtex(pub)
        self.assertEqual(result, expected_result)

    def test_search_pubs(self):
        """
        As of May 12, 2020 there are at least 29 pubs that fit the search term:
        ["naive physics" stability "3d shape"].

        Check that the paper "Visual perception of the physical stability of asymmetric three-dimensional objects"
        is among them
        """
        pub = scholarly.search_single_pub("naive physics stability 3d shape")
        pubs = list(scholarly.search_pubs('"naive physics" stability "3d shape"'))
        # Check that the first entry in pubs is the same as pub.
        # Checking for quality holds for non-dict entries only.
        for key in {'author_id', 'pub_url', 'num_citations'}:
            self.assertEqual(pub[key], pubs[0][key])
        for key in {'title', 'pub_year', 'venue'}:
            self.assertEqual(pub['bib'][key], pubs[0]['bib'][key])
        self.assertGreaterEqual(len(pubs), 27)
        titles = [p['bib']['title'] for p in pubs]
        self.assertIn('Visual perception of the physical stability of asymmetric three-dimensional objects', titles)

    def test_search_pubs_total_results(self):
        """
        As of September 16, 2021 there are 32 pubs that fit the search term:
        ["naive physics" stability "3d shape"], and 17'000 results that fit
        the search term ["WIEN2k Blaha"] and none for ["sdfsdf+24r+asdfasdf"].

        Check that the total results for that search term equals 32.
        """
        pubs = scholarly.search_pubs('"naive physics" stability "3d shape"')
        self.assertGreaterEqual(pubs.total_results, 32)

        pubs = scholarly.search_pubs('WIEN2k Blaha')
        self.assertGreaterEqual(pubs.total_results, 10000)

        pubs = scholarly.search_pubs('sdfsdf+24r+asdfasdf')
        self.assertEqual(pubs.total_results, 0)

    def test_search_pubs_filling_publication_contents(self):
        '''
        This process  checks the process of filling a publication that is derived
         from the search publication snippets.
        '''
        query = 'Creating correct blur and its effect on accommodation'
        results = scholarly.search_pubs(query)
        pubs = [p for p in results]
        self.assertGreaterEqual(len(pubs), 1)
        f = scholarly.fill(pubs[0])
        self.assertTrue(f['bib']['author'] == u'Cholewiak, Steven A and Love, Gordon D and Banks, Martin S')
        self.assertTrue(f['author_id'] == ['4bahYMkAAAAJ', '3xJXtlwAAAAJ', 'Smr99uEAAAAJ'])
        self.assertTrue(f['bib']['journal'] == u'Journal of Vision')
        self.assertTrue(f['bib']['number'] == '9')
        self.assertTrue(f['bib']['pages'] == u'1--1')
        self.assertTrue(f['bib']['publisher'] == u'The Association for Research in Vision and Ophthalmology')
        self.assertTrue(f['bib']['title'] == u'Creating correct blur and its effect on accommodation')
        self.assertTrue(f['pub_url'] == u'https://jov.arvojournals.org/article.aspx?articleid=2701817')
        self.assertTrue(f['bib']['volume'] == '18')
        self.assertTrue(f['bib']['pub_year'] == u'2018')

    def test_related_articles_from_author(self):
        """
        Test that we obtain related articles to an article from an author
        """
        author = scholarly.search_author_id("ImhakoAAAAAJ")
        scholarly.fill(author, sections=['basics', 'publications'])
        pub = author['publications'][0]
        self.assertEqual(pub['bib']['title'], 'Prospect theory: An analysis of decision under risk')
        self.assertEqual(pub['bib']['citation'], 'Handbook of the fundamentals of financial decision making: Part I, 99-127, 2013')
        related_articles = scholarly.get_related_articles(pub)
        # Typically, the same publication is returned as the most related article
        same_article = next(related_articles)
        self.assertEqual(pub["pub_url"], same_article["pub_url"])
        for key in {'title', 'pub_year'}:
            self.assertEqual(str(pub['bib'][key]), (same_article['bib'][key]))

        # These may change with time
        related_article = next(related_articles)
        self.assertEqual(related_article['bib']['title'], 'Advances in prospect theory: Cumulative representation of uncertainty')
        self.assertEqual(related_article['bib']['pub_year'], '1992')
        self.assertGreaterEqual(related_article['num_citations'], 18673)
        self.assertIn("A Tversky", related_article['bib']['author'])

    def test_related_articles_from_publication(self):
        """
        Test that we obtain related articles to an article from a search
        """
        pub = scholarly.search_single_pub("Planck 2018 results-VI. Cosmological parameters")
        related_articles = scholarly.get_related_articles(pub)
        # Typically, the same publication is returned as the most related article
        same_article = next(related_articles)
        for key in {'author_id', 'pub_url', 'num_citations'}:
            self.assertEqual(pub[key], same_article[key])
        for key in {'title', 'pub_year'}:
            self.assertEqual(pub['bib'][key], same_article['bib'][key])

        # These may change with time
        related_article = next(related_articles)
        self.assertEqual(related_article['bib']['title'], 'Large Magellanic Cloud Cepheid standards provide '
                         'a 1% foundation for the determination of the Hubble constant and stronger evidence '
                         'for physics beyond ΛCDM')
        self.assertEqual(related_article['bib']['pub_year'], '2019')
        self.assertGreaterEqual(related_article['num_citations'], 1388)
        self.assertIn("AG Riess", related_article['bib']['author'])

    def test_pubs_custom_url(self):
        """
        Test that we can use custom URLs for retrieving publication data
        """
        query_url = ('/scholar?as_q=&as_epq=&as_oq=SFDI+"modulated+imaging"&as_eq=&as_occt=any&as_sauthors=&'
                     'as_publication=&as_ylo=2005&as_yhi=2020&hl=en&as_sdt=0%2C31')
        pubs = scholarly.search_pubs_custom_url(query_url)
        pub = next(pubs)
        self.assertEqual(pub['bib']['title'], 'Quantitation and mapping of tissue optical properties using modulated imaging')
        self.assertEqual(set(pub['author_id']), {'V-ab9U4AAAAJ', '4k-k6SEAAAAJ', 'GLm-SaQAAAAJ'})
        self.assertEqual(pub['bib']['pub_year'], '2009')
        self.assertGreaterEqual(pub['num_citations'], 581)

    def check_citedby_1k(self, pub):
        """A common checking method to check
        """
        original_citation_count = pub["num_citations"]
        # Trigger a different code path
        if original_citation_count <= 1000:
            pub["num_citations"] = 1001
        citations = scholarly.citedby(pub)
        citation_list = list(citations)
        self.assertEqual(len(citation_list), original_citation_count)
        return citation_list

    def test_citedby_1k_citations(self):
        """Test that scholarly can fetch 1000+ citations from an author
        """
        author = scholarly.search_author_id('QoX9bu8AAAAJ')
        scholarly.fill(author, sections=['publications'])
        pub = [_p for _p in  author['publications'] if _p["author_pub_id"]=="QoX9bu8AAAAJ:L8Ckcad2t8MC"][0]
        scholarly.fill(pub)
        citation_list = self.check_citedby_1k(pub)

        yearwise_counter = Counter([c["bib"]["pub_year"] for c in citation_list])
        for year, count in pub["cites_per_year"].items():
            self.assertEqual(yearwise_counter.get(str(year), 0), count)

    def test_citedby_1k_scholar(self):
        """Test that scholarly can fetch 1000+ citations from a pub search.
        """
        title = "Persistent entanglement in a class of eigenstates of quantum Heisenberg spin glasses"
        pubs = scholarly.search_pubs(title)
        pub = next(pubs)
        self.check_citedby_1k(pub)

    def test_citedby(self):
        """Test that we can search citations of a paper from author's profile.
        """
        # Retrieve the author's data, fill-in, and print
        author = scholarly.search_author_id('4bahYMkAAAAJ')
        scholarly.fill(author, sections=['publications'])
        pub = scholarly.fill(author['publications'][0])

        # Which papers cited that publication?
        top10_citations = [citation for num, citation in enumerate(scholarly.citedby(pub)) if num<10]
        self.assertEqual(len(top10_citations), 10)

if __name__ == '__main__':
    unittest.main()
