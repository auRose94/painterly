"""Painterly MCP server: the hand, exposed as tools.

Run: uv run --with mcp --with numpy --with pillow python src/painterly/server.py
Session dir defaults to ./sessions/mcp_live; override with PAINTERLY_SESSION_DIR.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mcp.server.fastmcp import FastMCP  # noqa: E402

from painterly.session import Session  # noqa: E402

mcp = FastMCP("painterly")
_session: Session | None = None


def _dir() -> str:
    return os.environ.get("PAINTERLY_SESSION_DIR", "sessions/mcp_live")


def session() -> Session:
    global _session
    if _session is None:
        d = _dir()
        _session = Session(d, restore=(Path(d) / "state.json").exists())
    return _session


@mcp.tool()
def prepare_session(
    paper_id: str = "hot_press",
    width_mm: float = 120.0,
    height_mm: float = 160.0,
    seed: int = 23,
    artist_id: str = "unnamed-artist-0",
    title: str = "untitled",
) -> str:
    """Begin a work: choose the surface, its size, and a title.

    Materials available — papers: plate_bristol, hot_press, cold_press, rough,
    copy_paper, newsprint. The environment offers; the artist chooses.
    """
    global _session
    _session = Session(
        _dir(),
        paper_id=paper_id,
        size_mm=(width_mm, height_mm),
        seed=seed,
        artist_id=artist_id,
        title=title,
    )
    return json.dumps({"ok": True, "session_dir": str(_session.dir), "canvas_mm": [width_mm, height_mm]})


@mcp.tool()
def select_tool(tool_id: str) -> str:
    """Pick up a tool. nibs: fineliner_03 (rigid, fine), felt_medium (soft edge),
    fountain_f (flexing, wet), ballpoint_blue (viscous, pressure-hungry)."""
    return json.dumps(session().select_tool(tool_id))


@mcp.tool()
def stroke(
    x0_mm: float,
    y0_mm: float,
    x1_mm: float,
    y1_mm: float,
    curvature: float = 0.0,
    pressure_start: float = 0.5,
    pressure_end: float = 0.5,
    speed_mm_s: float = 60.0,
    tag: str = "",
) -> str:
    """One hand motion: glide from (x0,y0) to (x1,y1), bowing perpendicular to
    the line by `curvature` (fraction of stroke length; ~0.37 bends a quarter
    circle). Pressure 0..1 at each end. Returns what the hand felt: resistance,
    skips, pooling, splay — read it before deciding the next move."""
    return json.dumps(
        session().stroke(
            x0_mm,
            y0_mm,
            x1_mm,
            y1_mm,
            curvature=curvature,
            pressure_start=pressure_start,
            pressure_end=pressure_end,
            speed_mm_s=speed_mm_s,
            tag=tag,
        )
    )


@mcp.tool()
def stroke_path(
    points_mm: list[float],
    pressure: float = 0.3,
    speed_mm_s: float = 60.0,
    tag: str = "",
) -> str:
    """One continuous hand motion through waypoints [x0,y0,x1,y1,...] — how a
    hand draws a circle or a flowing line in a single gesture. Smooth, no
    vertices at waypoints. Returns what the hand felt."""
    return json.dumps(session().stroke_path(points_mm, pressure=pressure, speed_mm_s=speed_mm_s, tag=tag))


@mcp.tool()
def guide_line(
    x0_mm: float,
    y0_mm: float,
    x1_mm: float,
    y1_mm: float,
    color: str = "red",
    opacity: float = 0.4,
    curvature: float = 0.0,
    pressure: float = 0.2,
    tag: str = "",
) -> str:
    """Lay a construction line in colored pencil (red | green | blue).
    Guides carry the same hand physics — pressure, skips, tooth. Erasable
    to a ghost with soft_erase; never fully gone."""
    return json.dumps(
        session().stroke(
            x0_mm, y0_mm, x1_mm, y1_mm,
            curvature=curvature, pressure_start=pressure, pressure_end=pressure,
            tag=tag or "guide", layer="guide", guide_color=color, guide_opacity=opacity,
        )
    )


@mcp.tool()
def soft_erase(
    x0_mm: float,
    y0_mm: float,
    x1_mm: float,
    y1_mm: float,
    width_mm: float = 3.0,
    strength: float = 0.5,
    curvature: float = 0.0,
    tag: str = "",
    pattern: str = "linear",
) -> str:
    """Drag a soft eraser along a path: grays the line, smears it a little,
    abrades the paper. Ink lifts toward a permanent ghost — never fully gone.
    Patterns: linear | scribble (left-right zigzag) | loop (overlapping
    circles, lifts from all directions). Narrow width + high strength = a
    precision rake that pulls pigment off exactly the spot."""
    return json.dumps(
        session().erase(x0_mm, y0_mm, x1_mm, y1_mm, width_mm, strength, curvature, tag, pattern)
    )


@mcp.tool()
def whiteout(
    x0_mm: float,
    y0_mm: float,
    x1_mm: float,
    y1_mm: float,
    width_mm: float = 4.0,
    strength: float = 0.9,
    curvature: float = 0.0,
    tag: str = "",
) -> str:
    """Opaque white-out (gouache) along a path: covers tone and ink fully —
    no ghost, no abrasion. The finishing step: clean paper anywhere, then
    draw or stamp on it."""
    return json.dumps(session().whiteout(x0_mm, y0_mm, x1_mm, y1_mm, width_mm, strength, curvature, tag))


@mcp.tool()
def view(name: str = "view", region_mm: list[float] | None = None, px_per_cell: int = 2) -> str:
    """Look at the work (or a region [x0,y0,x1,y1] in mm). Returns the render
    path — open it with your eyes before the next stroke."""
    region = tuple(region_mm) if region_mm else None
    return json.dumps(session().view(name, region, px_per_cell))


@mcp.tool()
def note(kind: str, text: str) -> str:
    """Sketchbook entries: reflection | attempt_boundary (rejected attempt +
    why) | artist_statement | material_choice. Rejections stay in the log —
    provenance includes the erasures."""
    return json.dumps(session().note(kind, text))


@mcp.tool()
def export_artwork(name: str = "artwork") -> str:
    """Render the print. The log remains the work."""
    return json.dumps(session().export_artwork(name))


if __name__ == "__main__":
    mcp.run()
