"""Sphere study — sheet 3. Reference-informed hatching.

Craft rules taken from hatching reference sheets:
  one direction per layer; each layer jumps the angle; value = spacing x
  layers, not pressure; strokes follow the form; ends taper.

Usage: python scripts/paint_sphere.py {1|2|3|final}
"""

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from painterly.session import Session  # noqa: E402
from painterly.stroke import curvature_through  # noqa: E402

DIR = ROOT / "sessions" / "sphere_study_03"

# Sphere geometry (mm). Light from the upper left at 45°.
C = (56.0, 74.0)
R = 26.0
U = (0.70710678, -0.70710678)  # across the light
V = (0.70710678, 0.70710678)  # along the light axis
K_LIGHT = 2.5129


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
        seed=23,
        artist_id="unnamed-artist-0",
        title="Sphere, light from the upper left",
    )


def report(tag: str, fb: dict) -> None:
    kinds = {}
    for e in fb["events"]:
        kinds[e["kind"]] = kinds.get(e["kind"], 0) + 1
    ev = ",".join(f"{k}×{v}" for k, v in kinds.items()) or "-"
    print(f"  [{tag:10s}] R={fb['resistance_mean_n']:.2f}N cov={fb['coverage']:.0%} {ev}")


def stroke_through(
    s: Session, a, mid, b, p: float, tag: str, speed: float = 60.0, taper: float = 0.82
) -> None:
    """A stroke planned by three points, ends feathered lighter."""
    k = curvature_through(a, mid, b)
    report(tag, s.stroke(*a, *b, curvature=k, pressure_start=p, pressure_end=p * taper, speed_mm_s=speed, tag=tag))


def pass1() -> None:
    s = get_session()
    s.note(
        "attempt_boundary",
        "Attempt 2 rejected: cast-shadow chords were collinear (minor-axis "
        "offset missing) and cross-hatch bow over-deep, escaping the rim. "
        "Added arc-through planning; restarting clean on sheet 3.",
    )
    s.note("material_choice", "hot-press: even tooth for tonal hatching; this study is about value, not texture")
    s.select_tool("fineliner_03")

    # Contour: quadrant arcs planned through their 45° points.
    q = R * 0.70710678
    arcs = [
        ((C[0] + R, C[1]), (C[0] + q, C[1] - q), (C[0], C[1] - R)),
        ((C[0], C[1] - R), (C[0] - q, C[1] - q), (C[0] - R, C[1])),
        ((C[0] - R, C[1]), (C[0] - q, C[1] + q), (C[0], C[1] + R)),
        ((C[0], C[1] + R), (C[0] + q, C[1] + q), (C[0] + R, C[1])),
    ]
    for i, (a, m, b) in enumerate(arcs):
        p = 0.42 if i == 3 else 0.30  # heavier on the shadow side
        stroke_through(s, a, m, b, p, "contour", speed=60, taper=0.94)

    # Terminator: rim at ~1:30 to rim at ~7:30, through its true midpoint.
    o = R * 0.70710678
    a, b = pt(o, s_rim(o) * 0.995), pt(-o, s_rim(o) * 0.995)
    stroke_through(s, a, pt(0.0, s_term(0.0)), b, 0.30, "terminator", speed=50, taper=0.9)

    s.save()
    print("pass1 view:", s.view("pass1"))


def pass2() -> None:
    s = get_session()
    s.select_tool("fineliner_03")

    # L1: straight hatch along the light axis (45° down-right), spacing 2.5mm,
    # spanning terminator -> near rim. Ends taper; pressure modest.
    o = -20.0
    while o <= 20.0:
        st, sr = s_term(o) + 0.8, s_rim(o) - 2.5
        if sr - st > 3.0:
            a, b = pt(o, st), pt(o, sr)
            report("form-L1", s.stroke(*a, *b, curvature=0.0, pressure_start=0.22, pressure_end=0.17, speed_mm_s=75, tag="form-L1"))
        o += 2.5

    # L2: cross-hatch, terminator-following arcs (the angle jump), confined to
    # the shadow half, tighter spacing toward the core.
    for d, omax, p in ((1.3, 20, 0.38), (2.6, 18, 0.38), (4.1, 15, 0.35), (5.8, 11, 0.32)):
        a, b = pt(omax, s_term(omax) + d), pt(-omax, s_term(-omax) + d)
        stroke_through(s, a, pt(0.0, s_term(0.0) + d), b, p, "form-L2", speed=65)

    # Cast shadow: ellipse beyond the contact point, chords slid along V,
    # dark near the sphere, feathering away.
    contact = (C[0] + V[0] * (R + 1.0), C[1] + V[1] * (R + 1.0))
    A, Bc = 17.0, 6.0
    ss = -Bc
    while ss <= Bc:
        half = A * math.sqrt(max(0.0, 1.0 - (ss / Bc) ** 2))
        if half > 2.0:
            ctr = (contact[0] + V[0] * (ss + 2.0), contact[1] + V[1] * (ss + 2.0))
            a = (ctr[0] - U[0] * half, ctr[1] - U[1] * half)
            b = (ctr[0] + U[0] * half, ctr[1] + U[1] * half)
            p = 0.46 * math.exp(-((ss + 3.5) ** 2) / 9.0) + 0.14
            report("cast", s.stroke(*a, *b, pressure_start=p, pressure_end=p * 0.9, speed_mm_s=70, tag="cast"))
        ss += 1.4

    s.save()
    print("pass2 view:", s.view("pass2"))


def pass4() -> None:
    """Deepening pass: the artist steps back, judges the values too timid,
    and builds density — ink only adds."""
    import random

    s = get_session()
    s.select_tool("fineliner_03")
    rng = random.Random(409)

    def wob(p, amount):
        return (p[0] + rng.uniform(-amount, amount), p[1] + rng.uniform(-amount, amount))

    # L1b: fill between the sparse first-layer lines (1.3mm offset), wobbled.
    o = -21.25
    while o <= 21.25:
        st, sr = s_term(o) + 0.6, s_rim(o) - 1.8
        if sr - st > 1.5:
            a, b = wob(pt(o, st), 0.35), wob(pt(o, sr), 0.35)
            m = wob(pt(o + rng.uniform(-0.3, 0.3), (st + sr) / 2), 0.3)
            report("form-L1b", s.stroke(*a, *b, curvature=curvature_through(a, m, b), pressure_start=0.20, pressure_end=0.16, speed_mm_s=75, tag="form-L1b"))
        o += 1.3

    # L2b: deepen toward the core — arcs at depths the mesh hasn't reached,
    # spans fitted to the shrinking lobe so they stay inside the form.
    for d in (6.8, 7.8, 8.7, 9.4):
        omax = 0.0
        while omax < 24 and s_term(omax + 0.5) + d + 0.5 < s_rim(omax + 0.5) - 1.2:
            omax += 0.5
        if omax < 2.0:
            continue
        a, b = wob(pt(omax, s_term(omax) + d), 0.3), wob(pt(-omax, s_term(-omax) + d), 0.3)
        m = wob(pt(0.0, s_term(0.0) + d), 0.3)
        p = 0.34 + 0.02 * (d - 6.8)
        stroke_through(s, a, m, b, p, "form-L2b", speed=65)

    # L4: short cross accents along U, deep in the core, third angle.
    for d in (3.0, 4.5, 6.0, 7.5):
        for oo in (-6.0, 0.0, 6.0):
            half = 4.0
            a = wob(pt(oo - half, s_term(oo - half) + d), 0.3)
            b = wob(pt(oo + half, s_term(oo + half) + d), 0.3)
            m = wob(pt(oo, s_term(oo) + d), 0.3)
            stroke_through(s, a, m, b, 0.28, "form-L4", speed=70)

    # Cast shadow: anchor to the contact point, extend the wedge, deepen near.
    contact = (C[0] + V[0] * (R + 1.0), C[1] + V[1] * (R + 1.0))
    for ss, p in ((-5.2, 0.56), (-4.4, 0.60), (-3.6, 0.58), (-2.8, 0.52), (-2.0, 0.46), (-1.2, 0.40), (7.0, 0.14), (8.0, 0.10)):
        half = 17.0 * math.sqrt(max(0.0, 1.0 - (min(abs(ss), 6.0) / 6.0) ** 2)) * (1.0 + 0.03 * max(0.0, ss))
        ctr = (contact[0] + V[0] * (ss + 2.0), contact[1] + V[1] * (ss + 2.0))
        a = wob((ctr[0] - U[0] * half, ctr[1] - U[1] * half), 0.3)
        b = wob((ctr[0] + U[0] * half, ctr[1] + U[1] * half), 0.3)
        report("cast-deep", s.stroke(*a, *b, pressure_start=p, pressure_end=p * 0.85, speed_mm_s=70, tag="cast-deep"))

    s.save()
    print("pass4 view:", s.view("pass4"))


def pass5() -> None:
    """Final tonal pass: interleave half-spacing midtone lines and bridge the
    reflected-light rim with a soft halation."""
    import random

    s = get_session()
    s.select_tool("fineliner_03")
    rng = random.Random(777)

    def wob(p, amount):
        return (p[0] + rng.uniform(-amount, amount), p[1] + rng.uniform(-amount, amount))

    # L1c: half-spacing fill across the whole lobe — the midtone body.
    o = -20.6
    while o <= 20.6:
        st, sr = s_term(o) + 0.5, s_rim(o) - 1.6
        if sr - st > 1.2:
            a, b = wob(pt(o, st), 0.3), wob(pt(o, sr), 0.3)
            m = wob(pt(o + rng.uniform(-0.25, 0.25), (st + sr) / 2), 0.25)
            report("form-L1c", s.stroke(*a, *b, curvature=curvature_through(a, m, b), pressure_start=0.17, pressure_end=0.14, speed_mm_s=80, tag="form-L1c"))
        o += 0.65

    # Halation: light hatching hugging the lower-left rim, fading to nothing
    # — the bounce light turning up at the edge of the form.
    o = -16.0
    while o <= 2.0:
        st, sr = s_rim(o) - 3.2, s_rim(o) - 0.9
        if sr - st > 1.0:
            a, b = wob(pt(o, st), 0.25), wob(pt(o, sr), 0.25)
            report("halation", s.stroke(*a, *b, pressure_start=0.13, pressure_end=0.10, speed_mm_s=85, tag="halation"))
        o += 2.2

    s.save()
    print("pass5 view:", s.view("pass5"))


def pass6() -> None:
    """Judgment pass: the darkest zone must sit mid-lobe and ease both ways.
    Soften the terminator entry; pull the core to the shadow's middle; log the
    terminator-endpoint error for the next sheet."""
    import random

    s = get_session()
    s.select_tool("fineliner_03")
    rng = random.Random(1010)

    def wob(p, amount):
        return (p[0] + rng.uniform(-amount, amount), p[1] + rng.uniform(-amount, amount))

    s.note(
        "reflection",
        "Value critique: darkest band hugged the terminator with hard edges, "
        "and the drawn terminator's endpoints landed at 3:00/6:00 instead of "
        "1:30/7:30 (rim parametrization error — cuts the lobe's corners). "
        "Ink cannot erase; softening the entry, pulling the core mid-lobe, "
        "and carrying the endpoint fix to the next sheet.",
    )

    # Soft terminator entry: the shadow edge fades in, it doesn't start hard.
    for d, omax, p in ((0.35, 17, 0.24), (0.7, 19, 0.26)):
        a = wob(pt(omax, s_term(omax) + d), 0.3)
        b = wob(pt(-omax, s_term(-omax) + d), 0.3)
        m = wob(pt(0.0, s_term(0.0) + d), 0.3)
        stroke_through(s, a, m, b, p, "soft-entry", speed=70)

    # Core shift: darkness peaks mid-lobe, easing both directions.
    for d, omax, p in ((3.6, 17, 0.44), (4.6, 15, 0.47), (5.6, 12, 0.44)):
        a = wob(pt(omax, s_term(omax) + d), 0.3)
        b = wob(pt(-omax, s_term(-omax) + d), 0.3)
        m = wob(pt(0.0, s_term(0.0) + d), 0.3)
        stroke_through(s, a, m, b, p, "core-shift", speed=65)

    s.save()
    print("pass6 view:", s.view("pass6"))


def pass3() -> None:
    s = get_session()
    s.select_tool("fineliner_03")

    # L3: staggered third layer between the L1 lines, core half only.
    o = -18.75
    while o <= 18.75:
        st, sr = s_term(o) + 0.8, s_rim(o) - 2.5
        if sr - st > 2.0 and st < s_term(0.0) + 3.0:
            end = min(sr, s_term(0.0) + 6.0)
            if end - st > 2.0:
                a, b = pt(o, st), pt(o, end)
                report("form-L3", s.stroke(*a, *b, curvature=0.0, pressure_start=0.30, pressure_end=0.24, speed_mm_s=70, tag="form-L3"))
        o += 5.0

    # Core accents: two deep arcs hugging the terminator inside.
    for d, omax, p in ((0.9, 10, 0.55), (2.3, 7, 0.62)):
        a, b = pt(omax, s_term(omax) + d), pt(-omax, s_term(-omax) + d)
        stroke_through(s, a, pt(0.0, s_term(0.0) + d), b, p, "core", speed=55, taper=0.95)

    # Rim turn at ~4:30: the edge rotates away from the light.
    r1 = (C[0] + U[0] * 0.34 * R + V[0] * 0.94 * R, C[1] + U[1] * 0.34 * R + V[1] * 0.94 * R)
    r2 = (C[0] + U[0] * 0.94 * R + V[0] * 0.34 * R, C[1] + U[1] * 0.94 * R + V[1] * 0.34 * R)
    n = math.hypot(r1[0] + r2[0] - 2 * C[0], r1[1] + r2[1] - 2 * C[1])
    m = (C[0] + (r1[0] + r2[0] - 2 * C[0]) / n * 0.96 * R, C[1] + (r1[1] + r2[1] - 2 * C[1]) / n * 0.96 * R)
    stroke_through(s, r1, m, r2, 0.32, "rim", speed=60, taper=0.9)

    # Occlusion: darkest right where sphere meets its shadow, chords offset.
    contact = (C[0] + V[0] * (R + 1.0), C[1] + V[1] * (R + 1.0))
    for ss, f, p in ((-3.6, 0.55, 0.66), (-2.2, 0.72, 0.70), (-0.8, 0.60, 0.62)):
        half = 17.0 * math.sqrt(max(0.0, 1.0 - (ss / 6.0) ** 2)) * f
        ctr = (contact[0] + V[0] * (ss + 2.0), contact[1] + V[1] * (ss + 2.0))
        a = (ctr[0] - U[0] * half, ctr[1] - U[1] * half)
        b = (ctr[0] + U[0] * half, ctr[1] + U[1] * half)
        report("occlusion", s.stroke(*a, *b, pressure_start=p, pressure_end=p * 0.85, speed_mm_s=60, tag="occlusion"))

    s.save()
    print("pass3 view:", s.view("pass3"))


def final() -> None:
    s = get_session()
    # The loupe before signing: detail check of the sphere region.
    print("loupe:", s.view("loupe", region_mm=[24.0, 42.0, 104.0, 122.0], px_per_cell=3))
    s.note(
        "artist_statement",
        "A sphere under one light. Ink cannot smear or erase, so value is built "
        "from line density alone: one direction per layer, the angle jumps each "
        "layer, spacing carries the darkness. The reflected light is the paper "
        "itself, kept unhatched. Third sheet — the first two taught the hand "
        "where its arcs actually land.",
    )
    print("export:", s.export_artwork("sphere_study"))
    kinds = {}
    for line in (DIR / "log.jsonl").read_text().splitlines():
        rec = json.loads(line)
        if rec["type"] == "stroke":
            kinds["strokes"] = kinds.get("strokes", 0) + 1
        elif rec["type"] == "view":
            kinds["views"] = kinds.get("views", 0) + 1
        elif rec["type"] == "note":
            kinds["notes"] = kinds.get("notes", 0) + 1
    print("session log:", kinds)


if __name__ == "__main__":
    import json

    stage = sys.argv[1] if len(sys.argv) > 1 else "1"
    {"1": pass1, "2": pass2, "3": pass3, "4": pass4, "5": pass5, "6": pass6, "final": final}[stage]()
