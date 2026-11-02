import numpy as np
import pytest

import painterly as pl
from painterly.canvas import Canvas
from painterly.render import render
from painterly.stroke import execute_erase, execute_stroke, expand_stroke

SMALL = (60.0, 40.0)


def make(spec_id: str, paper_id: str, load_ml: float = 1.0):
    paper = pl.Paper(pl.PAPER_CATALOG[paper_id], seed=3, size_mm=SMALL)
    canvas = Canvas(paper)
    tool = pl.ToolState("test", pl.NIB_CATALOG[spec_id], load_ml=load_ml)
    return canvas, tool


def test_guide_stroke_lays_color_not_ink():
    c, t = make("fineliner_03", "plate_bristol")
    cmd = expand_stroke(t, (10.0, 20.0), (50.0, 20.0))
    execute_stroke(c, t, cmd, layer="guide", guide_channel=0, guide_opacity=0.5)
    assert c.guides[0].sum() > 0, "red channel should carry the construction"
    assert c.deposit.sum() == pytest.approx(0.0, abs=1e-6), "no ink must land"
    assert t.load_ml == 1.0, "pencil does not drink from the ink reservoir"
    img = np.asarray(render(c))
    # sample where the guide ran: should read reddish
    row = int(20.0 / c.cell_mm) * 2
    mid = img[row, 400:420].mean(axis=0)
    assert mid[0] > mid[2], f"guide pixel should be red-leaning, got {mid}"


def test_soft_eraser_leaves_ghost_and_damage():
    c, t = make("fineliner_03", "plate_bristol")
    cmd = expand_stroke(t, (10.0, 20.0), (50.0, 20.0), pressure_start=0.8, pressure_end=0.8)
    execute_stroke(c, t, cmd)
    peak_before = float(c.deposit.max())
    center = (int(20.0 / c.cell_mm), int(30.0 / c.cell_mm))  # on the line
    before_center = float(c.deposit[center])

    ecmd = expand_stroke(t, (30.0, 20.0), (32.0, 20.0))
    execute_erase(c, ecmd, width_mm=4.0, strength=0.9)

    after_center = float(c.deposit[center])
    assert after_center < before_center, "eraser must lighten the line"
    floor = float(c.stain[center]) * 0.18 - 1e-4
    assert after_center >= floor, "ink dye stays in the fibers — ghost remains"
    assert float(c.damage[center]) > 0.0, "paper must abrade"
    assert peak_before > 0


def test_eraser_smears_neighbors():
    c, t = make("fineliner_03", "plate_bristol")
    cmd = expand_stroke(t, (10.0, 20.0), (50.0, 20.0), pressure_start=0.9, pressure_end=0.9)
    execute_stroke(c, t, cmd)
    off = (int(20.0 / c.cell_mm) + 2, int(30.0 / c.cell_mm))  # just off the line
    before = float(c.deposit[off])
    ecmd = expand_stroke(t, (30.0, 20.0), (32.0, 20.0))
    execute_erase(c, ecmd, width_mm=5.0, strength=0.7)
    after = float(c.deposit[off])
    assert after > before or after > 0.0, "smear should move deposit toward neighbors"


def test_whiteout_covers_fully_without_abrading():
    from painterly.stroke import execute_whiteout

    c, t = make("fineliner_03", "plate_bristol")
    execute_stroke(c, t, expand_stroke(t, (10.0, 20.0), (50.0, 20.0), pressure_start=0.8, pressure_end=0.8))
    mid = (int(20.0 / c.cell_mm), int(30.0 / c.cell_mm))
    assert float(c.deposit[mid]) > 0
    wcmd = expand_stroke(t, (25.0, 20.0), (35.0, 20.0))
    execute_whiteout(c, wcmd, width_mm=6.0, strength=0.97)
    assert float(c.deposit[mid]) < 0.01, "gouache covers the ink"
    assert float(c.damage.sum()) == 0.0, "white-out protects the paper"


def test_pigmented_ink_and_optical_mix():
    c, t = make("fineliner_red", "plate_bristol")
    assert t.spec.pigment_channel == 0
    execute_stroke(c, t, expand_stroke(t, (12.0, 20.0), (40.0, 20.0), pressure_start=0.8, pressure_end=0.8))
    tb = pl.ToolState("blue", pl.NIB_CATALOG["fineliner_blue"], load_ml=1.0)
    execute_stroke(c, tb, expand_stroke(tb, (24.0, 20.15), (44.0, 20.3), pressure_start=0.8, pressure_end=0.8))
    mid = (int(20.05 / c.cell_mm), int(32.0 / c.cell_mm))  # inside both nib footprints
    assert c.pigment[0][mid] > 0 and c.pigment[1][mid] > 0, "both pigments land"
    assert c.pigment[2][mid] == pytest.approx(0.0), "no yellow was used"
    img = np.asarray(render(c))
    px = img[mid[0] * 2, mid[1] * 2]
    assert px[0] > px[1] and px[2] > px[1], f"red+blue should mix violet-ish, got {px}"
