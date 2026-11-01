#!/usr/bin/env python3
"""Check the plugin's structure and writing rules. Exits with 1 if anything fails."""

import json
import re
import sys
from pathlib import Path
from typing import Dict, Iterator, List

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"

NAME_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
MAX_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 200  # The limit for skills uploaded to claude.ai.
MAX_SKILL_LINES = 500
REFERENCED_FILE = re.compile(r"`((?:references|scripts)/[^`\s]+)`")
BANNED_CHARACTERS = {"—": "em dash", "–": "en dash"}
CHECKED_SUFFIXES = {".md", ".py", ".json", ".yml"}
SKIPPED_FOLDERS = {".git", "dist", "__pycache__"}


def parse_frontmatter(text: str) -> Dict[str, str]:
    """Read the simple key: value frontmatter that SKILL.md files use."""
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        return {}
    fields = (line.split(":", 1) for line in match.group(1).splitlines() if ":" in line)
    return {key.strip(): value.strip() for key, value in fields}


def check_skill(folder: Path) -> Iterator[str]:
    skill_file = folder / "SKILL.md"
    label = folder.name
    if not skill_file.exists():
        yield f"{label}: SKILL.md is missing"
        return

    text = skill_file.read_text(encoding="utf-8")
    fields = parse_frontmatter(text)
    name = fields.get("name", "")
    description = fields.get("description", "")

    if name != label:
        yield f"{label}: frontmatter name {name!r} must match the folder"
    if not NAME_PATTERN.match(name) or len(name) > MAX_NAME_LENGTH:
        yield f"{label}: invalid skill name"
    if not description:
        yield f"{label}: description is missing"
    if len(description) > MAX_DESCRIPTION_LENGTH:
        yield f"{label}: description has {len(description)} characters, limit {MAX_DESCRIPTION_LENGTH}"
    if len(text.splitlines()) > MAX_SKILL_LINES:
        yield f"{label}: SKILL.md is longer than {MAX_SKILL_LINES} lines"

    for reference in REFERENCED_FILE.findall(text):
        if not (folder / reference).exists():
            yield f"{label}: references missing file {reference}"


def check_manifests() -> Iterator[str]:
    plugin = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
    marketplace = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
    json.loads((ROOT / ".mcp.json").read_text(encoding="utf-8"))

    entry_names = [entry["name"] for entry in marketplace["plugins"]]
    if plugin["name"] not in entry_names:
        yield "marketplace.json must list the plugin under the same name as plugin.json"
    if not (ROOT / plugin["icon"]).exists():
        yield f"plugin.json points to a missing icon: {plugin['icon']}"


def check_characters() -> Iterator[str]:
    for path in sorted(ROOT.rglob("*")):
        if path.suffix not in CHECKED_SUFFIXES or SKIPPED_FOLDERS.intersection(path.parts):
            continue
        if path.resolve() == Path(__file__).resolve():
            continue
        text = path.read_text(encoding="utf-8")
        for character, name in BANNED_CHARACTERS.items():
            if character in text:
                yield f"{path.relative_to(ROOT)}: contains an {name}"


def collect_errors() -> List[str]:
    errors = list(check_manifests()) + list(check_characters())
    folders = sorted(path for path in SKILLS.iterdir() if path.is_dir())
    if not folders:
        errors.append("no skills found")
    for folder in folders:
        errors.extend(check_skill(folder))
    return errors


def main() -> int:
    errors = collect_errors()
    for error in errors:
        print(f"Error: {error}")
    if not errors:
        print("Validation passed.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
