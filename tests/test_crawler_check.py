import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "skills/ai-crawler-check/scripts/crawler_check.py"
spec = importlib.util.spec_from_file_location("crawler_check", SCRIPT)
crawler_check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(crawler_check)


def state_of(robots_text, token):
    groups, _ = crawler_check.parse_robots(robots_text)
    agents = crawler_check.check_robots(groups)["agents"]
    return next(agent["state"] for agent in agents if agent["token"] == token)


class RobotsMatching(unittest.TestCase):
    def test_wildcard_block_applies_without_a_specific_group(self):
        self.assertEqual(state_of("User-agent: *\nDisallow: /", "GPTBot"), "blocked")

    def test_specific_group_overrides_the_wildcard(self):
        text = "User-agent: *\nDisallow: /\n\nUser-agent: GPTBot\nDisallow:"
        self.assertEqual(state_of(text, "GPTBot"), "allowed")
        self.assertEqual(state_of(text, "ClaudeBot"), "blocked")

    def test_matching_ignores_case(self):
        self.assertEqual(state_of("User-agent: gptbot\nDisallow: /", "GPTBot"), "blocked")

    def test_agents_can_share_a_group(self):
        text = "User-agent: GPTBot\nUser-agent: ClaudeBot\nDisallow: /"
        self.assertEqual(state_of(text, "GPTBot"), "blocked")
        self.assertEqual(state_of(text, "ClaudeBot"), "blocked")

    def test_groups_for_the_same_agent_are_merged(self):
        text = "User-agent: GPTBot\nDisallow: /private/\n\nUser-agent: GPTBot\nDisallow: /"
        self.assertEqual(state_of(text, "GPTBot"), "blocked")

    def test_partial_block_is_not_a_site_wide_block(self):
        self.assertEqual(state_of("User-agent: OAI-SearchBot\nDisallow: /checkout/", "OAI-SearchBot"), "partial")

    def test_longest_rule_wins_and_allow_wins_a_tie(self):
        self.assertTrue(crawler_check.is_allowed([("disallow", "/"), ("allow", "/blog")], "/blog/post")[0])
        self.assertFalse(crawler_check.is_allowed([("allow", "/blog"), ("disallow", "/blog/private")], "/blog/private/x")[0])
        self.assertTrue(crawler_check.is_allowed([("disallow", "/page"), ("allow", "/page")], "/page")[0])

    def test_wildcards_and_end_anchors(self):
        self.assertFalse(crawler_check.is_allowed([("disallow", "/*.pdf$")], "/files/guide.pdf")[0])
        self.assertTrue(crawler_check.is_allowed([("disallow", "/*.pdf$")], "/files/guide.pdf.html")[0])

    def test_comments_and_sitemaps_are_parsed(self):
        groups, sitemaps = crawler_check.parse_robots(
            "# note\nUser-agent: *  # all\nDisallow: /x\nSitemap: https://example.com/s.xml"
        )
        self.assertEqual(groups[0]["rules"], [("disallow", "/x")])
        self.assertEqual(sitemaps, ["https://example.com/s.xml"])

    def test_crawl_delay_does_not_split_a_group(self):
        self.assertEqual(state_of("User-agent: OAI-SearchBot\nCrawl-delay: 5\nDisallow: /", "OAI-SearchBot"), "blocked")

    def test_byte_order_mark_does_not_hide_the_first_line(self):
        self.assertEqual(state_of("\ufeffUser-agent: *\nDisallow: /", "GPTBot"), "blocked")

    def test_empty_user_agent_matches_nothing(self):
        self.assertEqual(state_of("User-agent:\nDisallow: /", "GPTBot"), "allowed")

    def test_homepage_only_allow_is_still_a_site_wide_block(self):
        self.assertEqual(state_of("User-agent: *\nDisallow: /\nAllow: /$", "Googlebot"), "blocked")

    def test_overridden_disallow_is_not_reported_as_a_block(self):
        self.assertEqual(state_of("User-agent: *\nDisallow: /\nAllow: /", "Googlebot"), "allowed")

    def test_misspelled_token_is_reported(self):
        groups, _ = crawler_check.parse_robots("User-agent: GPT-Bot\nDisallow: /")
        self.assertEqual(crawler_check.find_misspelled_tokens(groups), [{"token": "GPT-Bot", "meant": "GPTBot"}])


class Findings(unittest.TestCase):
    def findings_for(self, text):
        report = crawler_check.run_offline(text)
        return crawler_check.build_findings(report)

    def test_blocked_search_indexer_is_p0_and_listed_first(self):
        findings = self.findings_for("User-agent: GPTBot\nDisallow: /\n\nUser-agent: OAI-SearchBot\nDisallow: /")
        self.assertTrue(findings[0].startswith("P0: OAI-SearchBot"))
        self.assertTrue(any(finding.startswith("Info: GPTBot") for finding in findings))

    def test_search_indexers_with_the_same_partial_block_share_one_finding(self):
        findings = self.findings_for("User-agent: *\nDisallow: /api/")
        partial = [finding for finding in findings if "cannot read /api/" in finding]
        self.assertEqual(len(partial), 1)
        self.assertIn("Googlebot", partial[0])
        self.assertIn("Bingbot", partial[0])

    def test_missing_robots_file_is_not_treated_as_a_block(self):
        robots = crawler_check.check_robots([])
        robots.update(status=404, error="HTTP 404")
        findings = crawler_check.robots_findings(robots)
        self.assertEqual(len(findings), 1)
        self.assertTrue(findings[0].startswith("P2"))
        self.assertTrue(all(agent["state"] == "allowed" for agent in robots["agents"]))

    def test_server_error_on_robots_file_is_p1(self):
        robots = crawler_check.check_robots([])
        robots.update(status=503, error="HTTP 503")
        self.assertTrue(crawler_check.robots_findings(robots)[0].startswith("P1"))


class Homepage(unittest.TestCase):
    def page(self, body, headers=None):
        return crawler_check.check_homepage({"status": 200, "error": None, "headers": headers or {}, "body": body})

    def test_reads_restrictions_from_meta_and_header(self):
        page = self.page('<meta name="robots" content="noindex">', {"X-Robots-Tag": "nosnippet"})
        self.assertEqual(page["restrictions"], ["noindex", "nosnippet"])

    def test_reads_meta_robots_in_either_attribute_order(self):
        self.assertEqual(self.page('<meta content="noindex" name="robots">')["restrictions"], ["noindex"])

    def test_restrictions_get_their_own_severity(self):
        page = self.page('<meta name="robots" content="noindex, nosnippet, noarchive">' + "<p>" + "words " * 400 + "</p>")
        findings = crawler_check.homepage_findings(page)
        self.assertTrue(any(finding.startswith("P0") and "noindex" in finding for finding in findings))
        self.assertTrue(any(finding.startswith("P1") and "nosnippet" in finding for finding in findings))
        self.assertTrue(any(finding.startswith("P2") and "noarchive" in finding for finding in findings))

    def test_reads_jsonld_types_from_graphs_and_lists(self):
        body = (
            '<script type="application/ld+json">{"@graph":[{"@type":"Organization"}]}</script>'
            '<script type="application/ld+json">[{"@type":["WebSite","Thing"]}]</script>'
            '<script type="application/ld+json">{broken</script>'
        )
        count, types = crawler_check.jsonld_types(body)
        self.assertEqual(count, 3)
        self.assertEqual(types, ["(invalid JSON-LD)", "Organization", "Thing", "WebSite"])

    def test_thin_html_is_flagged_and_real_text_is_not(self):
        self.assertTrue(self.page('<div id="root"></div><script>app()</script>')["likely_needs_javascript"])
        self.assertFalse(self.page("<p>" + "words " * 400 + "</p>")["likely_needs_javascript"])

    def test_html_soft_404_is_not_a_text_file(self):
        self.assertFalse(crawler_check.looks_like_text_file({"status": 200, "body": "<!doctype html><html>"}))
        self.assertTrue(crawler_check.looks_like_text_file({"status": 200, "body": "# Site\n> About"}))


if __name__ == "__main__":
    unittest.main()
