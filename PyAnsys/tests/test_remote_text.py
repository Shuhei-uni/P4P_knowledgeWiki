"""Regression checks for literal C-source transfer through the Fluent API."""

import re
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from pyansys_fluent.remote_text import ascii_write_expression, read_text, write_ascii_text_new


class RemoteTextTests(unittest.TestCase):
    def test_content_is_numeric_and_preserves_literal_escapes(self):
        source = 'Message0("{\\"record\\":\\"probe\\"}\\n");\n/* C:\\tmp */'
        expression = ascii_write_expression("C:/P4P/probe.c", source)
        codes = re.search(r"'\((.*?)\)\)\)\)$", expression).group(1)
        self.assertEqual("".join(chr(int(code)) for code in codes.split()), source)
        self.assertNotIn("Message0", expression)

    def test_line_endings_are_not_normalized(self):
        for source in ["", "line\n", "line", "a\tb\r\nc"]:
            with self.subTest(source=source):
                expression = ascii_write_expression("C:/P4P/probe.c", source)
                codes = re.search(r"'\((.*?)\)\)\)\)$", expression).group(1)
                self.assertEqual(bytes(int(code) for code in codes.split()).decode("ascii"), source)

    def test_unsupported_text_is_rejected_before_remote_access(self):
        for source in ["caf\u00e9", "a\x00b", "\x7f"]:
            with self.subTest(source=source):
                solver = Mock()
                with self.assertRaises((UnicodeEncodeError, ValueError)):
                    write_ascii_text_new(solver, "C:/P4P/probe.c", source)
                solver.scheme.eval.assert_not_called()

    def test_existing_destination_is_not_overwritten(self):
        solver = Mock()
        with patch("pyansys_fluent.remote_text.remote_file_exists", return_value=True):
            with self.assertRaises(FileExistsError):
                write_ascii_text_new(solver, "C:/P4P/probe.c", "source")
        solver.scheme.eval.assert_not_called()

    def test_write_requires_exact_readback_and_uses_eval(self):
        solver = SimpleNamespace(scheme=SimpleNamespace(eval=Mock()))
        with patch("pyansys_fluent.remote_text.remote_file_exists", return_value=False), patch(
            "pyansys_fluent.remote_text.read_text", return_value="altered"
        ):
            with self.assertRaisesRegex(RuntimeError, "round-trip"):
                write_ascii_text_new(solver, "C:/P4P/probe.c", "source")
        solver.scheme.eval.assert_called_once()

    def test_missing_read_is_not_empty_text(self):
        with patch("pyansys_fluent.remote_text.remote_file_exists", return_value=False):
            with self.assertRaises(FileNotFoundError):
                read_text(Mock(), "C:/P4P/missing")


if __name__ == "__main__":
    unittest.main()
