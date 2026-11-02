"""Street study — sheet 6. ONE-point perspective, VP ON the canvas.

Fixes carried from sheet 5's critique:
  - the vanishing point is visible in the composition, on the horizon, and
    EVERY guide line drawn in pass 1 is a line the structure actually rides
    (the etching-style construction stays visible in the final)
  - every building shows its receding side face — all boxes, no flat planes

Usage: python scripts/paint_street_06.py {1|2|3|4|final}
"""

import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from painterly.session import Session  # noqa: E402

DIR = ROOT / "sessions" / "street_study_06b"

VP = (60.0, 70.0)  # the vanishing point — on the canvas, on the horizon
HORIZON_Y = 70.0

# buildings: front-face rect (parallel to the picture plane) + depth factor s
# (the back face is the front face scaled toward the VP by s)
L1 = dict(fl=6.0, fr=24.0, yt=34.0, yb=126.0, s=0.55)  # near left, street edge = fr
L2 = dict(fl=40.2, fr=52.0, yt=44.0, yb=112.0, s=0.42)  # far left
R1 = dict(fl=96.0, fr=114.0, yt=40.0, yb=120.0, s=0.50)  # near right, street edge = fl
R2 = dict(fl=78.0, fr=96.0, yt=46.0, yb=108.0, s=0.40)  # far right


def ray_point(p, s):
    """Point on the ray VP -> p, at fraction s toward p (s=1 is p itself)."""
    return (VP[0] + (p[0] - VP[0]) * s, VP[1] + (p[1] - VP[1]) * s)


def ray_at_x(p, x):
    """Point on the ray VP -> p at the given screen x."""
    u = (x - VP[0]) / (p[0] - VP[0])
    return (x, VP[1] + u * (p[1] - VP[1]))


def get_session() -> Session:
    if (DIR / "state.json").exists():
        return Session(DIR, restore=True)
    return Session(
        DIR,
        paper_id="hot_press",
        seed=53,
        artist_id="unnamed-artist-0",
        title="Street in one-point perspective",
    )


def report(tag: str, fb: dict) -> None:
    skips = sum(1 for e in fb["events"] if e["kind"] == "skip")
    print(f"  [{tag:10s}] R={fb['resistance_mean_n']:.2f}N cov={fb['coverage']:.0%} skips={skips}")


def line(s, x0, y0, x1, y1, p, tag, taper=0.95):
    report(tag, s.stroke(x0, y0, x1, y1, pressure_start=p, pressure_end=p * taper, speed_mm_s=65, tag=tag))


def side_face(b):
    """The receding face: front street-edge corners and their scaled backs."""
    front_top = (b["fr"], b["yt"]) if b is not R1 and b is not R2 else (b["fl"], b["yt"])
    edge_x = b["fr"] if b in (L1, L2) else b["fl"]
    ft = (edge_x, b["yt"])
    fb = (edge_x, b["yb"])
    return ft, fb, ray_point(ft, b["s"]), ray_point(fb, b["s"])


def building_hex(b):
    """Full visible silhouette: front face + receding side face."""
    if b in (L1, L2):
        edge_x, outer_x = b["fr"], b["fl"]
    else:
        edge_x, outer_x = b["fl"], b["fr"]
    ft, fb = (edge_x, b["yt"]), (edge_x, b["yb"])
    bt, bb = ray_point(ft, b["s"]), ray_point(fb, b["s"])
    return [(outer_x, b["yt"]), ft, bt, bb, fb, (outer_x, b["yb"])]


HEXES = [building_hex(b) for b in (L1, L2, R1, R2)]


def point_in_poly(pt, poly):
    inside = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > pt[1]) != (yj > pt[1]) and pt[0] < (xj - xi) * (pt[1] - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


def occluded(pt):
    return any(point_in_poly(pt, h) for h in HEXES)


def draw_line_clipped(s, a, b, p, tag):
    """Draw a construction line only where no building occludes it — the
    etcher's convention: construction shows in free air, hides behind solids."""
    import math

    dist = math.hypot(b[0] - a[0], b[1] - a[1])
    steps = max(2, int(dist / 0.2))
    run_start = None
    for i in range(steps + 1):
        t = i / steps
        pt = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
        if not occluded(pt):
            if run_start is None:
                run_start = (pt, t)
            run_end = (pt, t)
        else:
            if run_start is not None:
                d = math.hypot(run_end[0][0] - run_start[0][0], run_end[0][1] - run_start[0][1])
                if d > 0.5:
                    line(s, run_start[0][0], run_start[0][1], run_end[0][0], run_end[0][1], p, tag, taper=1.0)
                run_start = None
    if run_start is not None:
        d = math.hypot(run_end[0][0] - run_start[0][0], run_end[0][1] - run_start[0][1])
        if d > 0.5:
            line(s, run_start[0][0], run_start[0][1], run_end[0][0], run_end[0][1], p, tag, taper=1.0)


def pass1() -> None:
    s = get_session()
    s.note(
        "attempt_boundary",
        "street_study_06 rejected: floor transversals were centered on the "
        "VP's x instead of interpolating the curb lines — the tiles widened "
        "toward the vanishing point, inside-out. Also the construction rays "
        "cut straight through building faces; the etcher's rule is they show "
        "only in free air. Both fixed here: transversals interpolate the "
        "curbs, rays are occlusion-clipped against building silhouettes.",
    )
    s.note(
        "material_choice",
        "Hot-press for sheet 6: the lesson is construction, and rough stock's "
        "broken lines fought the last sheet's structure. Construction rays "
        "stay visible on purpose — the etching tradition.",
    )
    s.note(
        "reflection",
        "Carried fix: sheet 5's VP ticks were decoration — nothing converged "
        "to them while the real VPs sat off-page. A guide that lies is worse "
        "than none. Here the VP is ON the canvas at (60,70), the horizon "
        "passes through it, and every ray drawn now is a line the geometry "
        "rides. All four buildings show receding side faces — boxes, not "
        "planes.",
    )
    s.select_tool("fineliner_03")

    # Horizon through the VP, and the VP marked — this time honestly.
    draw_line_clipped(s, (4, HORIZON_Y), (116, HORIZON_Y), 0.11, "horizon")
    line(s, VP[0] - 2.5, VP[1], VP[0] + 2.5, VP[1], 0.30, "vp-mark", taper=1.0)
    line(s, VP[0], VP[1] - 2.5, VP[0], VP[1] + 2.5, 0.30, "vp-mark", taper=1.0)

    # Construction rays: every one is a line the buildings will sit on,
    # shown only where the buildings don't occlude them.
    for target in (
        (6, 34), (24, 34), (24, 126), (6, 126),      # L1 corners
        (52, 44), (52, 112),                          # L2 street edge
        (114, 40), (96, 40), (96, 120), (114, 120),   # R1 corners
        (78, 46), (78, 108),                          # R2 street edge
        (2, 150), (118, 150),                         # curbs
    ):
        draw_line_clipped(s, VP, target, 0.11, "ray")

    s.save()
    print("pass1 view:", s.view("pass1"))


def pass2() -> None:
    s = get_session()
    s.select_tool("fineliner_03")

    for b, outer_x in ((L1, 6.0), (L2, 40.2), (R1, 114.0), (R2, 78.0)):
        # front face: top, bottom, both verticals
        line(s, b["fl"], b["yt"], b["fr"], b["yt"], 0.36, "front-top")
        line(s, b["fl"], b["yb"], b["fr"], b["yb"], 0.36, "front-bot")
        line(s, b["fl"], b["yt"], b["fl"], b["yb"], 0.42, "front-vert")
        line(s, b["fr"], b["yt"], b["fr"], b["yb"], 0.42, "front-vert")
        # receding side face: top ray, bottom ray, back vertical
        ft, fb, bt, bb = side_face(b)
        line(s, ft[0], ft[1], bt[0], bt[1], 0.34, "side-top")
        line(s, fb[0], fb[1], bb[0], bb[1], 0.30, "side-bot")
        line(s, bt[0], bt[1], bb[0], bb[1], 0.38, "back-vert")

    # Curbs converge to the VP — the floor reads from these two plus bases.
    for p, tagx in (((2, 150), "curb-L"), ((118, 150), "curb-R")):
        e = ray_point(p, 0.18)
        line(s, p[0], p[1], e[0], e[1], 0.32, "curb")

    s.save()
    print("pass2 view:", s.view("pass2"))


def pass3() -> None:
    s = get_session()
    s.select_tool("fineliner_03")

    # Floor: transversals interpolated ALONG the curb lines — wide near the
    # viewer, tightening to the VP. (Sheet 6 had this inverted.)
    for y, p in ((76, 0.14), (80, 0.14), (86, 0.15), (94, 0.15), (104, 0.15), (116, 0.16), (130, 0.16), (146, 0.16)):
        u = (150.0 - y) / 80.0
        xl = 2.0 + 58.0 * u
        xr = 118.0 - 58.0 * u
        line(s, xl, y, xr, y, p, "floor-t")

    # Shadow hatch: left buildings' side faces face away from the sun.
    for b, fstep, p, jstep, jp in ((L1, 0.05, 0.30, 3.0, 0.22), (L2, 0.09, 0.22, 3.0, 0.16)):
        ft, fb, bt, bb = side_face(b)
        f = 0.06
        while f <= 0.94:
            pf = (ft[0], ft[1] + f * (fb[1] - ft[1]))
            pb = ray_point(pf, b["s"])
            line(s, pf[0], pf[1], pb[0], pb[1], p, "side-shadow")
            f += fstep
        # wall joints: verticals between the top and bottom rays
        x = ft[0] + jstep
        while x < bt[0] - 0.5:
            t = ray_at_x(ft, x)
            bo = ray_at_x(fb, x)
            line(s, x, t[1], x, bo[1], jp, "side-joint")
            x += jstep

    # Contact shadows where walls meet floor.
    line(s, 6, 127.2, 20, 127.2, 0.40, "contact")
    line(s, 6, 128.2, 15, 128.2, 0.30, "contact")
    p1 = ray_point((24.6, 126.6), 0.52)
    line(s, 24.6, 126.6, p1[0], p1[1], 0.36, "contact")
    p2 = ray_point((24.6, 127.6), 0.40)
    line(s, 24.6, 127.6, p2[0], p2[1], 0.26, "contact")
    line(s, 100, 121.2, 112, 121.2, 0.28, "contact")
    p3 = ray_point((95.4, 120.6), 0.5)
    line(s, 95.4, 120.6, p3[0], p3[1], 0.24, "contact")

    s.save()
    print("pass3 view:", s.view("pass3"))


def window_rect(s, x0, x1, y0, y1, hatch_p, hatch_step, tag):
    line(s, x0, y0, x1, y0, 0.34, tag)
    line(s, x0, y1, x1, y1, 0.34, tag)
    line(s, x0, y0, x0, y1, 0.40, tag)
    line(s, x1, y0, x1, y1, 0.40, tag)
    rng = random.Random(int(x0 * 7 + y0))
    x = x0 + 0.6
    while x <= x1 - 0.4:
        jx = x + rng.uniform(-0.15, 0.15)
        line(s, jx, y0 + 0.5, jx + rng.uniform(-0.1, 0.1), y1 - 0.5, hatch_p, tag, taper=0.8)
        x += hatch_step


def pass4() -> None:
    s = get_session()
    s.select_tool("fineliner_03")

    def wins(b, cols, rows, hp, hs):
        w = b["fr"] - b["fl"]
        h = b["yb"] - b["yt"]
        for c0, c1 in cols:
            for f0, f1 in rows:
                window_rect(
                    s,
                    b["fl"] + c0 * w, b["fl"] + c1 * w,
                    b["yt"] + f0 * h, b["yt"] + f1 * h,
                    hp, hs, "win",
                )

    wins(L1, ((0.16, 0.42), (0.52, 0.78)), ((0.08, 0.26), (0.38, 0.56)), 0.5, 0.8)
    # L1 door: reaches the ground
    window_rect(s, 11, 19, L1["yt"] + 0.70 * (L1["yb"] - L1["yt"]), L1["yb"] - 0.6, 0.55, 0.7, "door")
    wins(L2, ((0.2, 0.5),), ((0.12, 0.32), (0.48, 0.68)), 0.40, 0.9)
    wins(R1, ((0.16, 0.42), (0.52, 0.78)), ((0.1, 0.3), (0.44, 0.64)), 0.5, 0.8)
    window_rect(s, 102.5, 107.5, R1["yt"] + 0.72 * (R1["yb"] - R1["yt"]), R1["yb"] - 0.6, 0.55, 0.7, "door")
    wins(R2, ((0.2, 0.45), (0.55, 0.8)), ((0.14, 0.34), (0.5, 0.7)), 0.40, 0.9)

    s.save()
    print("pass4 view:", s.view("pass4"))


def final() -> None:
    s = get_session()
    print("loupe:", s.view("loupe", region_mm=[30.0, 40.0, 96.0, 110.0], px_per_cell=3))
    s.note(
        "artist_statement",
        "A street in one-point perspective. The vanishing point sits in the "
        "picture, marked, and the construction rays that found it are left "
        "visible — the way etchers have always shown their working. Four "
        "buildings, every one a box with a receding face; the left-hand "
        "faces carry the shadow, hatched along lines that converge to the "
        "same point as the rooflines. The floor is transversals tightening "
        "toward the distance. Sheet 6 — the guides no longer lie.",
    )
    print("export:", s.export_artwork("street_study_06"))
    kinds = {}
    for line_txt in (DIR / "log.jsonl").read_text().splitlines():
        import json

        rec = json.loads(line_txt)
        if rec["type"] == "stroke":
            kinds["strokes"] = kinds.get("strokes", 0) + 1
        elif rec["type"] == "view":
            kinds["views"] = kinds.get("views", 0) + 1
        elif rec["type"] == "note":
            kinds["notes"] = kinds.get("notes", 0) + 1
    print("session log:", kinds)


if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else "1"
    {"1": pass1, "2": pass2, "3": pass3, "4": pass4, "final": final}[stage]()
