#!/usr/bin/env python3
"""Regression tests: install/update reload the user's Plasma Shell safely."""
from pathlib import Path
import os
import shutil
import subprocess
import tempfile
import unittest
import time

SOURCE = Path(__file__).resolve().parents[1]
PACKAGE = "application-dashboard-plus-kubuntu24.04-amd64.plasmoid"


@unittest.skipIf(os.geteuid() == 0, "Installer explicitly refuses root; test as desktop user")
class InstallerRestartTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.bin = self.root / "bin"
        self.bin.mkdir()
        for name in ("install.sh", "update.sh"):
            shutil.copy2(SOURCE / name, self.root / name)
        (self.root / PACKAGE).write_text("mock plasmoid\n")
        self.log = self.root / "actions.log"
        self.env = os.environ.copy()
        self.env.update({
            "PATH": f"{self.bin}:{self.env['PATH']}",
            "MOCK_LOG": str(self.log),
            "MOCK_SYSTEMCTL_ACTIVE": "1",
            "MOCK_PGREP_ACTIVE": "0",
            "DISPLAY": ":99",
            "WAYLAND_DISPLAY": "",
        })
        self.mock("plasmashell", """#!/bin/sh
if [ "$1" = "--version" ]; then echo 'plasmashell 5.27.12'; exit 0; fi
printf 'plasmashell %s\n' "$*" >> "$MOCK_LOG"
""")
        self.mock("kpackagetool5", """#!/bin/sh
printf 'kpackagetool5 %s\n' "$*" >> "$MOCK_LOG"
if [ "$3" = "--show" ]; then exit 1; fi
exit 0
""")
        self.mock("systemctl", """#!/bin/sh
printf 'systemctl %s\n' "$*" >> "$MOCK_LOG"
if [ "$2" = "is-active" ]; then
    [ "$MOCK_SYSTEMCTL_ACTIVE" = "1" ] && exit 0 || exit 3
fi
exit 0
""")
        self.mock("pgrep", """#!/bin/sh
printf 'pgrep %s\n' "$*" >> "$MOCK_LOG"
[ "$MOCK_PGREP_ACTIVE" = "1" ]
""")
        self.mock("nohup", """#!/bin/sh
printf 'nohup %s\n' "$*" >> "$MOCK_LOG"
exit 0
""")
        self.mock("git", """#!/bin/sh
case "$1" in
    branch) echo main ;;
    status) : ;;
    pull) printf 'git %s\n' "$*" >> "$MOCK_LOG" ;;
    *) exit 1 ;;
esac
""")

    def mock(self, name, script):
        path = self.bin / name
        path.write_text(script)
        path.chmod(0o755)

    def run_script(self, script, *args, env=None):
        result = subprocess.run(
            ["bash", str(self.root / script), *args],
            cwd=self.root, env=env or self.env,
            text=True, capture_output=True, timeout=15
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def log_text(self):
        return self.log.read_text() if self.log.exists() else ""

    def test_install_restarts_active_plasma_service(self):
        self.run_script("install.sh")
        self.assertIn("kpackagetool5 --type Plasma/Applet --install", self.log_text())
        self.assertIn("systemctl --user restart plasma-plasmashell.service", self.log_text())

    def test_install_no_restart_option(self):
        self.run_script("install.sh", "--no-restart")
        self.assertIn("kpackagetool5 --type Plasma/Applet --install", self.log_text())
        self.assertNotIn("systemctl", self.log_text())
        self.assertNotIn("nohup", self.log_text())

    def test_package_mode_can_skip_restart(self):
        self.run_script("install.sh", "--package", str(self.root / PACKAGE), "--no-restart")
        self.assertIn("kpackagetool5 --type Plasma/Applet --install", self.log_text())
        self.assertNotIn("systemctl", self.log_text())

    def test_headless_skips_restart(self):
        env = dict(self.env, DISPLAY="", WAYLAND_DISPLAY="")
        self.run_script("install.sh", env=env)
        self.assertNotIn("systemctl", self.log_text())
        self.assertNotIn("nohup", self.log_text())

    def test_replace_existing_shell_if_user_service_not_active(self):
        env = dict(self.env, MOCK_SYSTEMCTL_ACTIVE="0", MOCK_PGREP_ACTIVE="1")
        self.run_script("install.sh", env=env)
        for _ in range(20):
            if "nohup plasmashell --replace" in self.log_text():
                break
            time.sleep(0.05)
        self.assertIn("nohup plasmashell --replace", self.log_text())
        self.assertNotIn("systemctl --user restart", self.log_text())

    def test_update_forwards_no_restart_to_installer(self):
        self.run_script("update.sh", "--no-restart")
        self.assertIn("git pull --ff-only origin main", self.log_text())
        self.assertIn("kpackagetool5 --type Plasma/Applet --install", self.log_text())
        self.assertNotIn("systemctl", self.log_text())

    def test_update_restarts_by_default(self):
        self.run_script("update.sh")
        self.assertIn("systemctl --user restart plasma-plasmashell.service", self.log_text())


if __name__ == "__main__":
    unittest.main()
