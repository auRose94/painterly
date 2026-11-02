import json
import math
import shutil
from pathlib import Path

from painterly.fonts import FONT
from painterly.session import Session


def fresh(tmp_name):
    tmp = Path(__file__).resolve().parents[1] / "sessions" / tmp_name
    shutil.rmtree(tmp, ignore_errors=True)
    s = Session(tmp, paper_id="plate_bristol", seed=9, size_mm=(120.0, 120.0))
    s.select_tool("fineliner_03")
    return s, tmp


def strokes_with_tag(tmp, tag):
    out = []
    for ln in (tmp / "log.jsonl").read_text().splitlines():
        if '"stroke"' in ln and f'"tag": "{tag}"' in ln:
            out.append(json.loads(ln))
    return out


def test_balloon_closes_without_strike():
    """The page-3..5 bug: a duplicated closing point turned the balloon's
    last segment into a chord from east to southwest. The tested primitive
    must produce exactly 12 arcs x 2 passes — no chord."""
    from painterly.panels import balloon

    s, tmp = fresh("_test_balloon")
    balloon(s, 60.0, 60.0, 20.0, 12.0, ["HELLO"])
    strokes = strokes_with_tag(tmp, "balloon")
    assert len(strokes) == 24, f"12 arcs x 2 passes expected, got {len(strokes)}"
    shutil.rmtree(tmp, ignore_errors=True)


def test_balloon_script_sits_mid_balloon():
    from painterly.panels import balloon

    s, tmp = fresh("_test_balloon_tail")
    balloon(s, 60.0, 60.0, 16.0, 10.0, ["HI"], tail=(60.0, 90.0))
    type_strokes = []
    for ln in (tmp / "log.jsonl").read_text().splitlines():
        if '"stroke"' in ln and '"tag": "type"' in ln:
            rec = json.loads(ln)
            type_strokes += [rec["params"]["from"], rec["params"]["to"]]
    assert type_strokes, "script should be stamped"
    # every type dab sits in the vertical middle band of the balloon,
    # safely away from rim and tail
    for (px, py) in type_strokes:
        assert 56.0 <= px <= 64.0, f"type x {px} outside the safe band"
        assert 57.0 <= py <= 63.0, f"type y {py} outside the safe band"
    shutil.rmtree(tmp, ignore_errors=True)


def test_gull_is_wide_not_tall():
    from painterly.panels import gull

    s, tmp = fresh("_test_gull")
    gull(s, 50.0, 60.0, 4.0)
    strokes = strokes_with_tag(tmp, "gull")
    xs, ys = [], []
    for rec in strokes:
        xs += [rec["params"]["from"][0], rec["params"]["to"][0]]
        ys += [rec["params"]["from"][1], rec["params"]["to"][1]]
    width, height = max(xs) - min(xs), max(ys) - min(ys)
    assert width >= 3.5
    assert height < width * 0.75, f"gull must be wider than tall, got {height}/{width}"
    shutil.rmtree(tmp, ignore_errors=True)


def test_hair_strands_flow_one_direction():
    from painterly.panels import hair_strands

    s, tmp = fresh("_test_hair")
    roots = [(50.0, 50.0 + 3.0 * k) for k in range(3)]
    hair_strands(s, roots, (0.0, 1.0), length=5.0, n=3, seed=1, tag="hair")
    strokes = strokes_with_tag(tmp, "hair")
    assert strokes, "strands should exist"
    for rec in strokes:
        (x0, y0), (x1, y1) = rec["params"]["from"], rec["params"]["to"]
        a = math.atan2(y1 - y0, x1 - x0)
        delta = abs((a - math.pi / 2 + math.pi) % (2 * math.pi) - math.pi)
        assert delta < math.radians(55), f"strand off-flow by {math.degrees(delta):.0f} deg"
    shutil.rmtree(tmp, ignore_errors=True)
