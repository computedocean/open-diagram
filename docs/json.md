# JSON

Describe a diagram as plain data, from any language or agent.

A small example:

```json
{
  "title": "How an email is delivered",
  "columns": [
    [{"id": "app", "title": "Mail app", "tiles": ["Write", "Send"], "cols": 1}],
    [{"id": "out", "title": "Sending server", "tiles": ["Queue", {"label": "Digital signature", "status": "building"}]}]
  ],
  "links": [{"from": "app", "to": "out"}]
}
```

![The JSON email example](https://raw.githubusercontent.com/lukendeasy/open-diagram/main/docs/images/email_delivery.png)

| Part | Keys |
| --- | --- |
| Top level | `title` (required); one layout: `columns` (a list of columns, each a list of panels), `ring` (panels around a circle, with optional `center` and `start_angle`) or `panels` (each with `x` and `y`), or `resources` (alone or with `panels`); `enclosures`; `subtitle`, `tag`, `note` (`title`, `lines`), `steps` (`[[1, "First"]]`), `steps_label`, `gap`, `row_gap`, `valign`, `groups`, `links`, `statuses`, `theme`, `routing` (`curved`, the default, or `orthogonal`: straight runs that meet at right angles) |
| Panel | `title` (required), `id`, `sub`, `status`, `step`, `footer`, `tone`, `width`, `x` and `y` (in `panels` only), `tiles` with `cols` and `label`, or `sections` (each `{"tiles": [...]}`, `{"text": "..."}`, `{"card": {...}}`, `{"graph": {...}}` or `{"row": [...]}`) |
| Tile | a string, or `{"label", "sub", "status", "icon"}` |
| Resource | a large icon with its label under it: `label`, `x` and `y` (required), `id`, `sub` (the service name), `icon`, `icon_size`, `max_width`, `border` |
| Enclosure | a box around resources, panels or other enclosures: `label` and `members` (required), `id`, `sub`, `pad`, `border` (`solid`, `dashed`, `dotted`), `style` (`outline` or `panel`), `fill`, `stroke`, `tone`; listed from the inside out |
| Icon | a name inside an icon folder, such as `aws/s3`: the built-in icons, the JSON file's own folder, or a folder given with `--icons`. Full paths and `..` are refused |
| Link | `from` and `to` (panel or resource ids), `kind` (`flow` or `planned`), `label`, `start` and `end` (a side, or `auto` for the side facing the other panel: the default in `ring` and `panels`), `lane` (`top` or `bottom`, to route around the picture), `via_x`, `via_y`, `cross_ok`, `dash` (`solid`, `dashed` or `dotted`, independent of state), `routing` (`curved` or `orthogonal`, for this link only) |
| Group | `label`, `members` (panel ids), `sub` |

Every mistake names its place, for example `columns[0][0].tiles[2]: unknown key(s) 'colour'`. From Python, use `from_spec(data)`. The full example is [`examples/email_delivery.json`](https://github.com/lukendeasy/open-diagram/blob/main/examples/email_delivery.json).

## Rings and free placement

Cycles read best as a ring. Use `"ring"` instead of `"columns"`, optionally with panels in the `"center"`; links then leave from the sides that face each other. For any other shape, use `"panels"` and give each panel an `x` and `y`. In Python, the same is `d.ring(blocks, center=[...])` and `d.add(block, x, y)`, with `link(a, b, start="auto", end="auto")`.

![A release cycle drawn with the ring layout](https://raw.githubusercontent.com/lukendeasy/open-diagram/main/docs/images/release_cycle.png)

The example is [`examples/release_cycle.json`](https://github.com/lukendeasy/open-diagram/blob/main/examples/release_cycle.json).
