import subprocess
import sys
import unittest
from pathlib import Path

DETECTOR = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "detect_ssh.py"
)


def log(second, ip="192.0.2.10", success=False):
    minute, second = divmod(second, 60)
    action = "Accepted" if success else "Failed"
    return (
        f"2026-09-21T06:{minute:02d}:{second:02d}Z "
        f"{action} password for labuser "
        f"from {ip} port 40000 ssh2\n"
    )


def detect(lines):
    result = subprocess.run(
        [sys.executable, str(DETECTOR)],
        input="".join(lines),
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.count("[ALERT]")


class DetectionTests(unittest.TestCase):
    def test_two_failures_no_alert(self):
        self.assertEqual(detect([log(0), log(10)]), 0)

    def test_three_failures_alert(self):
        self.assertEqual(detect([log(0), log(10), log(20)]), 1)

    def test_old_failure_excluded(self):
        self.assertEqual(detect([log(0), log(30), log(61)]), 0)

    def test_exactly_sixty_seconds_included(self):
        self.assertEqual(detect([log(0), log(30), log(60)]), 1)

    def test_different_ips_not_combined(self):
        self.assertEqual(
            detect([
                log(0),
                log(10, ip="192.0.2.20"),
                log(20),
            ]),
            0,
        )

    def test_success_not_counted_as_failure(self):
        self.assertEqual(
            detect([log(0), log(10, success=True), log(20)]),
            0,
        )

    def test_fourth_failure_no_duplicate_alert(self):
        self.assertEqual(
            detect([log(0), log(10), log(20), log(30)]),
            1,
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)