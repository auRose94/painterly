"""Sphere study — sheet 4. Everything sheet 3 taught, applied up front.

Fixes carried from sheet 3's log:
  - the circle is ONE continuous gesture (stroke_path), no cardinal vertices
  - terminator endpoints at 1:30/7:30 (rim parametrization: s = sqrt(R^2-o^2))
  - value plan written before hatching; darkness peaks mid-lobe
  - cast shadow attached at the contact point, foreshortened on the ground
    plane (mostly rightward), not a 45-degree stripe

Usage: python scripts/paint_sphere_04.py {1|2|3|final}
"""

import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from painterly.session import Session  # noqa: E402
from painterly.stroke import curvature_through  # noqa: E402

DIR = ROOT / "sessions" / "sphere_study_04"

C = (56.0, 74.0)
R = 26.0
U = (0.70710678, -0.70710678)  # across the light
V = (0.70710678, 0.70710678)  # along the light axis
K_LIGHT = 2.5129

# Ground plane: the sphere rests at 6:00; its shadow lies mostly rightward.
CONTACT = (C[0], C[1] + R)
DIRV = (0.974, 0.225)  # shadow direction, 13° below horizontal
PERP = (-0.225, 0.974)


def pt(o: float, s: float) -> tuple[float, float]:
    return (C[0] + o * U[0] + s * V[0], C[1] + o * U[1] + s * V[1])


def s_term(o: float) -> float:
    return math.sqrt(max(0.0, (R * R - o * o) / K_LIGHT))


def s_rim(o: float) -> float:
    return math.sqrt(max(0.0, R * R - o * o))


def get_session() -> Session:
    if (DIR / "state.json").exists():
        return Session(DIR, restore=True)
    return Session(
        DIR,
        paper_id="hot_press",
        seed=31,
        artist_id="unnamed-artist-0",
        title="Sphere at rest, light from the upper left",
    )


def report(tag: str, fb: dict) -> None:
    kinds = {}
    for e in fb["events"]:
        kinds[e["kind"]] = kinds.get(e["kind"], 0) + 1
    ev = ",".join(f"{k}×{v}" for k, v in kinds.items()) or "-"
    print(f"  [{tag:10s}] R={fb['resistance_mean_n']:.2f}N cov={fb['coverage']:.0%} {ev}")


def stroke_through(s, a, mid, b, p, tag, speed=60.0, taper=0.82):
    k = curvature_through(a, mid, b)
    report(tag, s.stroke(*a, *b, curvature=k, pressure_start=p, pressure_end=p * taper, speed_mm_s=speed, tag=tag))


def pass4() -> None:
    """Value body: the midtone between core and rim was ~8% gray; it needs
    ~25%. Dense interleaved fill at 0.75mm spacing — the reference sheets'
    midtone boxes are dense, not sparse."""
    import random

    s = get_session()
    s.select_tool("fineliner_03")
    rng = random.Random(440)

    def wob(p, amount):
        return (p[0] + rng.uniform(-amount, amount), p[1] + rng.uniform(-amount, amount))

    o = -20.4
    while o <= 20.4:
        start = s_term(o) + (3.0 if abs(o) <= 10 else 0.8)
        sr = s_rim(o) - 2.2
        if sr - start > 1.5:
            a, b = wob(pt(o, start), 0.3), wob(pt(o, sr), 0.3)
            m = wob(pt(o + rng.uniform(-0.3, 0.3), (start + sr) / 2), 0.3)
            report("value-body", s.stroke(*a, *b, curvature=curvature_through(a, m, b), pressure_start=0.18, pressure_end=0.14, speed_mm_s=80, tag="value-body"))
        o += 0.75

    s.save()
    print("pass4 view:", s.view("pass4"))


def pass1() -> None:
    s = get_session()
    s.note("material_choice", "hot-press again: same tooth, so the two sheets compare honestly")
    s.note(
        "reflection",
        "Carried fixes from sheet 3: terminator endpoints must land at 1:30/7:30 "
        "(o=±R, s=0 — last sheet cut the lobe's corners); the circle is one "
        "gesture this time, not four arcs; the shadow lies on a ground plane, "
        "foreshortened, attached at 6:00.",
    )
    s.note(
        "material_choice",
        "Value plan: midtone base over the whole lobe, fill layer between, "
        "cross-hatch peaking at mid-lobe (d≈4), soft entry at the terminator, "
        "halation at the rim. Darkness from spacing x layers, never pressure.",
    )
    s.select_tool("fineliner_03")

    # THE CIRCLE — one continuous motion, north start, counterclockwise,
    # closing with a small overlap past the start like a hand leaves.
    pts = []
    deg = 90.0
    while deg <= 452.0:
        a = math.radians(deg - 4.0 if deg > 450.0 else deg)
        pts.append((C[0] + R * math.cos(a), C[1] - R * math.sin(a)))
        deg += 15.0
    report("circle", s.stroke_path([v for p in pts for v in p], pressure=0.28, speed_mm_s=75, tag="circle-one-motion"))

    # Terminator: 1:30 -> 7:30, through its true midpoint (the sheet-3 fix).
    a, b = pt(R * 0.995, 0.0), pt(-R * 0.995, 0.0)
    stroke_through(s, a, pt(0.0, s_term(0.0)), b, 0.30, "terminator", speed=50, taper=0.9)

    s.save()
    print("pass1 view:", s.view("pass1"))


def pass2() -> None:
    s = get_session()
    s.select_tool("fineliner_03")
    rng = random.Random(808)

    def wob(p, amount):
        return (p[0] + rng.uniform(-amount, amount), p[1] + rng.uniform(-amount, amount))

    # Layer A: midtone base across the whole lobe, along the light axis.
    o = -20.0
    while o <= 20.0:
        st, sr = s_term(o) + 0.5, s_rim(o) - 2.2
        if sr - st > 1.5:
            a, b = wob(pt(o, st), 0.3), wob(pt(o, sr), 0.3)
            m = wob(pt(o + rng.uniform(-0.3, 0.3), (st + sr) / 2), 0.3)
            report("form-A", s.stroke(*a, *b, curvature=curvature_through(a, m, b), pressure_start=0.20, pressure_end=0.16, speed_mm_s=75, tag="form-A"))
        o += 2.2

    # Layer B: fill between, but only deeper than mid-lobe (spacing = value).
    o = -18.9
    while o <= 18.9:
        st, sr = s_term(o) + 0.5, min(s_rim(o) - 2.0, s_term(o) + 7.5)
        if sr - st > 1.5:
            a, b = wob(pt(o, st), 0.3), wob(pt(o, sr), 0.3)
            m = wob(pt(o + rng.uniform(-0.3, 0.3), (st + sr) / 2), 0.3)
            report("form-B", s.stroke(*a, *b, curvature=curvature_through(a, m, b), pressure_start=0.18, pressure_end=0.14, speed_mm_s=80, tag="form-B"))
        o += 2.2

    # Soft terminator entry: the shadow fades in from the light side.
    for d, omax, p in ((0.35, 17, 0.24), (0.7, 19, 0.26)):
        a, b = wob(pt(omax, s_term(omax) + d), 0.3), wob(pt(-omax, s_term(-omax) + d), 0.3)
        m = wob(pt(0.0, s_term(0.0) + d), 0.3)
        stroke_through(s, a, m, b, p, "soft-entry", speed=70)

    s.save()
    print("pass2 view:", s.view("pass2"))


def pass3() -> None:
    s = get_session()
    s.select_tool("fineliner_03")
    rng = random.Random(909)

    def wob(p, amount):
        return (p[0] + rng.uniform(-amount, amount), p[1] + rng.uniform(-amount, amount))

    # Layer C: cross-hatch arcs, darkness peaking at mid-lobe (d≈4.2).
    d = 1.1
    while d <= 7.6:
        p = 0.50 - 0.045 * abs(d - 4.2)
        omax = 0.0
        while omax < 24 and s_term(omax + 0.5) + d + 0.5 < s_rim(omax + 0.5) - 1.2:
            omax += 0.5
        if omax >= 2.0:
            a, b = wob(pt(omax, s_term(omax) + d), 0.3), wob(pt(-omax, s_term(-omax) + d), 0.3)
            m = wob(pt(0.0, s_term(0.0) + d), 0.3)
            stroke_through(s, a, m, b, p, "form-C", speed=65)
        d += 1.1

    # Core accents at the peak, short and sure.
    for d, omax, p in ((4.2, 9, 0.55), (3.4, 6, 0.50), (5.0, 6, 0.48)):
        a, b = wob(pt(omax, s_term(omax) + d), 0.3), wob(pt(-omax, s_term(-omax) + d), 0.3)
        m = wob(pt(0.0, s_term(0.0) + d), 0.3)
        stroke_through(s, a, m, b, p, "core", speed=55, taper=0.95)

    # Cast shadow: attached at the contact, foreshortened on the ground.
    length = 26.0
    l = 0.0
    while l <= length:
        frac = l / length
        half = 6.5 * max(0.08, math.sin(math.pi * min(1.0, (l + 3.0) / (length + 4.0))) ** 0.9)
        if half > 0.8:
            ctr = (CONTACT[0] + DIRV[0] * l, CONTACT[1] + DIRV[1] * l)
            a = wob((ctr[0] - PERP[0] * half, ctr[1] - PERP[1] * half), 0.3)
            b = wob((ctr[0] + PERP[0] * half, ctr[1] + PERP[1] * half), 0.3)
            p = 0.50 * math.exp(-l / 6.0) + 0.13
            report("cast", s.stroke(*a, *b, pressure_start=p, pressure_end=p * 0.9, speed_mm_s=70, tag="cast"))
        l += 1.2

    # Occlusion: darkest right at the meeting of sphere and ground.
    for l, f, p in ((0.5, 0.6, 0.62), (1.8, 0.75, 0.66), (3.2, 0.6, 0.58)):
        half = 6.5 * max(0.08, math.sin(math.pi * min(1.0, (l + 3.0) / 30.0)) ** 0.9) * f
        ctr = (CONTACT[0] + DIRV[0] * l, CONTACT[1] + DIRV[1] * l)
        a = wob((ctr[0] - PERP[0] * half, ctr[1] - PERP[1] * half), 0.25)
        b = wob((ctr[0] + PERP[0] * half, ctr[1] + PERP[1] * half), 0.25)
        report("occlusion", s.stroke(*a, *b, pressure_start=p, pressure_end=p * 0.85, speed_mm_s=60, tag="occlusion"))

    # Halation: light hatching hugging the lower rim, the bounce light.
    o = -16.0
    while o <= 2.0:
        st, sr = s_rim(o) - 3.2, s_rim(o) - 0.9
        if sr - st > 1.0:
            a, b = wob(pt(o, st), 0.25), wob(pt(o, sr), 0.25)
            report("halation", s.stroke(*a, *b, pressure_start=0.13, pressure_end=0.10, speed_mm_s=85, tag="halation"))
        o += 2.2

    s.save()
    print("pass3 view:", s.view("pass3"))


def final() -> None:
    s = get_session()
    print("loupe:", s.view("loupe", region_mm=[24.0, 42.0, 108.0, 124.0], px_per_cell=3))
    s.note(
        "artist_statement",
        "A sphere at rest on a plane, one light from the upper left. The circle "
        "is a single gesture that closes past its own beginning, the way a hand "
        "leaves a mark. Shadow planned before hatching: it peaks mid-lobe, "
        "fades into the light, lifts at the rim. The ground shadow lies "
        "foreshortened, attached where sphere meets plane. Sheet 4 — the "
        "corrections from sheet 3 carried and kept.",
    )
    print("export:", s.export_artwork("sphere_study_04"))
    kinds = {}
    for line in (DIR / "log.jsonl").read_text().splitlines():
        import json

        rec = json.loads(line)
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
