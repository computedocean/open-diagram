"""The files a release depends on name the same version, so the PyPI upload and the MCP Registry listing match."""
import json
import os
import re
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from open_diagram import __version__  # noqa: E402


def read(name):
    with open(os.path.join(ROOT, name), encoding="utf-8") as fh:
        return fh.read()


class ReleaseFilesTests(unittest.TestCase):
    def test_versions_match(self):
        server = json.loads(read("server.json"))
        pyproject = re.search(r'^version = "([^"]+)"', read("pyproject.toml"), re.M).group(1)
        self.assertEqual([pyproject, server["version"], server["packages"][0]["version"]], [__version__] * 3)

    def test_registry_can_prove_the_package_is_ours(self):
        # The registry looks for this line in the README that PyPI shows; it must be followed by a space,
        # a newline or the end of the comment.
        server = json.loads(read("server.json"))
        self.assertRegex(read("README.md"), r"mcp-name: " + re.escape(server["name"]) + r"(\s|-->)")
        self.assertEqual(server["packages"][0]["identifier"], "open-diagram")

    def test_registry_description_fits(self):
        self.assertLessEqual(len(json.loads(read("server.json"))["description"]), 100)


if __name__ == "__main__":
    unittest.main()
