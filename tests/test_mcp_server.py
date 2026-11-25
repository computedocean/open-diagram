"""The MCP server. The helpers are tested everywhere; the MCP tests run when the MCP toolkit is installed
(it is part of the main install since 0.6.2)."""
import asyncio
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from open_diagram import mcp_server  # noqa: E402

try:
    import mcp  # noqa: F401
    HAVE_MCP = True
except ImportError:
    HAVE_MCP = False

with open(os.path.join(ROOT, "examples", "email_delivery.json"), encoding="utf-8") as fh:
    EMAIL = fh.read()
with open(os.path.join(ROOT, "examples", "signup_flow.mmd"), encoding="utf-8") as fh:
    SIGNUP = fh.read()
GUIDE_EXAMPLE = mcp_server.GUIDE[mcp_server.GUIDE.index("{"): mcp_server.GUIDE.index("\n## Other shapes")]


class HelperTests(unittest.TestCase):
    def test_open_diagram_mcp_starts_the_server(self):
        # `uvx open-diagram mcp` is the command the MCP Registry gives apps; it must reach the server's own options.
        import contextlib
        import io
        from open_diagram import cli
        out = io.StringIO()
        with contextlib.redirect_stdout(out), self.assertRaises(SystemExit):
            cli.main(["mcp", "--help"])
        self.assertIn("usage: open-diagram mcp", out.getvalue())
        self.assertIn("--out", out.getvalue())

    def test_guide_example_is_clean(self):
        _, report = mcp_server.build(GUIDE_EXAMPLE).render()
        self.assertEqual(report.problems, [])

    def test_templates_and_icons_are_offered(self):
        self.assertIn("- gcp_event_pipeline:", mcp_server.template_text())
        _, report = mcp_server.build(mcp_server.template_text("azure_web_app")).render()
        self.assertEqual(report.problems, [])
        self.assertIn("aws/s3", mcp_server.guide_text().splitlines()[-1])
        with self.assertRaises(ValueError):
            mcp_server.template_text("nope")

    def test_format_is_detected(self):
        self.assertEqual(mcp_server.build(EMAIL).title, "How an email is delivered")
        self.assertEqual(mcp_server.build(SIGNUP).title, "How a new account is created")

    def test_files_stay_in_the_output_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = mcp_server.draw_files(EMAIL, "auto", "../../outside", tmp, png=False)
            for f in result["files"]:
                self.assertEqual(os.path.dirname(f), tmp)
            self.assertIn("0 layout problem(s)", result["text"])
            self.assertIn("What the picture says:", result["text"])

    def test_bad_input_names_the_place(self):
        with self.assertRaises(ValueError) as caught:
            mcp_server.build('{"title": "t", "columns": [[{"title": "A", "tiles": [{"label": "x", "colour": 1}]}]]}')
        self.assertIn("columns[0][0].tiles[0]", str(caught.exception))
        with self.assertRaises(ValueError):
            mcp_server.build("x" * (mcp_server.MAX_SOURCE + 1))

    def test_nothing_is_printed_to_stdout(self):
        import contextlib
        import io
        out = io.StringIO()
        with tempfile.TemporaryDirectory() as tmp, contextlib.redirect_stdout(out):
            mcp_server.draw_files(SIGNUP, "mermaid", "flow", tmp, png=True)
        self.assertEqual(out.getvalue(), "")


@unittest.skipUnless(HAVE_MCP, "MCP toolkit not installed")
class ServerTests(unittest.IsolatedAsyncioTestCase):
    async def test_tools_over_the_protocol(self):
        from mcp import Client
        with tempfile.TemporaryDirectory() as tmp:
            async with Client(mcp_server.create_server(tmp)) as client:
                names = sorted(t.name for t in (await client.list_tools()).tools)
                self.assertEqual(names, ["check", "describe", "draw", "format_guide", "template"])
                listed = await client.call_tool("template", {})
                self.assertIn("azure_web_app", listed.content[0].text)
                etl = await client.call_tool("template", {"name": "aws_etl"})
                checked = await client.call_tool("check", {"source": etl.content[0].text})
                self.assertEqual(checked.content[0].text, "0 layout problem(s)")
                guide = await client.call_tool("format_guide", {})
                self.assertIn('"columns"', guide.content[0].text)
                checked = await client.call_tool("check", {"source": EMAIL})
                self.assertEqual(checked.content[0].text, "0 layout problem(s)")
                described = await client.call_tool("describe", {"source": SIGNUP})
                self.assertIn("Set up profile (being built)", described.content[0].text)
                drawn = await client.call_tool("draw", {"source": SIGNUP, "name": "signup"})
                self.assertFalse(drawn.is_error)
                self.assertIn("0 layout problem(s)", drawn.content[0].text)
                self.assertTrue(os.path.exists(os.path.join(tmp, "signup.svg")))
                if os.path.exists(os.path.join(tmp, "signup.png")):
                    self.assertEqual(drawn.content[1].type, "image")
                bad = await client.call_tool("check", {"source": '{"title": "t", "columns": [[{"title": "A", "tile": []}]]}'})
                self.assertTrue(bad.is_error)
                self.assertIn("unknown key(s) 'tile'", bad.content[0].text)

    async def test_stdio_like_an_app_starts_it(self):
        from mcp import Client, StdioServerParameters
        with tempfile.TemporaryDirectory() as tmp:
            params = StdioServerParameters(command=sys.executable,
                                           args=["-m", "open_diagram.mcp_server", "--out", tmp],
                                           env={**os.environ, "PYTHONPATH": os.path.join(ROOT, "src")})
            async with Client(params) as client:
                drawn = await client.call_tool("draw", {"source": EMAIL, "name": "email", "picture": False})
                self.assertFalse(drawn.is_error)
                self.assertIn("0 layout problem(s)", drawn.content[0].text)
                self.assertTrue(os.path.exists(os.path.join(tmp, "email.svg")))


if __name__ == "__main__":
    unittest.main()
