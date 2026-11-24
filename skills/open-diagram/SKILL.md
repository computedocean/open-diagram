---
name: open-diagram
description: Draw architecture diagrams, systems maps, layered stacks, data flows, cycles, cloud resource diagrams and concept maps as SVG and PNG with the open-diagram library, which measures every label and names each layout problem. Use when asked for an architecture diagram, systems map, stack picture, data flow, cloud architecture picture, "what is live and what is planned" picture, or concept map that should look finished on the first pass.
---

# open-diagram

open-diagram turns a short description (JSON, Mermaid, or a Python script) into a finished diagram. It measures every label from the font, places the blocks, and checks the layout. Each problem comes back as a plain sentence that names the parts involved, so you can fix it without looking at the picture. Follow these steps in order.

## 1. Pick the route

- **MCP tools available** (`format_guide`, `check`, `draw`, `describe`, `template`): read `format_guide` once, write the diagram as JSON, call `check` until it reports 0 problems, then `draw` and look at the picture it returns. Skip to step 5. For a cloud picture, call `template` first and start from the closest one; `format_guide` ends with the icon names you can use.
- **Otherwise** run `python3 -c "import open_diagram; print(open_diagram.__version__)"`. If it fails or prints below 0.5.0, run `pip install -U open-diagram`. Version 0.4.0 or later is needed for rings, free placement and `auto` sides; 0.5.0 or later for `Resource`, `d.enclosure()` and link `dash`; 0.6.0 or later for resources, enclosures and icons in JSON, and for templates. PNG output needs Chrome, Chromium or Edge; set `CHROME` to its path if it is not found. The SVG is always written.
- **Format.** Write JSON unless the picture needs something only Python offers (a `Card`, `Graph`, `Row`, or computed positions). Given a Mermaid flowchart, run `open-diagram draw flow.mmd` directly; dotted edges become planned connections and subgraphs become groups.

## 2. Plan before writing

Write the plan in a few lines first. Use only facts the user gave. Never invent systems, owners, numbers or statuses; if a fact the picture needs is missing, ask, or write "Owner: Not yet named" when owner lines are wanted but no owner was named.

- **Layout.** `columns` for flows, read left to right (where things come from, what handles them, who uses the result) or top to bottom for layers. `ring` for cycles, with goals or shared parts in `center`. `panels` with an `x` and `y` for any other shape.
- **Columns.** Three to six columns, each holding one to three panels. Avoid long lines between distant panels: place the two side by side, or route through a lane.
- **Panels.** One panel per system or team, titled in two to four words. Add a `sub` line only when it adds a fact.
- **Tiles.** Up to about nine per panel, labels of four words or fewer. Put detail in `sub`.
- **Statuses.** Only if the user cares about state: `live`, `building`, `trial`, `planned`, `retiring`.
- **Lines.** Only the flows that matter. `kind="planned"` for connections still to build. A line that must jump past a column goes through a lane (`"lane": "top"` in JSON, `via_y` in Python). Lines are curved by default; when the user asks for straight, square or right-angle lines, set `"routing": "orthogonal"` (JSON) or `Diagram(..., routing="orthogonal")` (Python).
- **Extras.** Steps, owners (`footer="Owner: ..."`), groups and a `Note` only when the user's material supports them.

## 3. Write it

**JSON** (run `open-diagram draw plan.json`):

```json
{"title": "Order flow",
 "columns": [[{"id": "web", "title": "Website", "tiles": ["Checkout", {"label": "Wallets", "status": "planned"}]}],
             [{"id": "orders", "title": "Order service", "tiles": ["Orders", "Payments"]}],
             [{"id": "ops", "title": "Operations", "tiles": ["Warehouse", "Finance"]}]],
 "links": [{"from": "web", "to": "orders"}, {"from": "orders", "to": "ops", "label": "hourly"},
           {"from": "web", "to": "ops", "lane": "top", "kind": "planned", "label": "direct"}]}
```

Top-level keys: `title` (required); one layout of `columns`, `ring` (with optional `center`, `start_angle`) or `panels`; plus `subtitle`, `tag`, `note` (`title`, `lines`), `steps` (`[[1, "First"]]`), `steps_label`, `gap`, `row_gap`, `valign`, `groups`, `links`, `statuses`, `theme`, `routing` (`curved` or `orthogonal`). Panel keys: `title` (required), `id`, `sub`, `status`, `step`, `footer`, `tone`, `width`, `x`/`y` (in `panels` only), `tiles` with `cols` and `label`, or `sections`. Link keys: `from`, `to`, `kind`, `label`, `start`, `end` (a side or `auto`), `lane`, `via_x`, `via_y`, `cross_ok`, `dash` (`solid`, `dashed` or `dotted`), `routing`.

**Python** (keep all words in lists at the top; build in a `build()` that returns the `Diagram`):

```python
from open_diagram import Diagram, Note, Panel, Tile, Tiles

def build():
    d = Diagram("Title in plain words", subtitle="Optional one-line scope", tag="DRAFT",
                note=Note("Draft", "Version 2, for review."),
                steps=[(1, "First change"), (2, "Second change")], steps_label="Rollout")
    (src,), (core, store), (apps,) = d.columns([
        [Panel("Sources", Tiles(["App", "Website", Tile("Kiosks", status="retiring")], cols=2),
               footer="Owner: Digital team")],
        [Panel("Core service", ["Orders", Tile("Fraud checks", status="building")], step=1),
         Panel("Data store", ["Main database", Tile("Event log", status="planned")], step=2, status="planned")],
        [Panel("Teams who use it", Tiles(["Finance", "Service"], cols=1), tone="neutral")],
    ], gap=88, row_gap=40)
    d.group("Platform", [core, store], sub="Run by the platform team")
    d.link(src, core)
    d.link(core, store, start="bottom", end="top")
    d.link(store, apps, kind="planned", label="nightly")
    d.link(src, apps, start="top", end="top", via_y=min(p.y for p in d.placed) - 80, label="direct today")
    return d

if __name__ == "__main__":
    build().save("out/picture")
```

A cycle as a ring:

```python
ring, (goal,) = d.ring([Panel("Plan", ["Scope"]), Panel("Build", ["Code"]), Panel("Ship", ["Release"])],
                       center=[Panel("Goals", ["Fewer bugs"], tone="neutral")])
for a, b in zip(ring, ring[1:] + ring[:1]):
    d.link(a, b, start="auto", end="auto")
```

**Cloud resources.** Start from a [cloud template](../../templates/README.md): `open-diagram new` lists them (AWS data ingestion, AWS account and network, Azure web app, Google Cloud event pipeline) and `open-diagram new NAME` writes one as JSON; keep its shape, replace each `label`, keep each `sub` (the service name under the icon). In JSON a resource is `{"id", "label", "sub", "icon": "aws/s3", "x", "y"}` and an enclosure is `{"id", "label", "members", "border"}`, listed from the inside out; icon names come from the built-in icons or a folder given with `--icons`. For services without a built-in icon, load the companion [cloud-icons skill](../cloud-icons/SKILL.md): it downloads each service's icon from the lists in [`cloud-icons/`](../../cloud-icons/). In Python:

```python
from open_diagram import Diagram, Resource, Theme

d = Diagram("Upload flow", theme=Theme(link_labels={"flow": "Data", "control": "Task control"}))
api = d.add(Resource("Upload API", sub="AWS Lambda", icon="icons/lambda.svg"))
raw = d.right_of(api, Resource("Raw files", sub="Amazon S3", icon="icons/s3.svg"))
d.link(api, raw, label="objects")
work = d.enclosure("Processing", [api], border="dashed")
d.enclosure("Cloud account", [work, raw], border="solid", pad=40)
```

- `Resource(label, sub=, icon=, icon_size=64)` is one service with a large icon and its name underneath. Lines attach to the icon. A missing icon file raises an error that names it.
- `d.enclosure(label, members, border=)` draws an account, network, subnet or other boundary around resources, and one enclosure can contain another. `border` is `solid`, `dashed` or `dotted`. Add `style="panel", tone="accent"` for a filled header with the panel's sloped lid.
- A border style says nothing about whether a part is live or planned; use statuses for that. For job orchestration, give the line its own kind with `dash="dashed"` (for example `kind="control"`) and name that kind in `Theme(link_labels=...)`, so the key explains it.
- For a small icon beside a tile label inside a panel, use `Tile(label, icon=...)`.

Other blocks: `Card(title, [(name, value), ...], intro=)` for a worked example; `Graph(nodes, links, at)` for a map of things and links, with `at` giving each node a `(column, row)`; `Row(a, b)` to put sections side by side; `Text(...)` for a short paragraph. Placing: `add(block, x, y)`, `right_of(ref, block, align=)`, `below(ref, block)`, `stack([...])`, `columns([[...], ...])`, `ring([...], center=[...])`. Tones: `neutral`, `accent` (soft yellow header), `dark` (charcoal header).

## 4. Run it and fix every named problem

Run `open-diagram check FILE` (works for `.json`, `.mmd` and `.py`) or run the script; `save()` writes the files, prints a summary, then raises `LayoutError` listing every problem. Fix them all and run again until it says `0 layout problem(s)`.

| Message contains | Fix |
| --- | --- |
| `overlap` or `px apart` | Move one block, raise `gap` or `row_gap`, or place it with `right_of()` / `below()` |
| `crosses` | Route the line through a lane (`lane`, `via_y` or `via_x`), change `start` and `end` sides, or move a block. Use `cross_ok` only when the line should pass behind |
| `label ... sits on` | Shorten the label, or widen the gap between the two columns |
| `facing away` | Use `start="auto", end="auto"`, choose other sides, or route the line through a lane |
| `sits on the title of group` | Give the line a different start or end side, route it through a lane, or move the group's blocks |
| `group ... overlaps` | Add the block to the group, or move it out of the group's area |
| `graph: the label ... touches` | Spread the nodes in `at`, or shorten the label |
| `graph: the line ... runs through` | Move a node so the straight line between the pair is clear |
| `needs N px` | Give the block more width, or shorten the words |
| `smallest text` | Do not shrink text below the theme minimum; shorten the words instead |

JSON and Mermaid mistakes name their place (`columns[1][0].tiles[2]`, `line 7`); fix that spot.

## 5. Check the picture before answering

Run `open-diagram describe FILE` (or `d.describe()`) and compare the text with the request: every system, state, owner and line the user named is there, and nothing they did not name. Then open the PNG and check it as a reader would:

- The reading direction is obvious and the main flow has few bends.
- No line is ambiguous where it meets a panel.
- The key matches what the picture uses.
- Every word is one the user would use, and no placeholder text is left.

Tell the user where the SVG and PNG are, and say which facts in the picture are your assumptions.

## Keeping diagrams current

Keep states in a small file such as `{"Fraud checks": "live", "Parcel lockers": "building"}` and draw with `--statuses states.json` (or `d.set_statuses(...)`). Names match panel titles, panel ids and tile labels. When work ships, change one word and redraw.

## Soundtrack

We recommend listening to music by [The Gathering Field](https://open.spotify.com/artist/0BfQ8COB7K647uB6a0kMZn) while you build.
