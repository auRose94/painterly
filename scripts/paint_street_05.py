"""Street study — sheet 5. Two-point perspective on rough paper.

Construction follows the classic sequence: horizon line, two vanishing points
(off-page), corner-first boxes, edges converging to the VPs, then hatching
that ALSO converges — shadow-face hatch lines run parallel to the face's
receding edges, so the shading obeys the same perspective as the structure.

Rough paper experiment: guide lines at low pressure skip on the tooth and read
as broken construction marks — the honest look of a working drawing.

Usage: python scripts/paint_street_05.py {1|2|3|4|final}
"""

import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from painterly.session import Session  # noqa: E402

DIR = ROOT / "sessions" / "street_study_05b"

HORIZON_Y = 75.0
VP_L = (-45.0, HORIZON_Y)  # off-page left
VP_R = (165.0, HORIZON_Y)  # off-page right
PAPER_W, PAPER_H = 120.0, 160.0

CORNER_X, TOP_Y, BASE_Y = 58.0, 30.0, 118.0
L_FACE_X, R_FACE_X = 20.0, 96.0  # outer edges of the corner building's faces
B2_X, B2_TOP = 20.0, 40.0  # left receding building, taller
B4_X, B4_TOP = 96.0, 38.0  # right receding building, taller


# face edge heights as functions of x (all linear — lines toward the VPs)
def ytl(x):  # corner left face, top
    return TOP_Y + (CORNER_X - x) * 45.0 / 103.0


def ybl(x):  # corner left face, bottom
    return BASE_Y - (CORNER_X - x) * 43.0 / 103.0


def ytr(x):  # corner right face, top
    return TOP_Y + (x - CORNER_X) * 45.0 / 107.0


def ybr(x):  # corner right face, bottom
    return BASE_Y - (x - CORNER_X) * 43.0 / 107.0


def y_b2t(x):
    return B2_TOP + (B2_X - x) * 35.0 / 65.0


def y_b2b(x):
    return ybl(B2_X) - (B2_X - x) * 43.0 / 103.0


def y_b4t(x):
    return B4_TOP + (x - B4_X) * 37.0 / 69.0


def y_b4b(x):
    return ybr(B4_X) - (x - B4_X) * 43.0 / 107.0


def get_session() -> Session:
    if (DIR / "state.json").exists():
        return Session(DIR, restore=True)
    return Session(
        DIR,
        paper_id="rough",
        seed=47,
        artist_id="unnamed-artist-0",
        title="Street corner, two-point perspective",
    )


def report(tag: str, fb: dict) -> None:
    skips = sum(1 for e in fb["events"] if e["kind"] == "skip")
    print(f"  [{tag:10s}] R={fb['resistance_mean_n']:.2f}N cov={fb['coverage']:.0%} skips={skips}")


def line(s, x0, y0, x1, y1, p, tag, taper=0.95):
    report(tag, s.stroke(x0, y0, x1, y1, pressure_start=p, pressure_end=p * taper, speed_mm_s=65, tag=tag))


def clip_x_toward(p, x_end, vp):
    """Point on the line p->vp at the given x (vp lines are straight)."""
    t = (x_end - p[0]) / (vp[0] - p[0])
    return (x_end, p[1] + t * (vp[1] - p[1]))


def window(s, yt, yb, x0, x1, f0, f1, tag, hatch_p=0.5):
    """A window on a receding face: verticals + edges converging to the VP,
    then dark vertical hatching for glass."""
    ya0 = yt(x0) + f0 * (yb(x0) - yt(x0))
    ya1 = yt(x1) + f0 * (yb(x1) - yt(x1))
    yc0 = yt(x0) + f1 * (yb(x0) - yt(x0))
    yc1 = yt(x1) + f1 * (yb(x1) - yt(x1))
    line(s, x0, ya0, x1, ya1, 0.34, tag)  # top edge, toward VP
    line(s, x0, yc0, x1, yc1, 0.34, tag)  # bottom edge, toward VP
    line(s, x0, ya0, x0, yc0, 0.40, tag)  # near jamb
    line(s, x1, ya1, x1, yc1, 0.40, tag)  # far jamb
    rng = random.Random(int(x0 * 10 + f0 * 100))
    x = x0 + 0.6
    while x <= x1 - 0.4:
        y0 = yt(x) + f0 * (yb(x) - yt(x)) + 0.5
        y1 = yt(x) + f1 * (yb(x) - yt(x)) - 0.5
        if y1 - y0 > 0.8:
            jx = x + rng.uniform(-0.15, 0.15)
            line(s, jx, y0, jx + rng.uniform(-0.1, 0.1), y1, hatch_p, tag, taper=0.8)
        x += 0.8


def pass5() -> None:
    """Value pass: the shadow face read as graph-paper grid, not shadow.
    Densify both hatch directions toward ~35% tone; darken the shadow-face
    windows so they stay the darkest notes."""
    import random

    s = get_session()
    s.select_tool("fineliner_03")
    rng = random.Random(555)

    # Denser fraction lines on the shadow face (halve the spacing).
    f = 0.028
    while f <= 0.96:
        ya = ytr(CORNER_X) + f * (ybr(CORNER_X) - ytr(CORNER_X))
        yb2 = ytr(R_FACE_X) + f * (ybr(R_FACE_X) - ytr(R_FACE_X))
        line(s, CORNER_X, ya, R_FACE_X, yb2, 0.28, "shadow-dense")
        f += 0.024

    # Denser verticals, offset between the first layer's.
    x = 61.3
    while x <= 94.5:
        line(s, x, ytr(x) + 1.4, x, ybr(x) - 1.4, 0.24, "shadow-vert2")
        x += 1.4

    # Fill the right-face window glass denser — they must stay darkest.
    for x0, x1 in ((62.0, 70.0), (78.0, 86.0)):
        for f0, f1 in ((0.16, 0.36), (0.50, 0.70)):
            x = x0 + 0.4
            while x <= x1 - 0.3:
                y0 = ytr(x) + f0 * (ybr(x) - ytr(x)) + 0.3
                y1 = ytr(x) + f1 * (ybr(x) - ytr(x)) - 0.3
                jx = x + rng.uniform(-0.12, 0.12)
                line(s, jx, y0, jx + rng.uniform(-0.1, 0.1), y1, 0.52, "win-dark", taper=0.8)
                x += 0.4

    # B2's shadow face: one more light layer so it holds tone at distance.
    f = 0.20
    while f <= 0.82:
        ya = y_b2t(B2_X) + f * (y_b2b(B2_X) - y_b2t(B2_X))
        yb2 = y_b2t(2.0) + f * (y_b2b(2.0) - y_b2t(2.0))
        line(s, B2_X, ya, 2.0, yb2, 0.24, "b2-shadow2")
        f += 0.08

    s.save()
    print("pass5 view:", s.view("pass5"))


def pass1() -> None:
    s = get_session()
    s.note(
        "attempt_boundary",
        "street_study_05 rejected: structure pass crashed (helper took "
        "(x_end, p) but was called (p, x_end)); hatch and windows landed on "
        "bare paper. Kept as corpus. This sheet restarts clean with the fix.",
    )
    s.note(
        "material_choice",
        "Rough stock for sheet 5: tooth amplitude 0.22mm. Guide lines drawn "
        "light will skip and break — construction marks that look worked, "
        "because on this paper they are. Structure lines need firmer pressure "
        "to stay solid; the log records what each pressure survives.",
    )
    s.note(
        "reflection",
        "Plan: two-point perspective, VPs off-page at x=-45 and x=165 on the "
        "horizon. Corner building nearest, one building receding on each side, "
        "curb lines making the floor read. Light from upper left: right-facing "
        "walls in shadow, hatched along their receding direction so the "
        "shading converges to the same VP as the edges.",
    )
    s.select_tool("fineliner_03")

    # Guide: the horizon, light — the tooth will break it, as guides break.
    line(s, 4, HORIZON_Y, 116, HORIZON_Y, 0.12, "horizon", taper=1.0)

    # Small VP ticks on the horizon for honest measuring.
    for x in (10, 60, 110):
        line(s, x, HORIZON_Y - 3, x, HORIZON_Y + 3, 0.12, "vp-tick", taper=1.0)

    s.save()
    print("pass1 view:", s.view("pass1"))


def pass2() -> None:
    s = get_session()
    s.select_tool("fineliner_03")

    # Corner building: the nearest vertical carries the composition.
    line(s, CORNER_X, TOP_Y, CORNER_X, BASE_Y, 0.44, "corner-vert")
    # left face (lit): top and bottom edges toward the left VP
    line(s, CORNER_X, TOP_Y, L_FACE_X, ytl(L_FACE_X), 0.38, "face-edge")
    line(s, CORNER_X, BASE_Y, L_FACE_X, ybl(L_FACE_X), 0.38, "face-edge")
    line(s, L_FACE_X, ytl(L_FACE_X), L_FACE_X, ybl(L_FACE_X), 0.42, "outer-vert")
    # right face (shadow side)
    line(s, CORNER_X, TOP_Y, R_FACE_X, ytr(R_FACE_X), 0.38, "face-edge")
    line(s, CORNER_X, BASE_Y, R_FACE_X, ybr(R_FACE_X), 0.38, "face-edge")
    line(s, R_FACE_X, ytr(R_FACE_X), R_FACE_X, ybr(R_FACE_X), 0.42, "outer-vert")

    # Base lines run to the VPs — the street floor begins here.
    e = clip_x_toward((CORNER_X, BASE_Y), 0.0, VP_L)
    line(s, CORNER_X, BASE_Y, e[0], e[1], 0.34, "base-L")
    e = clip_x_toward((CORNER_X, BASE_Y), PAPER_W, VP_R)
    line(s, CORNER_X, BASE_Y, e[0], e[1], 0.34, "base-R")

    # B2: left receding, taller, shares the corner building's outer edge.
    line(s, B2_X, B2_TOP, B2_X, ybl(B2_X), 0.40, "b2-vert")
    e = clip_x_toward((B2_X, B2_TOP), 0.0, VP_L)
    line(s, B2_X, B2_TOP, e[0], e[1], 0.34, "b2-top")
    e = clip_x_toward((B2_X, ybl(B2_X)), 0.0, VP_L)
    line(s, B2_X, ybl(B2_X), e[0], e[1], 0.30, "b2-base")

    # B4: right receding, taller.
    line(s, B4_X, B4_TOP, B4_X, ybr(B4_X), 0.40, "b4-vert")
    e = clip_x_toward((B4_X, B4_TOP), PAPER_W, VP_R)
    line(s, B4_X, B4_TOP, e[0], e[1], 0.34, "b4-top")
    e = clip_x_toward((B4_X, ybr(B4_X)), PAPER_W, VP_R)
    line(s, B4_X, ybr(B4_X), e[0], e[1], 0.30, "b4-base")

    # Sidewalk curbs — the V that makes the floor obvious.
    for x0, tag in ((30.0, "curb-outer-L"), (40.0, "curb-inner-L")):
        y0 = 158.0 if "outer" in tag else 146.0
        e = clip_x_toward((x0, y0), 0.0, VP_L)
        line(s, x0, y0, e[0], e[1], 0.32, "curb")
    for x0, tag in ((90.0, "curb-outer-R"), (80.0, "curb-inner-R")):
        y0 = 158.0 if "outer" in tag else 146.0
        e = clip_x_toward((x0, y0), PAPER_W, VP_R)
        line(s, x0, y0, e[0], e[1], 0.32, "curb")

    s.save()
    print("pass2 view:", s.view("pass2"))


def pass3() -> None:
    s = get_session()
    s.select_tool("fineliner_03")

    # Shadow hatch on the corner building's right face: fraction lines running
    # toward the right VP — the shading obeys the perspective.
    f = 0.06
    while f <= 0.95:
        ya = ytr(CORNER_X) + f * (ybr(CORNER_X) - ytr(CORNER_X))
        yb2 = ytr(R_FACE_X) + f * (ybr(R_FACE_X) - ytr(R_FACE_X))
        line(s, CORNER_X, ya, R_FACE_X, yb2, 0.30, "shadow-h1")
        f += 0.048

    # Cross layer: verticals — with the converging horizontals this makes a
    # mesh that respects both the VP and the verticals.
    x = 60.0
    while x <= 94.0:
        line(s, x, ytr(x) + 1.6, x, ybr(x) - 1.6, 0.26, "shadow-h2")
        x += 2.6

    # B2's visible face faces the shadow side too — distant, so lighter.
    f = 0.12
    while f <= 0.9:
        ya = y_b2t(B2_X) + f * (y_b2b(B2_X) - y_b2t(B2_X))
        yb2 = y_b2t(2.0) + f * (y_b2b(2.0) - y_b2t(2.0))
        line(s, B2_X, ya, 2.0, yb2, 0.22, "b2-shadow")
        f += 0.16

    # Contact shadows hugging the base lines — darkest where wall meets floor.
    for d, xe, p in ((0.7, 36.0, 0.44), (1.6, 42.0, 0.36), (2.6, 47.0, 0.28), (3.6, 51.0, 0.20)):
        ya, yb2 = BASE_Y + d, BASE_Y + d - (CORNER_X - xe) * (43.0 + d) / 103.0
        line(s, CORNER_X, ya, xe, yb2, p, "ground-L")
    for d, xe, p in ((0.7, 78.0, 0.44), (1.6, 72.0, 0.36), (2.6, 67.0, 0.28), (3.6, 63.0, 0.20)):
        ya, yb2 = BASE_Y + d, BASE_Y + d + (xe - CORNER_X) * (43.0 + d) / 107.0
        line(s, CORNER_X, ya, xe, yb2, p, "ground-R")

    s.save()
    print("pass3 view:", s.view("pass3"))


def pass4() -> None:
    s = get_session()
    s.select_tool("fineliner_03")

    # Windows: corner building, 2x2 per face.
    for x0, x1 in ((30.0, 38.0), (44.0, 52.0)):
        for f0, f1 in ((0.16, 0.36), (0.50, 0.70)):
            window(s, ytl, ybl, x0, x1, f0, f1, "win-L")
    for x0, x1 in ((62.0, 70.0), (78.0, 86.0)):
        for f0, f1 in ((0.16, 0.36), (0.50, 0.70)):
            window(s, ytr, ybr, x0, x1, f0, f1, "win-R")

    # B2: one small window; B4: two columns.
    window(s, y_b2t, y_b2b, 7.0, 15.0, 0.25, 0.52, "win-b2", hatch_p=0.42)
    for x0, x1 in ((100.0, 107.0), (111.0, 118.0)):
        for f0, f1 in ((0.20, 0.42), (0.55, 0.77)):
            window(s, y_b4t, y_b4b, x0, x1, f0, f1, "win-b4", hatch_p=0.42)

    s.save()
    print("pass4 view:", s.view("pass4"))


def final() -> None:
    s = get_session()
    print("loupe:", s.view("loupe", region_mm=[14.0, 24.0, 104.0, 130.0], px_per_cell=3))
    s.note(
        "artist_statement",
        "A street corner in two-point perspective, drawn on rough stock with a "
        "0.3 fineliner. Construction is left visible: the horizon guide broke "
        "on the paper's tooth and stays broken, the way working drawings do. "
        "Every shadow line runs toward the same vanishing point as the edges "
        "it shades between — the darkness obeys the geometry. The windows are "
        "the darkest notes; the street floor is carried by curbs and contact "
        "shadows converging off-page.",
    )
    print("export:", s.export_artwork("street_study_05"))
    kinds = {}
    skips_light = skips_firm = n_light = n_firm = 0
    for line_txt in (DIR / "log.jsonl").read_text().splitlines():
        import json

        rec = json.loads(line_txt)
        if rec["type"] == "stroke":
            kinds["strokes"] = kinds.get("strokes", 0) + 1
            p = rec["params"]["pressure"][0]
            sk = sum(1 for e in rec["feedback"]["events"] if e["kind"] == "skip")
            length = math.hypot(
                rec["params"]["from"][0] - rec["params"]["to"][0],
                rec["params"]["from"][1] - rec["params"]["to"][1],
            )
            if p < 0.2 and length > 2:
                n_light += 1
                skips_light += sk
            elif p >= 0.3 and length > 2:
                n_firm += 1
                skips_firm += sk
        elif rec["type"] == "view":
            kinds["views"] = kinds.get("views", 0) + 1
        elif rec["type"] == "note":
            kinds["notes"] = kinds.get("notes", 0) + 1
    print("session log:", kinds)
    print(
        f"skip physics, rough stock: light strokes (<0.2N press) averaged "
        f"{skips_light / max(1, n_light):.2f} skips over {n_light} strokes; "
        f"firm strokes (>=0.3N) averaged {skips_firm / max(1, n_firm):.2f} over {n_firm}"
    )


if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else "1"
    {"1": pass1, "2": pass2, "3": pass3, "4": pass4, "5": pass5, "final": final}[stage]()
