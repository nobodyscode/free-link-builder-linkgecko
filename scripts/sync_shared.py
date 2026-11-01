#!/usr/bin/env python3
"""Copy shared reference files into each skill, so every skill works as its own upload.

Usage:
  python3 scripts/sync_shared.py          # write the copies
  python3 scripts/sync_shared.py --check  # fail if a copy is out of date
"""

import sys
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parent.parent
SHARED = ROOT / "shared"
SKILLS = ROOT / "skills"

ALL_SKILLS = (
    "ai-crawler-check",
    "community-replies",
    "link-gap-audit",
    "link-outreach",
    "link-quality-check",
    "reddit-link-builder",
)
DRAFTING_SKILLS = ("community-replies", "link-outreach", "reddit-link-builder")

DESTINATIONS = {
    "evidence-rules.md": ALL_SKILLS,
    "linkgecko-connector.md": ALL_SKILLS,
    "writing-rules.md": DRAFTING_SKILLS,
}


def out_of_date() -> List[Path]:
    """Return every skill copy that is missing or differs from its shared source."""
    stale = []
    for filename, skills in DESTINATIONS.items():
        source = (SHARED / filename).read_bytes()
        for skill in skills:
            copy = SKILLS / skill / "references" / filename
            if not copy.exists() or copy.read_bytes() != source:
                stale.append(copy)
    return stale


def main() -> int:
    stale = out_of_date()
    if "--check" in sys.argv[1:]:
        for path in stale:
            print(f"Out of date: {path.relative_to(ROOT)}")
        return 1 if stale else 0

    for path in stale:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((SHARED / path.name).read_bytes())
    print(f"Updated {len(stale)} files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
