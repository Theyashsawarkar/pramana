"""The password prompt's keys: generated annotations, the vendored keys module."""
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class Keys(unittest.TestCase):
    def test_annotations_and_readme_are_generated(self):
        r = subprocess.run([sys.executable, str(ROOT / "scripts" / "keybinds.py"), "--check"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_keys_module_is_vendored_from_vyom(self):
        self.assertTrue((ROOT / "lib" / "keys.py").read_text().startswith("# Vendored from Vyom's vyom/keys.py v"))

    def test_installed_root_owned_with_the_agent(self):
        self.assertIn('"lib/keys.py:$lib/keys.py:644"', (ROOT / "install.sh").read_text())


if __name__ == "__main__":
    unittest.main()
