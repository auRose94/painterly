"""Artist session: the hand, the tools, the canvas, and the practice log.

Every action is logged (JSONL, append-only) so a session can be replayed,
diffed, and rendered from the log alone. State persists across processes so a
session can span many invocations — like days in a studio.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from types import SimpleNamespace

import numpy as np

from .canvas import Canvas
from .render import render
from .stroke import erase_pattern_points, execute_erase, execute_stroke, execute_whiteout, expand_path_stroke, expand_stroke
from .types import NIB_CATALOG, PAPER_CATALOG, HandState, Paper, ToolState

NOTE_KINDS = {
    "reflection",
    "attempt_boundary",
    "artist_statement",
    "material_choice",
    "derivative_work",  # disclosure: this sheet derives from existing IP
}


class Session:
    def __init__(
        self,
        dirpath: str | Path,
        *,
        paper_id: str = "hot_press",
        size_mm: tuple[float, float] = (120.0, 160.0),
        seed: int = 23,
        cell_mm: float = 0.2,
        artist_id: str = "unnamed-artist-0",
        title: str = "untitled",
        restore: bool = False,
    ) -> None:
        self.dir = Path(dirpath)
        (self.dir / "views").mkdir(parents=True, exist_ok=True)
        self.log_path = self.dir / "log.jsonl"

        if restore and (self.dir / "state.json").exists():
            self._restore()
            return

        self.meta = {
            "artist_id": artist_id,
            "title": title,
            "paper_id": paper_id,
            "size_mm": list(size_mm),
            "seed": seed,
            "cell_mm": cell_mm,
            "started": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        paper = Paper(PAPER_CATALOG[paper_id], seed=seed, size_mm=tuple(size_mm))
        self.canvas = Canvas(paper, cell_mm=cell_mm)
        self.tools = {tid: ToolState(tid, spec, load_ml=spec.reservoir_ml) for tid, spec in NIB_CATALOG.items()}
        self.held: str | None = None
        self.hand = HandState()
        self._n_strokes = 0
        self._event(
            "prepare",
            paper_id=paper_id,
            size_mm=list(size_mm),
            seed=seed,
            title=title,
            artist_id=artist_id,
        )
        self.save()

    # -- persistence -------------------------------------------------------

    def _restore(self) -> None:
        state = json.loads((self.dir / "state.json").read_text())
        self.meta = state["meta"]
        paper = Paper(
            PAPER_CATALOG[self.meta["paper_id"]],
            seed=self.meta["seed"],
            size_mm=tuple(self.meta["size_mm"]),
        )
        self.canvas = Canvas(paper, cell_mm=self.meta["cell_mm"])
        self.canvas.deposit = np.load(self.dir / "deposit.npy")
        self.canvas.damage = np.load(self.dir / "damage.npy")
        for name, field in (("guides.npy", "guides"), ("stain.npy", "stain"), ("pigment.npy", "pigment")):
            p = self.dir / name
            if p.exists():
                setattr(self.canvas, field, np.load(p))
        self.tools = {
            tid: ToolState(tid, NIB_CATALOG[tid], load_ml=st["load_ml"], wear=st["wear"])
            for tid, st in state["tools"].items()
        }
        self.held = state["held"]
        self.hand = HandState(**state["hand"])
        self._n_strokes = state["n_strokes"]

    def save(self) -> None:
        np.save(self.dir / "deposit.npy", self.canvas.deposit)
        np.save(self.dir / "damage.npy", self.canvas.damage)
        np.save(self.dir / "guides.npy", self.canvas.guides)
        np.save(self.dir / "stain.npy", self.canvas.stain)
        np.save(self.dir / "pigment.npy", self.canvas.pigment)
        state = {
            "meta": self.meta,
            "held": self.held,
            "hand": {"x_mm": self.hand.x_mm, "y_mm": self.hand.y_mm},
            "tools": {tid: {"load_ml": t.load_ml, "wear": t.wear} for tid, t in self.tools.items()},
            "n_strokes": self._n_strokes,
        }
        (self.dir / "state.json").write_text(json.dumps(state, indent=1))

    def _event(self, kind: str, **fields) -> None:
        record = {"type": kind, "t": time.strftime("%Y-%m-%dT%H:%M:%S"), **fields}
        with self.log_path.open("a") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    # -- the hand ----------------------------------------------------------

    def select_tool(self, tool_id: str) -> dict:
        if tool_id not in self.tools:
            raise ValueError(f"no such tool: {tool_id} (have: {', '.join(self.tools)})")
        prev, self.held = self.held, tool_id
        spec = self.tools[tool_id].spec
        self._event("tool_change", from_tool=prev, to_tool=tool_id)
        return {
            "held": tool_id,
            "feel": {
                "rigidity_n_per_mm": spec.rigidity_n_per_mm,
                "porosity": spec.porosity,
                "max_pressure_n": spec.max_pressure_n,
                "tip_radius_mm": spec.tip_radius_mm,
            },
            "load_ul": round(self.tools[tool_id].load_ml * 1000, 1),
        }

    def stroke(
        self,
        x0_mm: float,
        y0_mm: float,
        x1_mm: float,
        y1_mm: float,
        curvature: float = 0.0,
        pressure_start: float = 0.5,
        pressure_end: float = 0.5,
        speed_mm_s: float = 60.0,
        tag: str = "",
        layer: str = "ink",
        guide_color: str | None = None,
        guide_opacity: float = 1.0,
    ) -> dict:
        if self.held is None:
            raise ValueError("no tool in hand — select_tool first")
        tool = self.tools[self.held]
        cmd = expand_stroke(
            tool,
            (x0_mm, y0_mm),
            (x1_mm, y1_mm),
            curvature=curvature,
            pressure_start=pressure_start,
            pressure_end=pressure_end,
            speed_mm_s=speed_mm_s,
        )
        if layer == "guide":
            channel = {"red": 0, "green": 1, "blue": 2}[guide_color or "red"]
            fb = execute_stroke(
                self.canvas,
                tool,
                cmd,
                seed=self._n_strokes * 7 + 13,
                layer="guide",
                guide_channel=channel,
                guide_opacity=guide_opacity,
            )
        else:
            fb = execute_stroke(self.canvas, tool, cmd, seed=self._n_strokes * 7 + 13)
        self._n_strokes += 1
        self.hand.x_mm, self.hand.y_mm = x1_mm, y1_mm

        events = [{"kind": e.kind, "at": [round(e.x_mm, 1), round(e.y_mm, 1)], "note": e.note} for e in fb.events]
        self._event(
            "stroke",
            n=self._n_strokes,
            tool=self.held,
            tag=tag,
            params={
                "from": [x0_mm, y0_mm],
                "to": [x1_mm, y1_mm],
                "curvature": curvature,
                "pressure": [pressure_start, pressure_end],
                "speed_mm_s": speed_mm_s,
                "layer": layer,
                **({"guide_color": guide_color, "guide_opacity": guide_opacity} if layer == "guide" else {}),
            },
            feedback={
                "resistance_mean_n": round(fb.resistance_mean_n, 3),
                "resistance_peak_n": round(fb.resistance_peak_n, 3),
                "coverage": round(fb.coverage, 3),
                "load_after_ml": round(fb.load_after_ml, 5),
                "events": events,
            },
        )
        return {
            "n": self._n_strokes,
            "length_mm": round(cmd.length_mm(), 1),
            "resistance_mean_n": round(fb.resistance_mean_n, 3),
            "resistance_peak_n": round(fb.resistance_peak_n, 3),
            "coverage": round(fb.coverage, 3),
            "load_ul": round(fb.load_after_ml * 1000, 1),
            "events": events,
            "hand_at": [x1_mm, y1_mm],
        }

    def stroke_path(
        self,
        points_mm: list[float],
        pressure: float = 0.3,
        speed_mm_s: float = 60.0,
        tag: str = "",
    ) -> dict:
        """One continuous hand motion through waypoints — a gesture, not a
        sequence of spliced arcs. `points_mm` is [x0,y0,x1,y1,...]."""
        if self.held is None:
            raise ValueError("no tool in hand — select_tool first")
        if len(points_mm) < 6 or len(points_mm) % 2 != 0:
            raise ValueError("points_mm must be an even-length list of >= 3 waypoints")
        pts = [(points_mm[i], points_mm[i + 1]) for i in range(0, len(points_mm), 2)]
        tool = self.tools[self.held]
        cmd = expand_path_stroke(tool, pts, pressure=pressure, speed_mm_s=speed_mm_s)
        fb = execute_stroke(self.canvas, tool, cmd, seed=self._n_strokes * 7 + 13)
        self._n_strokes += 1
        self.hand.x_mm, self.hand.y_mm = pts[-1]

        events = [{"kind": e.kind, "at": [round(e.x_mm, 1), round(e.y_mm, 1)], "note": e.note} for e in fb.events]
        self._event(
            "stroke",
            n=self._n_strokes,
            tool=self.held,
            tag=tag,
            params={"gesture": "path", "waypoints": [[round(x, 1), round(y, 1)] for x, y in pts],
                    "pressure": pressure, "speed_mm_s": speed_mm_s},
            feedback={
                "resistance_mean_n": round(fb.resistance_mean_n, 3),
                "resistance_peak_n": round(fb.resistance_peak_n, 3),
                "coverage": round(fb.coverage, 3),
                "load_after_ml": round(fb.load_after_ml, 5),
                "events": events,
            },
        )
        return {
            "n": self._n_strokes,
            "length_mm": round(cmd.length_mm(), 1),
            "resistance_mean_n": round(fb.resistance_mean_n, 3),
            "resistance_peak_n": round(fb.resistance_peak_n, 3),
            "coverage": round(fb.coverage, 3),
            "events": events,
            "hand_at": [pts[-1][0], pts[-1][1]],
        }

    def erase(
        self,
        x0_mm: float,
        y0_mm: float,
        x1_mm: float,
        y1_mm: float,
        width_mm: float = 3.0,
        strength: float = 0.5,
        curvature: float = 0.0,
        tag: str = "",
        pattern: str = "linear",
    ) -> dict:
        """A soft eraser dragged along a hand path: lightens ink toward a
        permanent ghost, smears a little, abrades the paper. Patterns:
        linear | scribble (left-right zigzag) | loop (overlapping loops)."""
        if self.held is None:
            raise ValueError("no tool in hand — select_tool first")
        tool = self.tools[self.held]
        if pattern == "linear":
            cmd = expand_stroke(tool, (x0_mm, y0_mm), (x1_mm, y1_mm), curvature=curvature)
        else:
            pts = erase_pattern_points((x0_mm, y0_mm), (x1_mm, y1_mm), width_mm, pattern)
            cmd = expand_path_stroke(tool, pts, pressure=0.25, speed_mm_s=55)
        fb = execute_erase(self.canvas, cmd, width_mm, strength)
        self.hand.x_mm, self.hand.y_mm = x1_mm, y1_mm
        self._event(
            "erase",
            tool=self.held,
            tag=tag,
            params={
                "from": [x0_mm, y0_mm], "to": [x1_mm, y1_mm],
                "width_mm": width_mm, "strength": strength, "pattern": pattern,
            },
            feedback=fb,
        )
        return {"removed": fb["removed"], "peak_damage": fb["peak_damage"], "hand_at": [x1_mm, y1_mm]}

    def whiteout(
        self,
        x0_mm: float,
        y0_mm: float,
        x1_mm: float,
        y1_mm: float,
        width_mm: float = 4.0,
        strength: float = 0.9,
        curvature: float = 0.0,
        tag: str = "",
    ) -> dict:
        """Opaque white-out along a hand path: covers fully, no ghost, no
        abrasion — clean paper anywhere, ready to draw on. Finishing step."""
        if self.held is None:
            raise ValueError("no tool in hand — select_tool first")
        tool = self.tools[self.held]
        cmd = expand_stroke(tool, (x0_mm, y0_mm), (x1_mm, y1_mm), curvature=curvature)
        fb = execute_whiteout(self.canvas, cmd, width_mm, strength)
        self.hand.x_mm, self.hand.y_mm = x1_mm, y1_mm
        self._event(
            "whiteout",
            tool=self.held,
            tag=tag,
            params={"from": [x0_mm, y0_mm], "to": [x1_mm, y1_mm], "width_mm": width_mm, "strength": strength},
            feedback=fb,
        )
        return {"removed": fb["removed"], "hand_at": [x1_mm, y1_mm]}

    # -- the eyes ----------------------------------------------------------

    def view(self, name: str = "view", region_mm: tuple[float, float, float, float] | None = None, px_per_cell: int = 2) -> dict:
        canvas = self.canvas
        if region_mm is not None:
            x0, y0, x1, y1 = region_mm
            c = canvas.cell_mm
            nx0, ny0 = max(0, int(x0 / c)), max(0, int(y0 / c))
            nx1, ny1 = min(canvas.nx, int(x1 / c)), min(canvas.ny, int(y1 / c))
            target = SimpleNamespace(
                deposit=canvas.deposit[ny0:ny1, nx0:nx1],
                damage=canvas.damage[ny0:ny1, nx0:nx1],
                tooth=canvas.tooth[ny0:ny1, nx0:nx1],
                guides=canvas.guides[:, ny0:ny1, nx0:nx1],
                pigment=canvas.pigment[:, ny0:ny1, nx0:nx1],
                paper=canvas.paper,
                nx=nx1 - nx0,
                ny=ny1 - ny0,
            )
        else:
            target = canvas
        img = render(target, px_per_cell=px_per_cell)
        path = self.dir / "views" / f"{name}.png"
        img.save(path)
        self._event("view", name=name, region_mm=list(region_mm) if region_mm else None)
        return {"path": str(path), "px": list(img.size), "region_mm": list(region_mm) if region_mm else "full"}

    # -- the sketchbook ----------------------------------------------------

    def note(self, kind: str, text: str) -> dict:
        if kind not in NOTE_KINDS:
            raise ValueError(f"note kind must be one of {sorted(NOTE_KINDS)}")
        self._event("note", note_kind=kind, text=text)
        return {"ok": True}

    def export_artwork(self, name: str = "artwork") -> dict:
        path = self.dir / "views" / f"{name}.png"
        render(self.canvas).save(path)
        self._event("export", name=name)
        return {
            "png": str(path),
            "strokes": self._n_strokes,
            "log": str(self.log_path),
            "title": self.meta["title"],
            "artist_id": self.meta["artist_id"],
        }
