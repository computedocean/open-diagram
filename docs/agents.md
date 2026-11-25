# AI agents

Let Claude, Cursor or Codex draw diagrams and fix their layout problems.

## MCP server

open-diagram can run as an MCP server: a small program that AI apps start on your computer, so the AI can draw diagrams as one of its own actions. Nothing is hosted and nothing leaves your computer. It accepts JSON and Mermaid only, never Python, and writes files only inside one output folder.

The commands below use [uv](https://docs.astral.sh/uv/), which fetches open-diagram and the Python it needs (3.10 or later) the first time.

**Claude Code**

```bash
claude mcp add open-diagram -- uvx open-diagram mcp
```

**Claude Desktop** (`claude_desktop_config.json`) **or Cursor** (`~/.cursor/mcp.json`)

```json
{
  "mcpServers": {
    "open-diagram": {
      "command": "uvx",
      "args": ["open-diagram", "mcp", "--out", "/Users/you/Documents/open-diagram"]
    }
  }
}
```

**Amp**

```bash
amp mcp add open-diagram -- uvx open-diagram mcp
```

Without uv: `pip install open-diagram`, then use `open-diagram` as the command and `mcp` as its first argument. Setups made before 0.6.2 with `--from "open-diagram[mcp]" open-diagram-mcp` keep working. uv keeps a copy of what it downloaded; to pick up a new release, add `--refresh` once after `uvx`.

| Action | What the AI gets |
| --- | --- |
| `format_guide` | A JSON example to copy, every key, Mermaid support, and how to fix each kind of problem |
| `check` | The layout problems, without writing files, so it can fix and retry quickly |
| `draw` | Writes the SVG and PNG, and returns the problems, the file paths, the plain-words description and the picture itself |
| `describe` | What the picture says, in plain words |
| `template` | The list of templates, or one template as JSON to start from |

Icons come only from the built-in icons and from folders you name with `--icons` (or the `OPEN_DIAGRAM_ICONS` environment variable), never from a path the AI writes. Files go to `--out`, else the `OPEN_DIAGRAM_OUT` environment variable, else an `open-diagram` folder where the app starts the server (or in your home folder if that one cannot be written).

### Tested with

Tested on November 25, 2026, with open-diagram 0.6.2 on macOS, using the setup lines above.

| App | Version | What was checked |
| --- | --- | --- |
| Claude Code | 2.1.332 | Claude called `format_guide`, `check` and `draw`; the SVG and PNG were written with 0 layout problems |
| Claude Desktop | 6.28899.6 | The app found `uvx`, started the server and received its list of actions |
| Cursor | 3.32.4 | Cursor connected and listed all 5 actions |
| Amp | 0.0.1788357228 | Amp connected and listed all 5 actions |

In Amp, a server added to one folder's settings (`amp mcp add --workspace`) also needs `amp mcp approve open-diagram`.

## Agent skill

The folder [`skills/open-diagram/`](https://github.com/lukendeasy/open-diagram/tree/main/skills/open-diagram) is an Agent Skill: instructions an agent loads when it needs them. Install it with the [skills](https://skills.sh) tool, without cloning this repo:

```bash
npx skills add lukendeasy/open-diagram --skill open-diagram --agent claude-code
```

That puts it in `.claude/skills/` in the current folder. Add `-g` to install it for all your projects, or name another app after `--agent`. In a copy of this repo you can also copy the folder yourself:

```bash
cp -r skills/open-diagram ~/.claude/skills/
```

Tested on November 25, 2026, with skills 1.9.0 and Claude Code 2.1.332: the installed file matched this repo's, and Claude Code loaded it from the folder the tool wrote.

Then ask for a picture in plain words, for example: "Draw a systems map of our checkout, warehouse and reporting, with what is live and what is planned." The skill tells the agent to plan the columns, write the script, run it, fix each named problem, and look at the PNG before it answers.

Agents changing the library itself should start with [AGENTS.md](https://github.com/lukendeasy/open-diagram/blob/main/AGENTS.md).

## Cloud service icons

The [`cloud-icons/`](https://github.com/lukendeasy/open-diagram/tree/main/cloud-icons) folder has one file each for [AWS](https://github.com/lukendeasy/open-diagram/blob/main/cloud-icons/aws.json), [Azure](https://github.com/lukendeasy/open-diagram/blob/main/cloud-icons/azure.json) and [Google Cloud](https://github.com/lukendeasy/open-diagram/blob/main/cloud-icons/gcp.json). Each file lists service keys, such as `s3` or `lambda`, with the web address of that service's SVG icon. AWS also includes `mwaa`, `glue` and `athena` for ETL diagrams. Every address points to one fixed version of the icon file, so later changes to the icon collection do not change your diagrams. A third party, theSVG, hosts the files; once downloaded, they work offline.

The [cloud-icons skill](https://github.com/lukendeasy/open-diagram/blob/main/skills/cloud-icons/SKILL.md) tells an agent how to pick icons, download them, and pass each file to `Resource(icon=...)` or `Tile(icon=...)`. The finished SVG and PNG contain the icons themselves, so you can share them without the icon links. JSON and the MCP server take icons by name (`"icon": "aws/s3"`) from the built-in icons or from a folder you add with `--icons`; Mermaid does not take icons. For Claude Code, copy the skill into your skills folder:

```bash
cp -r skills/cloud-icons ~/.claude/skills/
```

The icon lists stay in your copy of this repo. If you run the skill's example from another folder, set its `ICON_DIR` to the `cloud-icons/` folder in your copy.

The icons belong to Amazon, Microsoft and Google, and keep their own terms; this project's MIT license does not cover them. The skill links each provider's terms and says how to credit the icons when you share a diagram.
