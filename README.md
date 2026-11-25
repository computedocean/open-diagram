# open-diagram

Python building blocks for dense architecture diagrams that check their own layout.

<!-- mcp-name: io.github.lukendeasy/open-diagram -->

Website, gallery and docs: [open-diagram.dev](https://open-diagram.dev) · How it compares with Mermaid, D2, draw.io, Excalidraw and four other tools: [open-diagram.dev/compare.html](https://open-diagram.dev/compare.html)

![A systems map for an invented video platform, drawn with open-diagram](https://raw.githubusercontent.com/lukendeasy/open-diagram/main/docs/images/systems_map.png)

You describe panels, tiles, lines and groups in a short Python script. open-diagram measures every label from the font, places the blocks, and checks the result. If two panels collide or a line runs through a panel, the build says so by name. The output is an SVG (a picture made of shapes, sharp at any size) and a PNG.

The same blocks draw software systems, release pipelines, layered stacks, data models and business processes. It is built to be written by an AI agent such as Claude Code or Cursor, as well as by people. The checks catch layout mistakes before anyone looks at the picture, so a first attempt usually comes out clean.

## Install

```bash
pip install open-diagram
```

For the newest unreleased code: `pip install git+https://github.com/lukendeasy/open-diagram`.

open-diagram needs Python 3.10 or later. pip installs the two packages it uses, fontTools and the MCP toolkit, for you. To make PNG files it also needs Google Chrome, Chromium or Microsoft Edge. If yours is not in the usual place, set the `CHROME` environment variable to its path. The SVG is always written, browser or not.

For AI apps that use MCP, such as Claude Code: `claude mcp add open-diagram -- uvx open-diagram mcp`. Claude Desktop, Cursor, Amp, the agent skill and the apps it has been tested with are in [AI agents](https://github.com/lukendeasy/open-diagram/blob/main/docs/agents.md), with [a block to paste into your project's AGENTS.md](https://github.com/lukendeasy/open-diagram/blob/main/docs/agents.md#tell-your-coding-agent-about-open-diagram) so your coding agent knows how to draw and check a diagram.

## Quick start

```python
from open_diagram import Diagram, Panel, Tile

d = Diagram("How a search request is answered", tag="EXAMPLE")
app = d.add(Panel("Web app", ["Search box", "Results page", "Filters"], footer="Owner: Web team"))
api = d.right_of(app, Panel("Search API", [Tile("Checks access"), Tile("Caches results", status="building")],
                            footer="Owner: Platform team"), align="center")
index = d.right_of(api, Panel("Search index", ["Product text", Tile("Spelling fixes", status="planned")],
                              status="planned"), align="center")
d.link(app, api)
d.link(api, index, kind="planned", label="new")
d.save("quickstart")   # writes quickstart.svg and quickstart.png
```

![The quick start diagram](https://raw.githubusercontent.com/lukendeasy/open-diagram/main/docs/images/quickstart.png)

The key at the top lists only the statuses and line kinds the picture uses.

## Why a first attempt comes out clean

- **Every label is measured before it is placed.** Widths come from the font's own spacing and kerning, so each box fits its words.
- **The build checks the layout and names each problem.** For example: `'Storage' and 'Recommendations' are only 9 px apart (minimum 16)` or `line 'Where videos come from' -> 'Storage' crosses 'Processing'; route it with via_x/via_y, move a block, or pass cross_ok=True`. `save()` writes the files, prints a summary, then raises `LayoutError` with the full list.
- **Text is drawn as shapes.** The SVG looks the same in a browser, PowerPoint, Keynote or Figma, with or without the font installed. Inter comes bundled.
- **Words stay apart from layout.** Keep labels in lists at the top of the script. Changing a word does not move anything by hand.

![How open-diagram turns a script into a picture, drawn with open-diagram](https://raw.githubusercontent.com/lukendeasy/open-diagram/main/docs/images/how_it_works.png)

## Examples

Each example is one script in [`examples/`](https://github.com/lukendeasy/open-diagram/tree/main/examples). Run any of them with `python3 examples/<name>.py`.

| Example | Shows |
| --- | --- |
| [`systems_map.py`](https://github.com/lukendeasy/open-diagram/blob/main/examples/systems_map.py) | A video platform from upload to screen: columns, a group, steps, statuses, owners, a small data map with a worked example, and lanes above and below the picture |
| [`how_it_works.py`](https://github.com/lukendeasy/open-diagram/blob/main/examples/how_it_works.py) | How open-diagram itself works, drawn with open-diagram |
| [`pipeline.py`](https://github.com/lukendeasy/open-diagram/blob/main/examples/pipeline.py) | A release pipeline from pull request to production, with a rollback lane |
| [`card_payment.py`](https://github.com/lukendeasy/open-diagram/blob/main/examples/card_payment.py) | What happens when you tap a card: numbered steps for the order of events, return paths above and below |
| [`layers.py`](https://github.com/lukendeasy/open-diagram/blob/main/examples/layers.py) | A web product as stacked layers, with a side panel |
| [`concept_map.py`](https://github.com/lukendeasy/open-diagram/blob/main/examples/concept_map.py) | How git stores a project: its objects and links, with a worked example |
| [`smart_home.py`](https://github.com/lukendeasy/open-diagram/blob/main/examples/smart_home.py) | A smart home from sensor to phone, with a planned overnight update path |
| [`incident_response.py`](https://github.com/lukendeasy/open-diagram/blob/main/examples/incident_response.py) | How a team handles an outage, from the first alert to the lessons learned |
| [`business_map.py`](https://github.com/lukendeasy/open-diagram/blob/main/examples/business_map.py) | Not only software: a furniture store from order to doorstep |
| [`email_delivery.json`](https://github.com/lukendeasy/open-diagram/blob/main/examples/email_delivery.json) | How an email is delivered, written as JSON instead of Python |
| [`signup_flow.mmd`](https://github.com/lukendeasy/open-diagram/blob/main/examples/signup_flow.mmd) | A sign-up flow imported from a Mermaid flowchart |
| [`release_cycle.json`](https://github.com/lukendeasy/open-diagram/blob/main/examples/release_cycle.json) | A release cycle as a ring, with goals in the middle |
| [`quickstart.py`](https://github.com/lukendeasy/open-diagram/blob/main/examples/quickstart.py) | The code above |

All of them, and the cloud templates, are in the [gallery](https://open-diagram.dev/gallery.html).

## Docs

The full reference is at [open-diagram.dev/docs.html](https://open-diagram.dev/docs.html), drawn from these files:

| Topic | File |
| --- | --- |
| Python: every block, placement method and theme setting | [docs/python.md](https://github.com/lukendeasy/open-diagram/blob/main/docs/python.md) |
| JSON: every key | [docs/json.md](https://github.com/lukendeasy/open-diagram/blob/main/docs/json.md) |
| Mermaid: what it reads and what changes | [docs/mermaid.md](https://github.com/lukendeasy/open-diagram/blob/main/docs/mermaid.md) |
| Command line and the GitHub Action | [docs/cli.md](https://github.com/lukendeasy/open-diagram/blob/main/docs/cli.md) |
| AI agents: the MCP server, the agent skill and cloud icons | [docs/agents.md](https://github.com/lukendeasy/open-diagram/blob/main/docs/agents.md) |
| Cloud templates and the template standard | [templates/README.md](https://github.com/lukendeasy/open-diagram/blob/main/templates/README.md) |
| What each layout problem means and how to fix it | [skills/open-diagram/SKILL.md](https://github.com/lukendeasy/open-diagram/blob/main/skills/open-diagram/SKILL.md) |
| How it compares with Mermaid, D2, draw.io, Excalidraw and archify | [docs/comparison.md](https://github.com/lukendeasy/open-diagram/blob/main/docs/comparison.md) |

The website also has [step-by-step guides](https://open-diagram.dev/guides.html), [a page for each example and template](https://open-diagram.dev/diagrams.html), [a page for each layout problem](https://open-diagram.dev/problems.html), [comparisons with eight other tools](https://open-diagram.dev/compare.html) and [pages for AI agents](https://open-diagram.dev/for-agents.html). Each page has a Markdown copy at the same address ending in `.md`.

## Contributing

Issues and pull requests are welcome.

**To report a bug or ask for a change,** [open an issue](https://github.com/lukendeasy/open-diagram/issues). Include the script, JSON or Mermaid file that shows the problem, and the problem message or picture you got.

**To make the change yourself,** open a pull request. For a large change, such as a new block or layout, open an issue first so we can agree on the approach before you write the code.

1. Fork the repo and create a branch.
2. Make the change. [AGENTS.md](https://github.com/lukendeasy/open-diagram/blob/main/AGENTS.md) lists the commands, the rules the code must keep, and what a finished change looks like. It is written for coding agents, and people can follow it the same way.
3. Run the tests:

   ```bash
   python3 -m unittest discover -s tests
   ```

4. If your change alters a picture, rebuild the examples and commit the new SVG and PNG files with the code:

   ```bash
   for f in examples/*.py; do PYTHONPATH=src python3 "$f"; done
   ```

5. Open the pull request. Say what changed and why, and attach a picture if the change alters how diagrams look.

New examples use an invented organization, never real company names, logos or data. To add or update a cloud icon, follow "Sources, family versions and attribution" in the [cloud-icons skill](https://github.com/lukendeasy/open-diagram/blob/main/skills/cloud-icons/SKILL.md): each new address must point to a fixed version of the file and return an SVG.

Contributions are released under the MIT license, like the rest of the project.

## Contributors

- **Creator:** [Luke Deasy](https://github.com/lukendeasy)
- **Founding contributor:** [Scott Williams](https://github.com/scotttenex)

Their backgrounds are on the [About page](https://open-diagram.dev/about.html).

## Soundtrack

We recommend listening to music by [The Gathering Field](https://open.spotify.com/artist/0BfQ8COB7K647uB6a0kMZn) while you build.

## License

MIT, in [LICENSE](https://github.com/lukendeasy/open-diagram/blob/main/LICENSE). The bundled Inter font is by The Inter Project Authors, under the SIL Open Font License 1.1, in [src/open_diagram/fonts/OFL.txt](https://github.com/lukendeasy/open-diagram/blob/main/src/open_diagram/fonts/OFL.txt).
