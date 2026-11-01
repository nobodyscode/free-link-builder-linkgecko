import importlib.util
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlparse

SCRIPT = Path(__file__).resolve().parent.parent / "skills/reddit-link-builder/scripts/build_search_links.py"
spec = importlib.util.spec_from_file_location("build_search_links", SCRIPT)
links = importlib.util.module_from_spec(spec)
spec.loader.exec_module(links)


class Subreddits(unittest.TestCase):
    def test_accepts_common_forms(self):
        for raw in ("SaaS", "r/SaaS", "/r/SaaS/", " R/SaaS "):
            self.assertEqual(links.clean_subreddit(raw), "SaaS")

    def test_rejects_anything_that_could_change_the_url(self):
        for raw in ("a", "bad name", "../admin", "r/x?y=1", "name-with-dash"):
            with self.assertRaises(ValueError):
                links.clean_subreddit(raw)


class Urls(unittest.TestCase):
    def test_fresh_threads_stay_in_the_subreddit_and_sort_by_new(self):
        url = urlparse(links.fresh_threads_url("freelance", "client won't pay"))
        query = parse_qs(url.query)
        self.assertEqual(url.path, "/r/freelance/search/")
        self.assertEqual(query["q"], ["client won't pay"])
        self.assertEqual(query["restrict_sr"], ["1"])
        self.assertEqual(query["sort"], ["new"])
        self.assertEqual(query["t"], ["month"])

    def test_quotes_and_symbols_are_encoded(self):
        url = links.top_results_url('"net 30" & invoices')
        self.assertEqual(parse_qs(urlparse(url).query)["q"], ['"net 30" & invoices'])
        self.assertNotIn(" ", url)

    def test_google_search_is_limited_to_reddit(self):
        url = links.google_url("invoice app")
        self.assertEqual(parse_qs(urlparse(url).query)["q"], ["site:reddit.com invoice app"])


class Keywords(unittest.TestCase):
    def test_accepts_strings_and_objects_and_removes_repeats(self):
        keywords = links.load_keywords(["invoice app", {"phrase": "Invoice App"}, {"phrase": "late fees", "subreddits": ["r/freelance"]}])
        self.assertEqual([item["phrase"] for item in keywords], ["invoice app", "late fees"])
        self.assertEqual(keywords[1]["subreddits"], ["freelance"])

    def test_rejects_bad_input(self):
        for bad in ([], {}, [{"subreddits": ["x"]}], [{"phrase": " "}], [{"phrase": None}], [3], [{"phrase": "x", "subreddits": "freelance"}]):
            with self.assertRaises(ValueError):
                links.load_keywords(bad)


class Pack(unittest.TestCase):
    def test_pack_has_every_link_type_and_the_notes(self):
        keywords = links.load_keywords([
            {"phrase": "late fees", "subreddits": ["freelance"], "layer": "problem", "intent": "problem-solving"}
        ])
        pack = links.render_pack(keywords, "example.com")
        self.assertIn("# Reddit search pack: example.com", pack)
        self.assertIn("Layer: problem | Likely intent: problem-solving", pack)
        self.assertIn("[Fresh threads in r/freelance]", pack)
        self.assertIn("[Top Reddit results, past year]", pack)
        self.assertIn("[Google results on Reddit]", pack)

    def test_file_name_comes_from_a_clean_domain(self):
        self.assertEqual(links.output_name("https://www.example.com/"), "reddit-search-pack-example.com.md")
        self.assertEqual(links.output_name(""), "reddit-search-pack-brand.md")


if __name__ == "__main__":
    unittest.main()
