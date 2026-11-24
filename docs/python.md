# Python

Build a diagram from blocks, place them, and set its colors and sizes with a theme.

## Building blocks

| Block | What it draws |
| --- | --- |
| `Panel(title, *sections, sub=, status=, step=, footer=, tone=)` | The main box: a colored header, sections stacked inside, an optional footer such as "Owner: Data team" |
| `Tiles(items, cols=, label=)` | A grid of tiles with one cell size. A plain list of labels inside a `Panel` becomes `Tiles` |
| `Tile(label, sub=, status=, icon=)` | One small box. `icon` takes a PNG or SVG file you supply; for AWS, Azure and Google Cloud, see [Cloud service icons](agents.md#cloud-service-icons) |
| `Resource(label, icon=, sub=, icon_size=64, border=)` | A standalone cloud resource: large icon above its workload label and service name, with no panel or raised tile |
| `Card(title, rows, intro=)` | A worked example: rows of name and value |
| `Graph(nodes, links, at)` | Things on a grid, joined by labelled lines. The build reports labels that touch nodes |
| `Row(*sections)` | Sections side by side inside a panel |
| `Text(text)` | A wrapped paragraph |
| `Note(title, *lines)` | A boxed note for the top right, such as "Draft" |

| Diagram method | What it does |
| --- | --- |
| `Diagram(title, subtitle=, tag=, note=, theme=, legend=, steps=, routing=)` | Start a picture. `routing="orthogonal"` draws every line as straight runs that meet at right angles; the default, `"curved"`, draws smooth curves |
| `add(block, x, y)` | Place a block at a position |
| `right_of(ref, block, align=)` and `below(ref, block, align=)` | Place a block next to another, with the theme's gap |
| `columns([[...], [...]])` and `stack([...])` | Place columns left to right, each one top to bottom |
| `ring(blocks, center=[...])` | Place blocks around a circle, with optional blocks in the middle; returns both lists |
| `group(label, members, sub=)` | A shaded, dashed area around some blocks |
| `enclosure(label, members, border=, sub=, pad=, fill=, stroke=, style=, tone=)` | A boundary around resources or nested enclosures; `style="panel"` adds the original sloped lid and a filled header; borders are `solid`, `dashed` or `dotted`, independent of deployment state |
| `link(a, b, kind=, label=, start=, end=, via_x=, via_y=, dash=, routing=)` | An arrow. `kind="planned"` is dotted. `dash` optionally overrides the stroke style. `start="auto"` and `end="auto"` pick the sides that face each other. `via_y` routes it through a lane, for example above everything. `routing` sets curved or right-angle for this line only |
| `save(path)` | Write the SVG and PNG, print a summary, raise `LayoutError` if there are problems |
| `render()` | Return the SVG text and a report without writing files |
| `describe()` | Return what the picture says in plain words |
| `set_statuses({name: state})` | Set states by panel title, id or tile label, for example from a file |

## Right-angle lines

`Diagram(..., routing="orthogonal")` draws every line as straight runs that meet at right angles, with slightly rounded corners. When two blocks face each other and their sides overlap, the line runs straight across. Lines that would share the same gap each get their own track, 12 px apart, ordered so they cross as little as possible. The layout checks work the same way for both kinds of line.

## Statuses, colors and sizes

Panels have light gray headers and yellow step numbers (charcoal instead when any panel uses the yellow `accent` header, so yellow keeps one meaning). Each panel has a sloped top and each tile a raised edge, for a light 3D look; `Theme(lid=0, depth=0)` turns it off. `tone="accent"` gives a panel a soft yellow header, and `tone="dark"` a charcoal one. Header text turns white by itself on a dark header.

Statuses are shown by color and by word: Live, Being built, In trial, Planned and Retiring. Change them, or anything else, with a `Theme`:

```python
from open_diagram import Diagram, Status, Theme

theme = Theme(tones={"default": "#2B3036", "neutral": "#6A7078", "accent": "#FFC83D", "dark": "#111418"})
theme.statuses["pilot"] = Status("Pilot", stroke="#8E24AA", fill="#F6EDF9", dash="dashed")
d = Diagram("My picture", theme=theme)
```

## The picture explains itself

`d.describe()`, or `open-diagram describe`, returns what the picture says in plain words: each block and its tiles with their states, the groups, every line and its label, and the key. The same text goes into the SVG as its description, so screen readers can read it. An agent can compare it with the request without looking at the picture.

```text
- Processing [step 1]: Upload checks; Transcoding; GPU encoding (being built); Auto captions (planned). Owner: Media team
- Video record -> Recommendations (connection to build)
```
