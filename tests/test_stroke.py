import numpy as np
import pytest

import painterly as pl
from painterly.canvas import Canvas
from painterly.stroke import curvature_through, expand_path_stroke, expand_stroke, execute_stroke

SMALL = (60.0, 40.0)


def make(spec_id: str, paper_id: str, load_ml: float = 1.0):
    paper = pl.Paper(pl.PAPER_CATALOG[paper_id], seed=3, size_mm=SMALL)
    canvas = Canvas(paper)
    tool = pl.ToolState("test", pl.NIB_CATALOG[spec_id], load_ml=load_ml)
    return canvas, tool


def stroke(canvas, tool, seed=0, **kw):
    cmd = expand_stroke(tool, (5.0, 20.0), (55.0, 20.0), **kw)
    return execute_stroke(canvas, tool, cmd, seed=seed)


def test_determinism():
    c1, t1 = make("fineliner_03", "cold_press")
    c2, t2 = make("fineliner_03", "cold_press")
    stroke(c1, t1, seed=7, pressure_start=0.5, pressure_end=0.5)
    stroke(c2, t2, seed=7, pressure_start=0.5, pressure_end=0.5)
    assert np.array_equal(c1.deposit, c2.deposit)
    assert t1.load_ml == t2.load_ml


def test_load_decreases_and_deposit_lands():
    c, t = make("fountain_f", "cold_press")
    start_load = t.load_ml
    fb = stroke(c, t, seed=1, pressure_start=0.6, pressure_end=0.6)
    assert t.load_ml < start_load
    assert c.deposit.sum() > 0
    assert fb.coverage > 0.9
    assert fb.touched_bbox_mm is not None


def test_light_stroke_on_rough_skips():
    c, t = make("fineliner_03", "rough")
    fb = stroke(c, t, seed=5, pressure_start=0.12, pressure_end=0.12)
    skips = [e for e in fb.events if e.kind == "skip"]
    assert skips, "low pressure on rough stock should catch and skip"


def test_pressure_shapes_width():
    c1, t1 = make("fountain_f", "plate_bristol")
    c2, t2 = make("fountain_f", "plate_bristol")
    stroke(c1, t1, seed=2, pressure_start=0.2, pressure_end=0.2)
    stroke(c2, t2, seed=2, pressure_start=0.9, pressure_end=0.9)
    w_light = np.count_nonzero(c1.deposit.sum(axis=0) > 0)
    w_heavy = np.count_nonzero(c2.deposit.sum(axis=0) > 0)
    assert w_heavy > w_light


def test_starved_nib_scratches():
    c, t = make("fineliner_03", "cold_press", load_ml=0.0)
    fb = stroke(c, t, seed=9)
    kinds = {e.kind for e in fb.events}
    assert "starved" in kinds
    assert fb.resistance_peak_n > 1.5
    assert c.deposit.sum() == pytest.approx(0.0, abs=1e-6)


def test_arc_passes_through_planned_point():
    a, mid, b = (0.0, 0.0), (10.0, 8.0), (20.0, 0.0)
    k = curvature_through(a, mid, b)
    c, t = make("fineliner_03", "plate_bristol")
    cmd = expand_stroke(t, a, b, curvature=k)
    # apex of the sampled arc (mid sits above the chord, so look for max y)
    i = max(range(cmd.n_samples), key=lambda i: cmd.ys_mm[i])
    assert abs(cmd.xs_mm[i] - mid[0]) < 2.0
    assert abs(cmd.ys_mm[i] - mid[1]) < 0.5


def test_path_stroke_one_motion_circle():
    # waypoints every 30° from north, counterclockwise, with a small overlap
    import math

    cx, cy, r = 40.0, 40.0, 18.0
    pts = []
    deg = 90
    while deg <= 448:
        a = math.radians(deg % 360 if deg != 448 else 88)
        pts.append((cx + r * math.cos(a), cy - r * math.sin(a)))
        deg += 30
    c, t = make("fineliner_03", "plate_bristol")
    cmd = expand_path_stroke(t, pts, pressure=0.3)

    # single gesture stays on the circle (no cardinal vertices, no loops)
    for x, y in zip(cmd.xs_mm, cmd.ys_mm):
        assert abs(math.hypot(x - cx, y - cy) - r) < 0.8

    # tangent continuity: heading changes gently everywhere (no spliced joins)
    worst = 0.0
    for i in range(2, cmd.n_samples):
        d1 = math.atan2(cmd.ys_mm[i - 1] - cmd.ys_mm[i - 2], cmd.xs_mm[i - 1] - cmd.xs_mm[i - 2])
        d2 = math.atan2(cmd.ys_mm[i] - cmd.ys_mm[i - 1], cmd.xs_mm[i] - cmd.xs_mm[i - 1])
        delta = abs((d2 - d1 + math.pi) % (2 * math.pi) - math.pi)
        worst = max(worst, delta)
    assert worst < math.radians(10), f"heading jumped {math.degrees(worst):.1f}°"


def test_path_stroke_rejects_degenerate_paths():
    c, t = make("fineliner_03", "plate_bristol")
    with pytest.raises(ValueError):
        expand_path_stroke(t, [(0.0, 0.0), (10.0, 10.0)])
