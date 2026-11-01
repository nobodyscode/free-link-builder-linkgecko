#!/usr/bin/env python3
"""Zip each skill into dist/ for upload to claude.ai.

Each archive holds the skill folder at its top level, as the upload requires.
"""

import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
DIST = ROOT / "dist"
SKIPPED_NAMES = {"__pycache__", ".DS_Store"}


def package(skill: Path) -> Path:
    archive = DIST / f"{skill.name}.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
        for path in sorted(skill.rglob("*")):
            if path.is_file() and not SKIPPED_NAMES.intersection(path.parts):
                bundle.write(path, path.relative_to(SKILLS))
    return archive


def main() -> int:
    shutil.rmtree(DIST, ignore_errors=True)
    DIST.mkdir()
    for skill in sorted(path for path in SKILLS.iterdir() if path.is_dir()):
        print(f"Packaged {package(skill).relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
