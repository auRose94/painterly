"""First marks: the canvas pushes back.

Three fineliner strokes and one fountain stroke on cold-press paper — light,
medium, heavy, then a pressure ramp. Prints what the handle felt and renders
the result to output/first_marks.png.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import painterly as pl
from painterly.canvas import Canvas
from painterly.render import render
from painterly.stroke import execute_stroke, expand_stroke

OUT = Path(__file__).resolve().parents[1] / "output"


def report(name: str, fb) -> None:
    kinds: dict[str, int] = {}
    for e in fb.events:
        kinds[e.kind] = kinds.get(e.kind, 0) + 1
    ev = ", ".join(f"{k}×{v}" for k, v in kinds.items()) or "clean"
    print(
        f"{name:24s} resistance {fb.resistance_mean_n:.2f}N (peak {fb.resistance_peak_n:.2f})"
        f" | coverage {fb.coverage:.0%} | load {fb.load_after_ml * 1000:.1f} µl | {ev}"
    )


def main() -> None:
    paper = pl.Paper(pl.PAPER_CATALOG["cold_press"], seed=11, size_mm=(120.0, 160.0))
    canvas = Canvas(paper)
    fineliner = pl.ToolState("fineliner_03", pl.NIB_CATALOG["fineliner_03"], load_ml=1.2)
    fountain = pl.ToolState("fountain_f", pl.NIB_CATALOG["fountain_f"], load_ml=1.5)

    strokes = [
        ("light fineliner", fineliner, ((15, 30), (105, 30)), 0.15, 0.12, 0.12, 80),
        ("medium fineliner arc", fineliner, ((15, 60), (105, 60)), -0.25, 0.55, 0.55, 55),
        ("heavy fineliner", fineliner, ((15, 90), (105, 90)), 0.0, 0.95, 0.9, 70),
        ("pressure ramp 0.05→0.9", fountain, ((15, 118), (105, 115)), 0.0, 0.05, 0.9, 55),
        ("fountain, wet + heavy", fountain, ((15, 145), (105, 142)), 0.1, 0.8, 0.75, 45),
    ]

    for i, (name, tool, (a, b), curv, p0, p1, speed) in enumerate(strokes):
        cmd = expand_stroke(tool, a, b, curvature=curv, pressure_start=p0, pressure_end=p1, speed_mm_s=speed)
        fb = execute_stroke(canvas, tool, cmd, seed=100 + i)
        report(name, fb)

    OUT.mkdir(exist_ok=True)
    path = OUT / "first_marks.png"
    render(canvas).save(path)
    print(f"\nrendered → {path}")


if __name__ == "__main__":
    main()
