import subprocess
import sys
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import package_skills  # noqa: E402
import sync_shared  # noqa: E402
import validate_repo  # noqa: E402


class Repo(unittest.TestCase):
    def test_structure_and_writing_rules_pass(self):
        self.assertEqual(validate_repo.collect_errors(), [])

    def test_shared_files_are_in_sync(self):
        self.assertEqual(sync_shared.out_of_date(), [])

    def test_frontmatter_parser_keeps_colons_in_values(self):
        fields = validate_repo.parse_frontmatter("---\nname: x\ndescription: a: b\n---\nbody")
        self.assertEqual(fields, {"name": "x", "description": "a: b"})

    def test_every_skill_zip_has_the_folder_at_its_top_level(self):
        for skill in sorted(path for path in package_skills.SKILLS.iterdir() if path.is_dir()):
            package_skills.DIST.mkdir(exist_ok=True)
            with zipfile.ZipFile(package_skills.package(skill)) as bundle:
                names = bundle.namelist()
            self.assertIn(f"{skill.name}/SKILL.md", names)
            self.assertTrue(all(name.startswith(f"{skill.name}/") for name in names))

    def test_scripts_show_help_without_errors(self):
        for script in ROOT.glob("skills/*/scripts/*.py"):
            result = subprocess.run([sys.executable, str(script), "--help"], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, script)


if __name__ == "__main__":
    unittest.main()
