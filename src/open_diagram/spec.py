"""Build a Diagram from plain data (JSON), so any agent or language can describe a picture without writing Python.

    {
      "title": "How an email is delivered",
      "columns": [[{"id": "app", "title": "Mail app", "tiles": ["Compose", "Send"]}],
                  [{"id": "out", "title": "Outgoing server", "tiles": ["Queue", {"label": "Signing", "status": "building"}]}]],
      "links": [{"from": "app", "to": "out"}]
    }

Cloud resources use "resources" (each with x and y) and "enclosures" (boxes around resources, nested from the inside
out). An icon is a name inside an icon folder, such as "aws/s3"; the built-in folder holds the templates' icons.

Every mistake raises SpecError with the place it happened, for example `columns[1][0].tiles[1]: unknown key 'colour'`.
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional, Sequence

from . import catalog
from .blocks import Card, Graph, Note, Panel, Resource, Row, Text, Tile, Tiles
from .diagram import ROUTINGS, Diagram
from .theme import Status, Theme


class SpecError(ValueError):
    """A problem in a diagram description, naming where it is."""


TOP_KEYS = {"title", "subtitle", "tag", "note", "steps", "steps_label", "legend", "theme", "columns", "panels", "ring",
            "center", "gap", "row_gap", "valign", "start_angle", "groups", "links", "statuses", "resources",
            "enclosures", "routing"}
LAYOUTS = ("columns", "panels", "ring")
PANEL_KEYS = {"id", "title", "sub", "status", "step", "footer", "tone", "width", "tiles", "cols", "label", "sections",
              "x", "y"}
TILE_KEYS = {"label", "sub", "status", "icon"}
RESOURCE_KEYS = {"id", "label", "sub", "icon", "icon_size", "max_width", "border", "x", "y"}
ENCLOSURE_KEYS = {"id", "label", "members", "sub", "pad", "border", "fill", "stroke", "style", "tone"}
LINK_KEYS = {"from", "to", "kind", "label", "start", "end", "lane", "via_x", "via_y", "cross_ok", "dash", "routing"}
GROUP_KEYS = {"label", "members", "sub"}


def _keys(obj: Any, allowed: set, where: str, required: tuple = ()) -> None:
    if not isinstance(obj, dict):
        raise SpecError(f"{where}: expected an object, got {type(obj).__name__}")
    extra = sorted(set(obj) - allowed)
    if extra:
        raise SpecError(f"{where}: unknown key(s) {', '.join(map(repr, extra))}; allowed: {', '.join(sorted(allowed))}")
    for key in required:
        if key not in obj:
            raise SpecError(f"{where}: missing required key '{key}'")


def default_icons() -> List[str]:
    """The icon folders a description can use when none are given: the built-in one."""
    return [catalog.icon_dir()]


def _icon(name: Any, where: str, icons: Optional[Sequence[str]]) -> str:
    folders = default_icons() if icons is None else list(icons)
    if not isinstance(name, str) or not name.strip():
        raise SpecError(f"{where}: an icon is a name inside an icon folder, such as 'aws/s3'")
    found = catalog.find_icon(name, folders)
    if found:
        return found
    if name.startswith(("/", "\\")) or ":" in name or ".." in name.replace("\\", "/").split("/"):
        raise SpecError(f"{where}: icon {name!r} must be a name inside an icon folder, such as 'aws/s3'; "
                        "full paths and '..' are not allowed")
    known = [n for f in folders for n in catalog.icon_names(f)][:40]
    hint = f"; icons available: {', '.join(known)}" if known else "; no icon folder holds any icons"
    raise SpecError(f"{where}: no icon named {name!r}{hint}")


def _tile(item: Any, where: str, icons=None) -> Tile:
    if isinstance(item, str):
        return Tile(item)
    _keys(item, TILE_KEYS, where, ("label",))
    icon = _icon(item["icon"], f"{where}.icon", icons) if "icon" in item else None
    return Tile(item["label"], sub=item.get("sub"), status=item.get("status"), icon=icon)


def _tiles(items: Any, where: str, cols=None, label=None, icons=None) -> Tiles:
    if not isinstance(items, list) or not items:
        raise SpecError(f"{where}: tiles must be a non-empty list")
    return Tiles([_tile(i, f"{where}[{n}]", icons) for n, i in enumerate(items)], cols=cols, label=label)


def _card(c: Any, where: str) -> Card:
    _keys(c, {"title", "rows", "intro"}, where, ("title", "rows"))
    rows = c["rows"]
    if not isinstance(rows, list):
        raise SpecError(f"{where}.rows: expected a list of [name, value] pairs")
    for n, row in enumerate(rows):
        if not isinstance(row, list) or len(row) != 2:
            got = f"{len(row)} item(s)" if isinstance(row, list) else f"a {type(row).__name__}"
            raise SpecError(f"{where}.rows[{n}]: each row is [name, value]; got {got}")
        if not all(isinstance(v, str) for v in row):
            raise SpecError(f"{where}.rows[{n}]: the name and the value must both be text; put numbers in quotes")
    return Card(c["title"], [tuple(r) for r in rows], intro=c.get("intro"))


def _graph(g: Any, where: str) -> Graph:
    _keys(g, {"nodes", "links", "at"}, where, ("nodes", "links", "at"))
    nodes, links, at = g["nodes"], g["links"], g["at"]
    if isinstance(nodes, list) and all(isinstance(x, list) and len(x) == 2 for x in nodes):
        nodes = dict(nodes)                         # [[key, label], ...] worked before, so it still does
    if not isinstance(nodes, dict) or not nodes:
        raise SpecError(f"{where}.nodes: expected an object of node keys and labels, such as {{\"a\": \"Login\"}}")
    if not isinstance(at, dict):
        raise SpecError(f"{where}.at: expected an object giving each node [column, row], such as {{\"a\": [0, 0]}}")
    for key in nodes:
        if key not in at:
            raise SpecError(f"{where}.at: no position for node '{key}'; give it [column, row]")
    for key, value in at.items():
        if not (isinstance(value, list) and len(value) == 2
                and all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in value)):
            raise SpecError(f"{where}.at.{key}: expected [column, row], two numbers")
    if not isinstance(links, list):
        raise SpecError(f"{where}.links: expected a list of [from, to] or [from, to, label]")
    for n, link in enumerate(links):
        if not (isinstance(link, list) and len(link) in (2, 3)):
            raise SpecError(f"{where}.links[{n}]: each link is [from, to] or [from, to, label]")
        for end in link[:2]:
            if end not in nodes:
                raise SpecError(f"{where}.links[{n}]: no node '{end}'; nodes: {', '.join(nodes)}")
    return Graph(nodes, [tuple(x) for x in links], {k: tuple(v) for k, v in at.items()})


def _section(obj: Any, where: str, icons=None):
    if isinstance(obj, list):
        return _tiles(obj, where, icons=icons)
    if isinstance(obj, str):
        return Text(obj)
    if not isinstance(obj, dict):
        raise SpecError(f"{where}: a section is a list of tiles, a string, or an object")
    if "tiles" in obj:
        _keys(obj, {"tiles", "cols", "label"}, where)
        return _tiles(obj["tiles"], f"{where}.tiles", obj.get("cols"), obj.get("label"), icons)
    if "text" in obj:
        _keys(obj, {"text"}, where)
        return Text(obj["text"])
    if "card" in obj:
        _keys(obj, {"card"}, where)
        return _card(obj["card"], f"{where}.card")
    if "graph" in obj:
        _keys(obj, {"graph"}, where)
        return _graph(obj["graph"], f"{where}.graph")
    if "row" in obj:
        _keys(obj, {"row"}, where)
        return Row(*[_section(s, f"{where}.row[{n}]", icons) for n, s in enumerate(obj["row"])])
    raise SpecError(f"{where}: a section needs one of 'tiles', 'text', 'card', 'graph' or 'row'")


def panel_from_spec(obj: Any, where: str = "panel", icons: Optional[Sequence[str]] = None) -> Panel:
    """Build one Panel from its JSON object (the same keys as in a full description). Public, for scripts that
    place panels themselves. icons: the folders tile icons are looked up in (default: the built-in folder)."""
    _keys(obj, PANEL_KEYS, where, ("title",))
    body = []
    if "tiles" in obj:
        body.append(_tiles(obj["tiles"], f"{where}.tiles", obj.get("cols"), obj.get("label"), icons))
    body += [_section(s, f"{where}.sections[{n}]", icons) for n, s in enumerate(obj.get("sections", []))]
    return Panel(obj["title"], *body, sub=obj.get("sub"), status=obj.get("status"), step=obj.get("step"),
                 footer=obj.get("footer"), tone=obj.get("tone", "default"), width=obj.get("width"),
                 name=obj.get("id") or obj["title"])


def theme_from_spec(obj: Any) -> Theme:
    """Build a Theme from the JSON "theme" object. Public, for scripts that place panels themselves."""
    t = Theme()
    if obj is None:
        return t
    if not isinstance(obj, dict):
        raise SpecError("theme: expected an object")
    for key, value in obj.items():
        if key == "tones":
            t.tones.update(value)
        elif key == "statuses":
            for name, s in value.items():
                _keys(s, {"label", "stroke", "fill", "dash"}, f"theme.statuses.{name}", ("label", "stroke", "fill"))
                t.statuses[name] = Status(**s)
        elif hasattr(t, key) and not callable(getattr(t, key)):
            setattr(t, key, value)
        else:
            raise SpecError(f"theme: unknown setting '{key}'")
    return t


_panel = panel_from_spec        # older names, kept for scripts that already use them
_theme = theme_from_spec


def _resource(obj: Any, where: str, icons) -> Resource:
    _keys(obj, RESOURCE_KEYS, where, ("label", "x", "y"))
    if not all(isinstance(obj.get(k), (int, float)) for k in ("x", "y")):
        raise SpecError(f"{where}: each resource needs numbers for x and y (its top-left corner, in pixels)")
    icon = _icon(obj["icon"], f"{where}.icon", icons) if "icon" in obj else None
    try:
        return Resource(obj["label"], icon=icon, sub=obj.get("sub"), icon_size=obj.get("icon_size", 64),
                        max_width=obj.get("max_width", 180), border=obj.get("border"),
                        name=obj.get("id") or obj["label"])
    except ValueError as e:
        raise SpecError(f"{where}: {e}") from None


def from_spec(spec: Dict[str, Any], icons: Optional[Sequence[str]] = None) -> Diagram:
    """Build a Diagram from a dict (parsed JSON). Raises SpecError naming the place of any mistake.

    icons: the folders icon names are looked up in, in order (default: the built-in icon folder only)."""
    _keys(spec, TOP_KEYS, "diagram", ("title",))
    chosen = [k for k in LAYOUTS if k in spec]
    if "resources" in spec and chosen and chosen != ["panels"]:
        raise SpecError(f"resources: each resource is placed with x and y, so they work alone or with the 'panels' "
                        f"layout, not with '{chosen[0]}'")
    if len(chosen) > 1 or (not chosen and "resources" not in spec):
        raise SpecError("diagram: give exactly one layout: 'columns' (left to right), 'panels' (each with x and y) "
                        "or 'ring' (around a circle); cloud resources use 'resources', each with x and y"
                        + (f"; got {', '.join(chosen)}" if chosen else ""))
    layout = chosen[0] if chosen else "resources"
    note = None
    if spec.get("note"):
        n = spec["note"]
        _keys(n, {"title", "lines"}, "note", ("title",))
        note = Note(n["title"], *n.get("lines", []))
    routing = spec.get("routing", "curved")
    if routing not in ROUTINGS:
        raise SpecError(f"routing: use 'curved' or 'orthogonal' (straight runs that meet at right angles), "
                        f"not {routing!r}")
    d = Diagram(spec["title"], subtitle=spec.get("subtitle"), tag=spec.get("tag"), note=note,
                theme=theme_from_spec(spec.get("theme")), legend=spec.get("legend", True),
                steps=[tuple(s) for s in spec.get("steps", [])], steps_label=spec.get("steps_label", "Steps"),
                routing=routing)
    if "center" in spec and layout != "ring":
        raise SpecError("center: only works with the 'ring' layout")

    def plain(obj, where):
        if isinstance(obj, dict) and ("x" in obj or "y" in obj):
            raise SpecError(f"{where}: x and y only work in the 'panels' layout")
        return panel_from_spec(obj, where, icons)

    placed = []
    if layout != "resources":
        items = spec[layout]
        if not isinstance(items, list) or not items:
            raise SpecError(f"{layout}: expected a non-empty list")
    if layout == "columns":
        panels = [[plain(p, f"columns[{i}][{j}]") for j, p in enumerate(col if isinstance(col, list) else [col])]
                  for i, col in enumerate(items)]
        placed = [p for col in d.columns(panels, gap=spec.get("gap"), row_gap=spec.get("row_gap"),
                                         valign=spec.get("valign", "center")) for p in col]
    elif layout == "panels":
        for n, obj in enumerate(items):
            where = f"panels[{n}]"
            if not isinstance(obj, dict) or not all(isinstance(obj.get(k), (int, float)) for k in ("x", "y")):
                raise SpecError(f"{where}: each panel needs numbers for x and y (its top-left corner, in pixels)")
            placed.append(d.add(panel_from_spec(obj, where, icons), obj["x"], obj["y"]))
    elif layout == "ring":
        middle = spec.get("center", [])
        if not isinstance(middle, list):
            raise SpecError("center: expected a list of panels")
        around, inside = d.ring([plain(p, f"ring[{n}]") for n, p in enumerate(items)], gap=spec.get("gap"),
                                start_angle=spec.get("start_angle", -90.0),
                                center=[plain(p, f"center[{n}]") for n, p in enumerate(middle)])
        placed = around + inside
    by_id = {p.name: p for p in placed}
    if "resources" in spec:
        res = spec["resources"]
        if not isinstance(res, list) or not res:
            raise SpecError("resources: expected a non-empty list")
        for n, obj in enumerate(res):
            where = f"resources[{n}]"
            r = _resource(obj, where, icons)
            if r.name in by_id:
                raise SpecError(f"{where}.id: '{r.name}' is already used; give each resource its own id")
            by_id[r.name] = d.add(r, obj["x"], obj["y"])
            placed.append(by_id[r.name])

    def find(name, where):
        if name not in by_id:
            kind = "panel or resource" if "resources" in spec else "panel"
            raise SpecError(f"{where}: no {kind} with id '{name}'; ids: {', '.join(by_id)}")
        return by_id[name]

    for n, g in enumerate(spec.get("groups", [])):
        _keys(g, GROUP_KEYS, f"groups[{n}]", ("label", "members"))
        d.group(g["label"], [find(m, f"groups[{n}].members") for m in g["members"]], sub=g.get("sub"))

    boxes = {}
    later = {e.get("id") or e.get("label") for e in spec.get("enclosures", []) if isinstance(e, dict)}
    for n, e in enumerate(spec.get("enclosures", [])):
        where = f"enclosures[{n}]"
        _keys(e, ENCLOSURE_KEYS, where, ("label", "members"))
        if not isinstance(e["members"], list) or not e["members"]:
            raise SpecError(f"{where}.members: expected a non-empty list of resource, panel or enclosure ids")
        members = []
        for m in e["members"]:
            if m in boxes:
                members.append(boxes[m])
            elif m in by_id:
                members.append(by_id[m])
            elif m in later:
                raise SpecError(f"{where}.members: enclosure '{m}' is listed after this one; list enclosures from "
                                "the inside out, so each one comes before the enclosures that hold it")
            else:
                raise SpecError(f"{where}.members: no resource, panel or enclosure with id '{m}'; "
                                f"ids: {', '.join(list(by_id) + list(boxes))}")
        key = e.get("id") or e["label"]
        if key in boxes or key in by_id:
            raise SpecError(f"{where}.id: '{key}' is already used; give each enclosure its own id")
        try:
            boxes[key] = d.enclosure(e["label"], members, sub=e.get("sub"), pad=e.get("pad", 24),
                                     border=e.get("border", "dashed"), fill=e.get("fill"), stroke=e.get("stroke"),
                                     style=e.get("style", "outline"), tone=e.get("tone", "default"))
        except (KeyError, ValueError) as err:
            raise SpecError(f"{where}: {err}") from None

    top = min(p.y for p in placed)
    bottom = max(p.bottom for p in placed)
    default_sides = ("right", "left") if layout == "columns" else ("auto", "auto")
    lanes = {"top": 0, "bottom": 0}
    for n, link in enumerate(spec.get("links", [])):
        where = f"links[{n}]"
        _keys(link, LINK_KEYS, where, ("from", "to"))
        a, b = find(link["from"], f"{where}.from"), find(link["to"], f"{where}.to")
        start, end = link.get("start", default_sides[0]), link.get("end", default_sides[1])
        via_y = link.get("via_y")
        lane = link.get("lane")
        if lane is not None:
            if lane not in lanes:
                raise SpecError(f"{where}.lane: use 'top' or 'bottom'")
            k = lanes[lane]
            lanes[lane] += 1
            via_y = top - 70 - 30 * k if lane == "top" else bottom + 44 + 30 * k
            start, end = link.get("start", lane), link.get("end", lane)
        try:
            d.link(a, b, kind=link.get("kind", "flow"), label=link.get("label"), start=start, end=end,
                   via_x=link.get("via_x"), via_y=via_y, cross_ok=link.get("cross_ok", False), dash=link.get("dash"),
                   routing=link.get("routing"))
        except (TypeError, ValueError) as e:
            raise SpecError(f"{where}: {e}") from None
    if spec.get("statuses"):
        d.set_statuses(spec["statuses"])
    return d


def load_spec(path: str, icons: Optional[Sequence[str]] = None) -> Diagram:
    """Read a JSON description from a file. Icon names are looked up next to the file, then in each folder in icons,
    then in the built-in icon folder."""
    with open(path, encoding="utf-8") as fh:
        try:
            data = json.load(fh)
        except json.JSONDecodeError as e:
            raise SpecError(f"{path}: not valid JSON ({e})") from None
    folders = [os.path.dirname(os.path.abspath(path))] + list(icons or []) + default_icons()
    return from_spec(data, icons=folders)
