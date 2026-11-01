#!/usr/bin/env python3
"""Check whether AI crawlers can reach a site.

Usage:
  python3 crawler_check.py example.com
  python3 crawler_check.py https://example.com --json
  python3 crawler_check.py --robots-file robots.txt

Reads robots.txt with Robots Exclusion Protocol matching (RFC 9309), then checks
llms.txt, sitemap.xml and the homepage. Results come from plain, unauthenticated
requests, so confirm serious findings in server logs or the CDN dashboard.

Standard library only. Python 3.8 or newer.
"""

import argparse
import datetime
import json
import re
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, NamedTuple, Optional, Sequence, Tuple

USER_AGENT = (
    "Mozilla/5.0 (compatible; free-link-builder/1.0; "
    "+https://github.com/nobodyscode/free-link-builder-linkgecko)"
)
TIMEOUT_SECONDS = 15
MAX_BODY_BYTES = 2_500_000
ANY_PAGE = "/any-page"  # Shows whether a rule reaches past the homepage.

SEARCH, TRAINING, FETCHER, CONTROL = "search", "training", "fetcher", "control"

ROLE_LABELS = {
    SEARCH: "Search indexer",
    TRAINING: "Training crawler",
    FETCHER: "User-triggered fetcher",
    CONTROL: "Control token",
}


class Agent(NamedTuple):
    token: str
    operator: str
    role: str
    effect: str


AGENTS = (
    Agent("OAI-SearchBot", "OpenAI", SEARCH, "kept out of ChatGPT search"),
    Agent("Claude-SearchBot", "Anthropic", SEARCH, "kept out of Claude search"),
    Agent("PerplexityBot", "Perplexity", SEARCH, "kept out of Perplexity answers"),
    Agent("Googlebot", "Google", SEARCH, "kept out of Google Search and AI Overviews"),
    Agent("Bingbot", "Microsoft", SEARCH, "kept out of Bing and Copilot"),
    Agent("DuckAssistBot", "DuckDuckGo", SEARCH, "kept out of DuckAssist"),
    Agent("YouBot", "You.com", SEARCH, "kept out of You.com answers"),
    Agent("ChatGPT-User", "OpenAI", FETCHER, "OpenAI says robots.txt rules may not apply"),
    Agent("Claude-User", "Anthropic", FETCHER, "Claude cannot open pages on request"),
    Agent("Perplexity-User", "Perplexity", FETCHER, "documented as generally ignoring robots.txt"),
    Agent("meta-externalfetcher", "Meta", FETCHER, "may bypass robots.txt"),
    Agent("MistralAI-User", "Mistral", FETCHER, "Le Chat cannot open pages on request"),
    Agent("GPTBot", "OpenAI", TRAINING, "excluded from OpenAI training"),
    Agent("ClaudeBot", "Anthropic", TRAINING, "excluded from Anthropic training"),
    Agent("anthropic-ai", "Anthropic (older token)", TRAINING, "older token some sites still use"),
    Agent("meta-externalagent", "Meta", TRAINING, "excluded from Meta training"),
    Agent("Amazonbot", "Amazon", TRAINING, "excluded from Amazon AI"),
    Agent("CCBot", "Common Crawl", TRAINING, "excluded from a dataset many labs use"),
    Agent("Bytespider", "ByteDance", TRAINING, "widely reported to ignore robots.txt"),
    Agent("Ai2Bot", "Allen Institute", TRAINING, "excluded from AI2 datasets"),
    Agent("Diffbot", "Diffbot", TRAINING, "excluded from Diffbot datasets"),
    Agent("cohere-training-data-crawler", "Cohere", TRAINING, "excluded from Cohere training"),
    Agent("Google-Extended", "Google", CONTROL, "excluded from Gemini training and grounding"),
    Agent("Applebot-Extended", "Apple", CONTROL, "excluded from Apple model training"),
)

Rule = Tuple[str, str]  # ("allow" or "disallow", path pattern)


# ------------------------------------------------------------------ network


def fetch(url: str) -> Dict[str, Any]:
    """Fetch a URL and return its status, headers and text, or an error description."""
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(
            request, timeout=TIMEOUT_SECONDS, context=ssl.create_default_context()
        ) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            return {
                "status": response.status,
                "headers": dict(response.headers),
                "body": response.read(MAX_BODY_BYTES).decode(charset, errors="replace"),
                "error": None,
            }
    except urllib.error.HTTPError as error:
        return {
            "status": error.code,
            "headers": dict(error.headers or {}),
            "body": "",
            "error": f"HTTP {error.code}",
        }
    except Exception as error:  # A failed request is a finding here, not a crash.
        return {"status": None, "headers": {}, "body": "", "error": f"{type(error).__name__}: {error}"}


# --------------------------------------------------------------- robots.txt


def parse_robots(text: str) -> Tuple[List[Dict[str, Any]], List[str]]:
    """Split robots.txt into groups of {agents, rules}, plus any sitemap URLs."""
    groups: List[Dict[str, Any]] = []
    sitemaps: List[str] = []
    current: Optional[Dict[str, Any]] = None
    in_agent_lines = False

    for raw_line in text.lstrip("\ufeff").splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if ":" not in line:
            continue
        field, value = (part.strip() for part in line.split(":", 1))
        field = field.lower()

        if field == "user-agent":
            if current is None or not in_agent_lines:
                current = {"agents": [], "rules": []}
                groups.append(current)
            current["agents"].append(value)
            in_agent_lines = True
            continue

        if field in ("allow", "disallow") and current is not None:
            current["rules"].append((field, value))
            in_agent_lines = False
        elif field == "sitemap":
            sitemaps.append(value)

    return groups, sitemaps


def rules_for(groups: Sequence[Dict[str, Any]], token: str) -> Tuple[Optional[List[Rule]], str]:
    """Return the rules that apply to a token and how they matched.

    The longest user-agent prefix wins. RFC 9309 merges groups naming the same
    agent, so rules from all groups at the winning match are combined.
    """
    token_lower = token.lower()
    best_length = -1
    specific: List[Rule] = []
    wildcard: Optional[List[Rule]] = None

    for group in groups:
        for agent in group["agents"]:
            agent_lower = agent.lower()
            if agent_lower == "*":
                wildcard = (wildcard or []) + group["rules"]
            elif agent_lower and token_lower.startswith(agent_lower):
                if len(agent_lower) > best_length:
                    best_length, specific = len(agent_lower), list(group["rules"])
                elif len(agent_lower) == best_length:
                    specific += group["rules"]

    if best_length >= 0:
        return specific, "own group"
    if wildcard is not None:
        return wildcard, "wildcard group"
    return None, "no group"


def pattern_length(pattern: str, path: str) -> int:
    """Return the pattern's length if it matches the path, otherwise -1."""
    if not pattern:
        return -1  # An empty rule matches nothing.
    regex = "".join(
        ".*" if char == "*" else "$" if char == "$" else re.escape(char) for char in pattern
    )
    return len(pattern) if re.match(regex, path) else -1


def is_allowed(rules: Optional[Sequence[Rule]], path: str = "/") -> Tuple[bool, str]:
    """Apply longest-match precedence. Allow wins a tie, and no match means allowed."""
    best_kind, best_pattern, best_length = "allow", None, -1
    for kind, pattern in rules or ():
        length = pattern_length(pattern, path)
        if length > best_length or (length == best_length and length >= 0 and kind == "allow"):
            best_kind, best_pattern, best_length = kind, pattern, length
    if best_pattern is None:
        return True, "no matching rule"
    return best_kind == "allow", f"{best_kind.capitalize()}: {best_pattern}"


def check_agent(groups: Sequence[Dict[str, Any]], agent: Agent) -> Dict[str, Any]:
    rules, matched_by = rules_for(groups, agent.token)
    root_allowed, root_rule = is_allowed(rules, "/")
    page_allowed, page_rule = is_allowed(rules, ANY_PAGE)
    allowed = root_allowed and page_allowed
    deciding_rule = page_rule if root_allowed and not page_allowed else root_rule
    blocked_paths = [
        pattern
        for kind, pattern in rules or ()
        if kind == "disallow" and pattern and not is_allowed(rules, pattern.replace("*", "").rstrip("$"))[0]
    ]

    if not allowed:
        state = "blocked"
    elif blocked_paths:
        state = "partial"
    else:
        state = "allowed"

    return {
        **agent._asdict(),
        "state": state,
        "matched_by": matched_by,
        "rule": deciding_rule,
        "blocked_paths": blocked_paths if allowed else [],
    }


def find_misspelled_tokens(groups: Sequence[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Find tokens that differ from a known agent only by punctuation or spacing."""
    known = {agent.token.lower(): agent.token for agent in AGENTS}
    squash = lambda value: re.sub(r"[-_ ]", "", value.lower())
    squashed_known = {squash(token): canonical for token, canonical in known.items()}

    found = []
    tokens = {agent for group in groups for agent in group["agents"]}
    for token in sorted(tokens):
        if token == "*" or token.lower() in known:
            continue
        if squash(token) in squashed_known:
            found.append({"token": token, "meant": squashed_known[squash(token)]})
    return found


def check_robots(groups: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "agents": [check_agent(groups, agent) for agent in AGENTS],
        "misspelled": find_misspelled_tokens(groups),
    }


# ----------------------------------------------------------------- homepage


def jsonld_types(body: str) -> Tuple[int, List[str]]:
    """Return the number of JSON-LD blocks in a page and the types they declare."""
    blocks = re.findall(
        r"<script[^>]+application/ld\+json[^>]*>(.*?)</script>", body, re.IGNORECASE | re.DOTALL
    )
    types = set()
    for block in blocks:
        try:
            data = json.loads(block.strip())
        except ValueError:
            types.add("(invalid JSON-LD)")
            continue
        if isinstance(data, dict):
            data = data.get("@graph", [data])
        for item in data if isinstance(data, list) else []:
            declared = item.get("@type") if isinstance(item, dict) else None
            if declared:
                types.update(declared if isinstance(declared, list) else [declared])
    return len(blocks), sorted(str(value) for value in types)


def visible_text_length(body: str) -> int:
    text = re.sub(r"<(script|style)\b.*?</\1>", " ", body, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    return len(re.sub(r"\s+", " ", text).strip())


def check_homepage(result: Dict[str, Any]) -> Dict[str, Any]:
    body = result["body"] or ""
    headers = {key.lower(): value for key, value in result["headers"].items()}
    x_robots = headers.get("x-robots-tag")

    title_match = re.search(r"<title[^>]*>(.*?)</title>", body, re.IGNORECASE | re.DOTALL)
    meta_robots = re.findall(
        r'<meta\b(?=[^>]*\bname=["\']?robots\b)[^>]*\bcontent=["\'](.*?)["\']', body, re.IGNORECASE
    )
    directives = ",".join(meta_robots + ([x_robots] if x_robots else [])).lower()
    jsonld_count, types = jsonld_types(body)
    text_length = visible_text_length(body)

    return {
        "status": result["status"],
        "error": result["error"],
        "title": re.sub(r"\s+", " ", title_match.group(1)).strip()[:200] if title_match else None,
        "meta_robots": meta_robots,
        "x_robots_tag": x_robots,
        "restrictions": [
            name
            for name in ("noindex", "nosnippet", "noarchive", "nocache", "noai", "noimageai")
            if name in directives
        ],
        "max_snippet_zero": "max-snippet:0" in directives.replace(" ", ""),
        "jsonld_blocks": jsonld_count,
        "jsonld_types": types,
        "visible_text_chars": text_length,
        "html_bytes": len(body),
        "likely_needs_javascript": bool(body)
        and (text_length < 800 or (len(body) > 50_000 and text_length / len(body) < 0.02)),
    }


# ----------------------------------------------------------------- findings


def robots_findings(robots: Dict[str, Any]) -> List[str]:
    findings = []
    status = robots.get("status")
    if robots.get("error") and (status is None or status >= 500):
        findings.append(
            f"P1: robots.txt failed ({robots['error']}). Crawlers may treat repeated "
            "server errors as a site-wide block."
        )
    elif robots.get("error"):
        findings.append(
            f"P2: robots.txt returned {robots['error']}. Crawlers generally read this as "
            "no restrictions, though a 401 or 403 may also signal a CDN or firewall rule."
        )

    severity = {SEARCH: "P0", FETCHER: "P1", TRAINING: "Info", CONTROL: "Info"}
    partial_blocks: Dict[str, List[str]] = {}
    for agent in robots.get("agents", []):
        if agent["state"] == "blocked":
            findings.append(
                f"{severity[agent['role']]}: {agent['token']} ({agent['operator']}) is blocked "
                f"by \"{agent['rule']}\": {agent['effect']}."
            )
        elif agent["state"] == "partial" and agent["role"] == SEARCH:
            partial_blocks.setdefault(", ".join(agent["blocked_paths"]), []).append(agent["token"])

    for paths, tokens in partial_blocks.items():
        findings.append(f"P2: {', '.join(tokens)} cannot read {paths}. Confirm this is intended.")

    for typo in robots.get("misspelled", []):
        findings.append(f"P2: robots.txt token \"{typo['token']}\" matches nothing. Did you mean {typo['meant']}?")
    return findings


def homepage_findings(page: Dict[str, Any]) -> List[str]:
    if page.get("error"):
        return [f"P0: the homepage request failed ({page['error']}). Confirm whether crawlers see the same."]

    findings = []
    severities = {"noindex": "P0", "nosnippet": "P1"}
    for restriction in page["restrictions"]:
        severity = severities.get(restriction, "P2")
        findings.append(f"{severity}: the homepage carries {restriction} in meta robots or X-Robots-Tag.")
    if page["max_snippet_zero"]:
        findings.append("P1: max-snippet:0 keeps the homepage text out of AI Overviews.")
    if page["likely_needs_javascript"]:
        findings.append(
            f"P1: the homepage has {page['visible_text_chars']} characters of text in "
            f"{page['html_bytes']} bytes of HTML. It may need JavaScript, which many AI fetchers do not run."
        )
    if not page["jsonld_blocks"]:
        findings.append("P2: the homepage has no JSON-LD structured data.")
    elif not any("organization" in value.lower() for value in page["jsonld_types"]):
        findings.append("P2: the homepage JSON-LD has no Organization type.")
    return findings


def build_findings(report: Dict[str, Any]) -> List[str]:
    findings = robots_findings(report["robots"])
    if "homepage" in report:
        findings += homepage_findings(report["homepage"])
        if not report["sitemap"]["present"] and not report["robots"]["sitemaps"]:
            findings.append("P2: no sitemap found at /sitemap.xml.")
        if not report["llms_txt"]["present"]:
            findings.append("P2: no llms.txt found. This file is optional.")

    rank = {"P0": 0, "P1": 1, "P2": 2, "Info": 3}
    findings.sort(key=lambda finding: rank.get(finding.split(":", 1)[0], 4))
    return findings or ["No blocks found by this request. Confirm at the CDN and in server logs."]


# ------------------------------------------------------------------- report


def looks_like_text_file(result: Dict[str, Any]) -> bool:
    """Reject soft 404s, where a missing file returns an HTML page with status 200."""
    return result["status"] == 200 and "<html" not in result["body"][:300].lower()


def run_online(domain: str) -> Dict[str, Any]:
    parts = urllib.parse.urlsplit(domain if "://" in domain else f"https://{domain}")
    base = f"{parts.scheme}://{parts.netloc}"

    robots_result = fetch(f"{base}/robots.txt")
    has_rules = robots_result["status"] == 200 and looks_like_text_file(robots_result)
    groups, sitemaps = parse_robots(robots_result["body"]) if has_rules else ([], [])
    robots = check_robots(groups)
    robots.update(status=robots_result["status"], error=robots_result["error"], sitemaps=sitemaps)

    llms = fetch(f"{base}/llms.txt")
    sitemap = fetch(f"{base}/sitemap.xml")
    sitemap_present = sitemap["status"] == 200 and re.search(r"<(urlset|sitemapindex)", sitemap["body"][:2000])

    return {
        "domain": domain,
        "robots": robots,
        "llms_txt": {"present": looks_like_text_file(llms), "bytes": len(llms["body"])},
        "sitemap": {"present": bool(sitemap_present), "urls": len(re.findall(r"<loc>", sitemap["body"]))},
        "homepage": check_homepage(fetch(f"{base}/")),
    }


def run_offline(robots_text: str) -> Dict[str, Any]:
    groups, sitemaps = parse_robots(robots_text)
    robots = check_robots(groups)
    robots.update(status=None, error=None, sitemaps=sitemaps)
    return {"domain": "saved robots.txt", "robots": robots}


def to_markdown(report: Dict[str, Any]) -> str:
    lines = [
        f"# AI crawler check: {report['domain']}",
        "",
        f"Checked {report['checked_on']} with a plain, unauthenticated request. "
        "Confirm serious findings in server logs or the CDN dashboard.",
        "",
        "## Findings",
        "",
    ]
    lines += [f"- {finding}" for finding in report["findings"]]
    lines += ["", "## Agents", "", "| Agent | Operator | Role | Rule | Access |", "|---|---|---|---|---|"]
    for agent in report["robots"]["agents"]:
        access = "**blocked**" if agent["state"] == "blocked" else agent["state"]
        lines.append(
            f"| {agent['token']} | {agent['operator']} | {ROLE_LABELS[agent['role']]} "
            f"| {agent['rule']} ({agent['matched_by']}) | {access} |"
        )

    if "homepage" in report:
        page = report["homepage"]
        lines += [
            "",
            "## Site files",
            "",
            f"- Homepage status: {page['status']}",
            f"- Title: {page['title'] or 'none'}",
            f"- JSON-LD types: {', '.join(page['jsonld_types']) or 'none'}",
            f"- llms.txt: {'present' if report['llms_txt']['present'] else 'absent'}",
            f"- Sitemap: {report['sitemap']['urls']} URLs" if report["sitemap"]["present"] else "- Sitemap: absent",
        ]
    return "\n".join(lines) + "\n"


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Check whether AI crawlers can reach a site.")
    parser.add_argument("domain", nargs="?", help="domain or URL to check")
    parser.add_argument("--robots-file", help="check a saved robots.txt without using the network")
    parser.add_argument("--json", action="store_true", help="print JSON instead of Markdown")
    args = parser.parse_args(argv)

    if args.robots_file:
        with open(args.robots_file, encoding="utf-8", errors="replace") as handle:
            report = run_offline(handle.read())
    elif args.domain:
        report = run_online(args.domain)
    else:
        parser.error("provide a domain or --robots-file")

    report["checked_on"] = datetime.date.today().isoformat()
    report["findings"] = build_findings(report)
    print(json.dumps(report, indent=2) if args.json else to_markdown(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
