from __future__ import annotations

import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.connection import endpoint_env_namespace  # noqa: E402


class EndpointEnvironmentNamespaceTests(unittest.TestCase):
    def test_default_endpoint_uses_unsuffixed_fluent_variables(self) -> None:
        self.assertEqual(endpoint_env_namespace(None), ("1", "FLUENT", ""))

    def test_numbered_endpoint_preserves_existing_fluent_suffix_convention(self) -> None:
        self.assertEqual(endpoint_env_namespace("3"), ("3", "FLUENT", "3"))

    def test_student_endpoint_uses_named_student_variables(self) -> None:
        self.assertEqual(endpoint_env_namespace("student"), ("student", "STUDENT", ""))


if __name__ == "__main__":
    unittest.main()
