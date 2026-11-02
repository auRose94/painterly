"""Apple study — first drawing from observation, after the photo reference.

No vanishing points here: proportion, light, form. Following the tutorial's
arc — light construction, contour, stem and crown, tone in layers, cast
shadow — with the hand's own tools: ink hatch for value, paper kept white
for highlights, precision eraser raking pale speckles back out of the tone.

Usage: python scripts/paint_apple_01.py {1|2|3|4|final}
"""

import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from painterly.session import Session  # noqa: E402
from painterly.stroke import curvature_through  # noqa: E402

DIR = ROOT / "sessions" / "apple_study_01"

C = (56.0, 88.0)
RX, RY = 30.0, 27.0


def get_session() -> Session:
    if (DIR / "state.json").exists():
        return Session(DIR, restore=True)
    return Session(
        DIR,
        paper_id="hot_press",
        seed=71,
        artist_id="unnamed-artist-0",
        title="Apple, from the photograph",
    )


def report(tag: str, fb: dict) -> None:
    skips = sum(1 for e in fb["events"] if e["kind"] == "skip")
    print(f"  [{tag:10s}] R={fb['resistance_mean_n']:.2f}N cov={fb['coverage']:.0%} skips={skips}")


def line(s, x0, y0, x1, y1, p, tag, taper=0.95):
    report(tag, s.stroke(x0, y0, x1, y1, pressure_start=p, pressure_end=p * taper, speed_mm_s=65, tag=tag))


def gline(s, x0, y0, x1, y1, color="red", opacity=0.35, p=0.18):
    s.stroke(
        x0, y0, x1, y1, pressure_start=p, pressure_end=p, speed_mm_s=70,
        tag=f"guide-{color}", layer="guide", guide_color=color, guide_opacity=opacity,
    )


def stroke_through(s, a, mid, b, p, tag, speed=60.0, taper=0.82):
    k = curvature_through(a, mid, b)
    report(tag, s.stroke(*a, *b, curvature=k, pressure_start=p, pressure_end=p * taper, speed_mm_s=speed, tag=tag))


def top_y(u):
    """Contour top y at horizontal parameter u in [-1, 1]."""
    return C[1] - RY * math.sqrt(max(0.0, 1.0 - u * u)) * 0.96


def bot_y(u):
    return C[1] + RY * math.sqrt(max(0.0, 1.0 - u * u)) * 0.99


def pass5() -> None:
    """Continuity pass: 3.3mm spacing read as stripes with white gaps — the
    value-body lesson again, ~0.5mm perpendicular for a true midtone. Blend
    the seam with a diagonal highlight boundary; tie the eraser smudge into
    the cast shadow's penumbra."""
    import random

    s = get_session()
    s.select_tool("fineliner_03")
    rng = random.Random(515)

    def wob(p, a):
        return (p[0] + rng.uniform(-a, a), p[1] + rng.uniform(-a, a))

    def start_y(u):
        """Diagonal highlight boundary: hatching starts below it."""
        if u >= -0.15:
            return None
        return 95.0 - (u + 0.85) * (29.0 / 0.35)

    # L1b: continuity fill between the L1 columns.
    u = -0.795
    while u <= 0.9:
        x = C[0] + u * RX * 0.98
        yt, yb = top_y(u) + 1.2, bot_y(u) - 1.6
        sy = start_y(u)
        segs = [(max(yt, sy), yb)] if sy is not None else [(yt, yb)]
        if -0.55 <= u <= -0.20:
            segs = [(s0, min(s1, 90.0)) for (s0, s1) in segs if s0 < 90.0]
            segs += [(max(s0, 100.0), s1) for (s0, s1) in [(max(yt, sy or yt), yb)] if s1 > 100.0]
        for (ya, ybb) in segs:
            if ybb - ya < 2.0:
                continue
            a, b, m = wob((x, ya), 0.25), wob((x, ybb), 0.25), wob((C[0] + u * RX * 1.045, (ya + ybb) / 2), 0.25)
            report("L1b", s.stroke(a[0], a[1], b[0], b[1], curvature=curvature_through(a, m, b),
                                   pressure_start=0.16, pressure_end=0.13, speed_mm_s=85, tag="tone-L1b"))
        u += 0.055

    # L2b: shadow-side fill at half the L2 spacing.
    u = 0.30
    while u <= 0.9:
        x = C[0] + u * RX * 0.98
        frac0 = 0.40 if u < 0.55 else 0.26
        yt, yb = top_y(u) + 1.2, bot_y(u) - 1.6
        ya = yt + frac0 * (yb - yt)
        if yb - ya > 2.0:
            a, b = wob((x, ya), 0.22), wob((x, yb), 0.22)
            m = wob((C[0] + u * RX * 1.045, (ya + yb) / 2), 0.22)
            report("L2b", s.stroke(a[0], a[1], b[0], b[1], curvature=curvature_through(a, m, b),
                                   pressure_start=0.20, pressure_end=0.16, speed_mm_s=80, tag="tone-L2b"))
        u += 0.0275

    # L3b: tighten the core band into a real gradient.
    u = 0.40
    while u <= 0.86:
        x = C[0] + u * RX * 0.98
        yt, yb = top_y(u) + 3.0, bot_y(u) - 4.5
        ya, ybb = yt + 0.25 * (yb - yt), yt + 0.85 * (yb - yt)
        if ybb - ya > 2.0:
            a, b = wob((x, ya), 0.2), wob((x, ybb), 0.2)
            m = wob((C[0] + u * RX * 1.045, (ya + ybb) / 2), 0.2)
            p = 0.26 + 0.06 * math.sin((u - 0.40) / 0.46 * math.pi)
            report("L3b", s.stroke(a[0], a[1], b[0], b[1], curvature=curvature_through(a, m, b),
                                   pressure_start=p, pressure_end=p * 0.8, speed_mm_s=75, tag="tone-L3b"))
        u += 0.016

    # Bridge L2->L3 so no white seam survives between body and core.
    u = 0.33
    while u <= 0.52:
        x = C[0] + u * RX * 0.98
        yt, yb = top_y(u) + 2.0, bot_y(u) - 3.0
        a, b = wob((x, yt + 0.3 * (yb - yt)), 0.2), wob((x, yt + 0.8 * (yb - yt)), 0.2)
        m = wob((C[0] + u * RX * 1.045, (a[1] + b[1]) / 2), 0.2)
        report("bridge", s.stroke(a[0], a[1], b[0], b[1], curvature=curvature_through(a, m, b),
                                  pressure_start=0.24, pressure_end=0.19, speed_mm_s=78, tag="tone-bridge"))
        u += 0.035

    # Tie the loop-eraser smudge into the cast shadow: sparse penumbra hatch
    # reaching through it, so it reads as the shadow's soft edge.
    y = 119.5
    while y <= 124.5:
        report("penumbra", s.stroke(78.0 + rng.uniform(-1, 1), y, 95.0 + rng.uniform(0, 3), y + rng.uniform(-0.3, 0.3),
                                    pressure_start=0.13, pressure_end=0.08, speed_mm_s=80, tag="penumbra"))
        y += 0.9

    s.save()
    print("pass5 view:", s.view("pass5"))


def pass1() -> None:
    s = get_session()
    s.note(
        "reflection",
        "Observation before marks: the apple is squat — wider than tall, "
        "width:height about 1.1:1. Stem rises up-and-LEFT from a deep dimple "
        "top-center, with crown folds radiating from it. One light, upper "
        "left: big highlight streaks on the upper-left cheek (the paper stays "
        "white there), form shadow wraps the right side past a terminator "
        "running from the dimple's right rim down to the bottom, reflected "
        "light hugs the lower-right rim, cast shadow spills right on the "
        "ground. Pale speckles in the tone are the fruit's lenticels.",
    )
    s.note(
        "material_choice",
        "Hot-press again — tonal hatching is the game and even tooth serves "
        "it. Values from line density, never pressure alone.",
    )
    s.select_tool("fineliner_03")

    # Red construction: axis, width, envelope, dimple, highlight, ground.
    gline(s, C[0], 40, C[0], 124)
    gline(s, 24, C[1], 90, C[1])
    q = 0.7071
    pts = [(C[0] - RX, C[1]), (C[0] - RX * q, C[1] - RY * q), (C[0], C[1] - RY),
           (C[0] + RX * q, C[1] - RY * q), (C[0] + RX, C[1]), (C[0] + RX * q, C[1] + RY * q),
           (C[0], C[1] + RY), (C[0] - RX * q, C[1] + RY * q)]
    for i in range(0, 8, 2):
        a, b = pts[i], pts[(i + 2) % 8]
        s.stroke(*a, *b, curvature=curvature_through(a, pts[(i + 1) % 8], b),
                 pressure_start=0.18, pressure_end=0.18, speed_mm_s=70,
                 tag="guide-red", layer="guide", guide_color="red", guide_opacity=0.35)
    gline(s, 52, 57, 71, 56.4)  # dimple rim axis
    gline(s, 33, 66, 52, 88)    # highlight zone upper boundary
    gline(s, 40, 121, 82, 121)  # ground / contact line

    # Contour: one continuous measured gesture, slightly irregular —
    # fuller left cheek, two subtle bottom lobes, shoulders into the dimple.
    contour = [
        (43.0, 63.5), (33.0, 71.0), (27.5, 82.0), (26.5, 91.0), (29.5, 103.0),
        (36.5, 112.0), (46.0, 117.8), (55.0, 119.2), (64.0, 118.6),
        (72.5, 115.0), (80.5, 107.0), (85.5, 96.0), (86.2, 85.0),
        (83.5, 73.0), (77.0, 62.5), (69.0, 55.8), (63.5, 53.8),
    ]
    contour.append((46.5, 61.0))  # overlap past the start, the way hands close
    fb = s.stroke_path([v for p in contour for v in p], pressure=0.30, speed_mm_s=60, tag="contour")
    report("contour", fb)

    s.save()
    print("pass1 view:", s.view("pass1"))


def pass2() -> None:
    s = get_session()
    s.select_tool("fineliner_03")
    rng = random.Random(171)

    # Dimple: the depression's rim arcs and its dark right interior.
    stroke_through(s, (52.5, 58.5), (61.5, 52.2), (71.0, 58.0), 0.30, "dimple", taper=0.9)
    stroke_through(s, (54.5, 61.0), (62.0, 57.4), (69.5, 60.6), 0.34, "dimple", taper=0.9)
    for f, p in ((0.35, 0.40), (0.55, 0.46)):
        stroke_through(s, (65.5 + f * 3, 58.2), (67.5 + f * 2, 56.4), (70.5, 57.6), p, "dimple-dark", taper=0.9)

    # Crown folds: ridges radiating from the rim toward the stem.
    for (a, m, b) in (
        ((55.0, 60.0), (58.0, 56.5), (60.0, 54.6)),
        ((59.5, 61.2), (62.0, 57.8), (63.5, 54.8)),
        ((64.5, 60.8), (66.0, 57.6), (66.8, 55.0)),
        ((68.0, 59.6), (69.0, 57.0), (69.2, 55.4)),
        ((51.5, 57.4), (54.5, 55.4), (58.0, 54.2)),
    ):
        stroke_through(s, a, m, b, 0.24, "crown", speed=55, taper=0.65)

    # Stem: two edges tapering up-left, dense fill, dark tip.
    stroke_through(s, (62.2, 55.2), (60.6, 48.0), (58.9, 42.4), 0.42, "stem", speed=45, taper=0.95)
    stroke_through(s, (64.4, 54.6), (62.8, 47.6), (60.9, 43.0), 0.42, "stem", speed=45, taper=0.95)
    x = 61.3
    while x <= 63.2:
        t0, t1 = 0.12 + rng.random() * 0.1, 0.88 - rng.random() * 0.08
        ya, yb = 55.2 - t0 * 12.6, 55.2 - t1 * 12.6
        report("stem-fill", s.stroke(x, ya, x - 0.35, yb, pressure_start=0.5, pressure_end=0.42, speed_mm_s=60, tag="stem"))
        x += 0.45
    report("stem-tip", s.stroke(59.5, 43.4, 60.4, 42.6, pressure_start=0.55, pressure_end=0.5, speed_mm_s=45, tag="stem"))

    s.save()
    print("pass2 view:", s.view("pass2"))


def pass3() -> None:
    s = get_session()
    s.select_tool("fineliner_03")
    rng = random.Random(737)

    def wob(p, a):
        return (p[0] + rng.uniform(-a, a), p[1] + rng.uniform(-a, a))

    # L1: form-following longitude hatch over the whole body, light.
    # Highlight kept white: upper-left cheek (u < -0.30) hatches only below
    # y=88; the secondary streak (u in [-0.55,-0.20]) skips y 90..100.
    u = -0.85
    while u <= 0.85:
        x = C[0] + u * RX * 0.98
        yt, yb = top_y(u) + 1.2, bot_y(u) - 1.6
        mid = (C[0] + u * RX * 1.045, C[1])
        segs = []
        if u < -0.30:
            if yb > 88.5:
                segs.append((max(yt, 88.5), yb))
        elif -0.55 <= u <= -0.20:
            if yt < 90.0:
                segs.append((yt, 90.0))
            if yb > 100.0:
                segs.append((100.0, yb))
        else:
            segs.append((yt, yb))
        for (ya, ybb) in segs:
            if ybb - ya < 2.0:
                continue
            a, b, m = wob((x, ya), 0.25), wob((x, ybb), 0.25), wob(mid, 0.25)
            report("tone-L1", s.stroke(a[0], a[1], b[0], b[1], curvature=curvature_through(a, m, b),
                                       pressure_start=0.17, pressure_end=0.14, speed_mm_s=80, tag="tone-L1"))
        u += 0.11

    # L2: fill pass on the shadow side only, between the L1 lines.
    u = 0.28
    while u <= 0.9:
        x = C[0] + u * RX * 0.98
        frac0 = 0.42 if u < 0.55 else 0.28
        yt, yb = top_y(u) + 1.2, bot_y(u) - 1.6
        ya = yt + frac0 * (yb - yt)
        if yb - ya > 2.0:
            a, b = wob((x, ya), 0.25), wob((x, yb), 0.25)
            m = wob((C[0] + u * RX * 1.045, (ya + yb) / 2), 0.25)
            report("tone-L2", s.stroke(a[0], a[1], b[0], b[1], curvature=curvature_through(a, m, b),
                                       pressure_start=0.22, pressure_end=0.18, speed_mm_s=75, tag="tone-L2"))
        u += 0.055

    # L3: the core — tight spacing mid-right, inset from the rim so the
    # reflected light survives.
    u = 0.48
    while u <= 0.82:
        x = C[0] + u * RX * 0.98
        yt, yb = top_y(u) + 3.0, bot_y(u) - 4.5
        frac0, frac1 = 0.25, 0.85
        ya, ybb = yt + frac0 * (yb - yt), yt + frac1 * (yb - yt)
        if ybb - ya > 2.0:
            a, b = wob((x, ya), 0.2), wob((x, ybb), 0.2)
            m = wob((C[0] + u * RX * 1.045, (ya + ybb) / 2), 0.2)
            p = 0.30 + 0.05 * math.sin((u - 0.48) / 0.34 * math.pi)
            report("tone-L3", s.stroke(a[0], a[1], b[0], b[1], curvature=curvature_through(a, m, b),
                                       pressure_start=p, pressure_end=p * 0.8, speed_mm_s=75, tag="tone-L3"))
        u += 0.024

    # L4: darkest accents — under the dimple's right overhang, the bottom
    # crease between the lobes, and the terminator's upper reach.
    stroke_through(s, (68.0, 60.4), (70.5, 62.5), (72.2, 66.0), 0.44, "accent", taper=0.9)
    stroke_through(s, (56.0, 116.6), (61.5, 117.4), (66.5, 116.2), 0.42, "accent", taper=0.9)
    stroke_through(s, (76.5, 63.0), (79.5, 66.5), (81.8, 71.0), 0.40, "accent", taper=0.85)

    s.save()
    print("pass3 view:", s.view("pass3"))


def pass4() -> None:
    s = get_session()
    s.select_tool("fineliner_03")
    rng = random.Random(941)

    # Cast shadow: dense at the contact, spilling right and softening.
    y = 118.6
    while y <= 126.0:
        x0 = 50.0 + rng.uniform(0.0, 3.0)
        x1 = 64.0 + (y - 117.0) * 2.4 + rng.uniform(0.0, 3.0)
        p = 0.34 * math.exp(-((y - 120.2) ** 2) / 14.0) + 0.10
        report("cast", s.stroke(x0, y, x1, y + rng.uniform(-0.4, 0.4),
                                pressure_start=p, pressure_end=p * 0.55, speed_mm_s=70, tag="cast"))
        y += 1.15
    # contact dark right under the fruit
    line(s, 52.0, 118.2, 68.0, 118.8, 0.44, "contact", taper=0.7)
    line(s, 55.0, 119.4, 70.0, 119.8, 0.36, "contact", taper=0.7)
    # soften the far fringe with looping lifts — the eraser as a soft brush
    fb = s.erase(80, 119, 94, 124, width_mm=4.5, strength=0.4, pattern="loop", tag="soften-cast")
    print(f"  [loop-erase ] removed={fb['removed']} damage={fb['peak_damage']}")

    # Lenticels: the precision rake. Tiny narrow dabs pull pale dots back
    # out of the midtone and shadow — never through the highlight paper.
    done = 0
    while done < 26:
        ang = rng.uniform(0, 2 * math.pi)
        rr = math.sqrt(rng.random())
        x = C[0] + rr * (RX - 6) * math.cos(ang)
        y = C[1] + rr * (RY - 6) * math.sin(ang)
        if x < 50 and y < 92:  # keep out of the highlight zones
            done += 1
            continue
        if 49 < x < 100 and 116 < y < 128:  # not on the cast shadow's face
            continue
        fb = s.erase(x, y, x + rng.uniform(0.5, 1.1), y + rng.uniform(-0.2, 0.3),
                     width_mm=0.75, strength=0.55, tag="lenticel")
        done += 1

    s.save()
    print("pass4 view:", s.view("pass4"))


def final() -> None:
    s = get_session()
    print("loupe:", s.view("loupe", region_mm=[22.0, 40.0, 102.0, 132.0], px_per_cell=2))
    s.note(
        "artist_statement",
        "An apple, drawn from the photograph. No perspective tricks to hold "
        "onto — proportion, one light, and the patience to build tone from "
        "line density. The highlights are the untouched paper; the shadow "
        "wraps the right side and spills onto the ground; the speckles are "
        "lifted back out of the tone with the eraser's point, a rake pulling "
        "pigment. First study from observation. The stem leans the way the "
        "apple grew.",
    )
    print("export:", s.export_artwork("apple_study"))
    kinds = {}
    erases = {}
    for line_txt in (DIR / "log.jsonl").read_text().splitlines():
        import json

        rec = json.loads(line_txt)
        if rec["type"] == "stroke":
            kinds["strokes"] = kinds.get("strokes", 0) + 1
            if rec["params"].get("layer") == "guide":
                kinds["guides"] = kinds.get("guides", 0) + 1
        elif rec["type"] == "view":
            kinds["views"] = kinds.get("views", 0) + 1
        elif rec["type"] == "note":
            kinds["notes"] = kinds.get("notes", 0) + 1
        elif rec["type"] == "erase":
            pat = rec["params"].get("pattern", "linear")
            erases[pat] = erases.get(pat, 0) + 1
    print(f"session log: {kinds}, erase patterns: {erases}")


if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else "1"
    {"1": pass1, "2": pass2, "3": pass3, "4": pass4, "5": pass5, "final": final}[stage]()
