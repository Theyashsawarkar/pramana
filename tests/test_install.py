"""The pieces that must agree: the service runs the installed copy,
isolated, and the installer installs what the service runs."""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(*p):
    with open(os.path.join(ROOT, *p)) as f:
        return f.read()


class Install(unittest.TestCase):
    def test_service_runs_the_root_owned_copy_isolated(self):
        unit = read("systemd", "pramana.service")
        self.assertIn("ExecStart=/usr/bin/python3 -I /usr/local/lib/pramana/agent.py", unit)
        self.assertIn("RestartPreventExitStatus=3", unit)   # agent.py exits 3 when another agent serves the session
        self.assertIn("sys.exit(3)", read("lib", "agent.py"))

    def test_installer_installs_every_runtime_file(self):
        sh = read("install.sh")
        for f in ("lib/agent.py", "lib/theme.py", "systemd/pramana.service"):
            self.assertIn(f'"{f}:', sh, f)

    def test_theme_is_loaded_by_path_not_from_sys_path(self):
        agent = read("lib", "agent.py")
        self.assertIn("spec_from_file_location", agent)
        self.assertNotRegex(agent, r"(?m)^import theme|^from theme")

    def test_version_has_a_changelog_entry(self):
        v = re.search(r'^VERSION = "(.+)"', read("lib", "agent.py"), re.M).group(1)
        self.assertRegex(read("CHANGELOG.md"), rf"(?m)^## v{re.escape(v)} ")


if __name__ == "__main__":
    unittest.main()
