# Mermaid

Draw a Mermaid flowchart you already have, and see what changes.

open-diagram lays the flowchart out again, with the same measuring and checks as any other diagram:

```bash
open-diagram draw signup_flow.mmd
```

![A Mermaid flowchart drawn by open-diagram](https://raw.githubusercontent.com/lukendeasy/open-diagram/main/docs/images/signup_flow.png)

It reads `flowchart` and `graph` in any direction, nodes of any bracket shape, chains, `&`, edge labels, and front-matter titles. Dotted edges (`-.->`) become planned connections. Each top-level `subgraph` becomes a shaded group with its own band, so groups never cover other nodes. A class named like a state (`A:::building`, or `class A,B planned`) sets that state. Lines that skip a step or point backwards travel above or below the picture. From Python, use `from_mermaid(text)`. The example is [`examples/signup_flow.mmd`](https://github.com/lukendeasy/open-diagram/blob/main/examples/signup_flow.mmd).

## What carries over

- `flowchart` and `graph`, with `LR`, `RL`, `TD`, `TB` or `BT`. `RL` and `BT` are drawn as the mirror image of `LR` and `TD`.
- Nodes in any bracket shape, with or without quotes.
- Chains (`A --> B --> C`) and `&` (`A & B --> C`).
- Line labels: `-->|text|`, `-- text -->`, `-. text .->` and `== text ==>`.
- Dotted lines (`-.->`) become connections still to build, drawn dotted.
- Each top-level `subgraph` … `end` becomes a shaded group.
- A class named after a state sets that state: `A:::building` or `class A,B planned`. The states are live, building, trial, planned and retiring.
- A `title:` in the front matter. Without one the title is “Flowchart”, and `--title` sets it.
- Mermaid's `curve` setting. `step`, `stepBefore` and `stepAfter` draw right-angle lines; any other curve draws smooth curves. It is read from the front matter (`config:` › `flowchart:` › `curve: step`) or from a `%%{init: {"flowchart": {"curve": "step"}}}%%` line. From Python, `from_mermaid(text, routing="orthogonal")` does the same.
- `%%` comments, and `;` between statements.

## What changes

- Every node is drawn as the same box. Diamonds, circles and other shapes are not kept.
- `<br/>` becomes a space, so a label written on several lines is drawn as one line, wrapped to fit.
- Thick lines (`==>`), lines with no arrowhead (`---`), circle and cross ends (`--o`, `--x`) and two-way arrows (`<-->`) are all drawn as ordinary one-way arrows.
- A subgraph inside another subgraph is merged into the outer one.
- Class names that are not states are ignored, and so are styling lines: `classDef`, `style`, `linkStyle`, `click` and `direction`.
- Markdown strings and icons such as `fa:fa-car` are shown exactly as typed.
- open-diagram chooses the layout. Boxes go in steps by their longest path, and lines that skip a step or point backwards run in a lane above or below the picture.

## What it does not read

- Other Mermaid diagram types, such as `sequenceDiagram`. The command stops and names the line.
- The newer shape syntax, `A@{ shape: … }`. The command stops and names the node.
- D2 files. open-diagram has no D2 reader.
