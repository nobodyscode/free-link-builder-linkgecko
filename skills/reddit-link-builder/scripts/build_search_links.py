#!/usr/bin/env python3
"""Turn a contextual keyword list into Reddit search links the user can open.

Usage:
  python3 build_search_links.py keywords.json --domain example.com
  python3 build_search_links.py keywords.json --stdout

Input is a JSON list. Each item is a phrase string, or an object with a required
"phrase" and optional "subreddits", "layer", "intent" and "source" fields.

This script only builds URLs. It makes no network requests. Standard library only.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence
from urllib.parse import urlencode

SUBREDDIT_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_]{1,20}$")
DOMAIN_PREFIX = re.compile(r"^https?://(www\.)?", re.IGNORECASE)


def clean_subreddit(raw: str) -> str:
    """Return a bare subreddit name, accepting forms like "r/SaaS" or "/r/SaaS/"."""
    name = raw.strip().strip("/")
    if name.lower().startswith("r/"):
        name = name[2:]
    if not SUBREDDIT_NAME.match(name):
        raise ValueError(f"Not a valid subreddit name: {raw!r}")
    return name


def fresh_threads_url(subreddit: str, phrase: str) -> str:
    """Newest threads in one subreddit from the past month."""
    query = urlencode({"q": phrase, "restrict_sr": 1, "sort": "new", "t": "month"})
    return f"https://www.reddit.com/r/{subreddit}/search/?{query}"


def top_results_url(phrase: str) -> str:
    """Most relevant threads across Reddit from the past year."""
    query = urlencode({"q": phrase, "sort": "relevance", "t": "year"})
    return f"https://www.reddit.com/search/?{query}"


def google_url(phrase: str) -> str:
    """Google results limited to Reddit, which show threads that draw search readers."""
    return "https://www.google.com/search?" + urlencode({"q": f"site:reddit.com {phrase}"})


def load_keywords(items: Any) -> List[Dict[str, Any]]:
    """Validate raw JSON, normalize each item and drop repeated phrases."""
    if not isinstance(items, list) or not items:
        raise ValueError("Expected a non-empty JSON list of keywords.")

    keywords: List[Dict[str, Any]] = []
    seen = set()
    for position, item in enumerate(items, start=1):
        entry = {"phrase": item} if isinstance(item, str) else item
        if not isinstance(entry, dict):
            raise ValueError(f"Item {position} must be a string or an object.")

        phrase = str(entry.get("phrase") or "").strip()
        if not phrase:
            raise ValueError(f"Item {position} has no phrase.")
        if phrase.lower() in seen:
            continue
        seen.add(phrase.lower())

        subreddits = entry.get("subreddits") or []
        if not isinstance(subreddits, list):
            raise ValueError(f"Item {position}: subreddits must be a list.")

        keywords.append(
            {
                "phrase": phrase,
                "subreddits": [clean_subreddit(str(name)) for name in subreddits],
                "layer": entry.get("layer"),
                "intent": entry.get("intent"),
                "source": entry.get("source"),
            }
        )
    return keywords


def render_keyword(keyword: Dict[str, Any]) -> List[str]:
    phrase = keyword["phrase"]
    lines = [f"## {phrase}", ""]

    notes = [
        f"{label}: {keyword[field]}"
        for label, field in (("Layer", "layer"), ("Likely intent", "intent"), ("Source", "source"))
        if keyword.get(field)
    ]
    if notes:
        lines += [" | ".join(notes), ""]

    for subreddit in keyword["subreddits"]:
        lines.append(f"- [Fresh threads in r/{subreddit}]({fresh_threads_url(subreddit, phrase)})")
    lines.append(f"- [Top Reddit results, past year]({top_results_url(phrase)})")
    lines.append(f"- [Google results on Reddit]({google_url(phrase)})")
    lines.append("")
    return lines


def render_pack(keywords: Sequence[Dict[str, Any]], domain: str = "") -> str:
    title = f"# Reddit search pack: {domain}" if domain else "# Reddit search pack"
    lines = [
        title,
        "",
        "Start with the first 10 links. Pick threads that look like real questions, then paste each full post and its comments back with the URL.",
        "",
    ]
    for keyword in keywords:
        lines += render_keyword(keyword)
    return "\n".join(lines).rstrip() + "\n"


def output_name(domain: str) -> str:
    slug = DOMAIN_PREFIX.sub("", domain.strip()).strip("/")
    slug = re.sub(r"[^A-Za-z0-9.-]+", "-", slug) or "brand"
    return f"reddit-search-pack-{slug}.md"


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Build Reddit search links from a keyword list.")
    parser.add_argument("keywords", type=Path, help="path to the keywords JSON file")
    parser.add_argument("--domain", default="", help="brand domain, used in the title and file name")
    parser.add_argument("--stdout", action="store_true", help="print instead of writing a file")
    args = parser.parse_args(argv)

    try:
        keywords = load_keywords(json.loads(args.keywords.read_text(encoding="utf-8")))
    except (OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    pack = render_pack(keywords, args.domain)
    if args.stdout:
        print(pack, end="")
        return 0

    path = Path(output_name(args.domain))
    path.write_text(pack, encoding="utf-8")
    print(f"Wrote {path} with {len(keywords)} phrases.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
