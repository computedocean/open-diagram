# Command line

Draw, check and describe diagrams from a terminal or a CI job.

```bash
open-diagram draw plan.json       # writes plan.svg and plan.png; exits with 1 if the layout has problems
open-diagram check docs/*.json    # checks without writing files, for scripts and CI
open-diagram describe plan.json   # prints what the picture says, in plain words
open-diagram new                  # lists the templates; `open-diagram new azure_web_app` writes one to start from
open-diagram mcp                  # runs as an MCP server for AI apps; see docs/agents.md
```

Each command takes a JSON description (`.json`), a Mermaid flowchart (`.mmd` or `.mermaid`), or a Python script with a `build()` function that returns a `Diagram` (`.py`). Add `--statuses states.json` to set states by name before drawing, and `--icons FOLDER` to use your own icons in JSON.

## Keep diagrams from going stale

Add this GitHub Action and every push checks your diagrams, or redraws them, and fails if a layout problem appears:

```yaml
# .github/workflows/diagrams.yml
name: diagrams
on: [push, pull_request]
jobs:
  diagrams:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: lukendeasy/open-diagram@v0.6.2
        with:
          files: docs/diagrams/*.json docs/diagrams/*.mmd
          statuses: docs/states.json            # optional; keep it outside the folders that files matches
          mode: check                           # or draw, to write SVG and PNG next to each file
```

Keep states in a small file, such as `{"Fraud checks": "live", "Parcel lockers": "building"}`. When work ships, change one word; the pictures follow. Names match panel titles, panel ids and tile labels, and `live` returns a part to the default look. From Python, use `d.set_statuses(...)`.

Keep the states file out of the folders that `files` matches, or the Action reads it as a diagram and stops with `unknown key(s)`. One states file applies to every file in the run, so every name in it must be a part of each diagram: a name that one diagram lacks stops the run with `no panel or tile is named ...`.
