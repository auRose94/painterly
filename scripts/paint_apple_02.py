"""Apple study — sheet 2. The crown is a DEPRESSION, not a peak.

What sheet 1 taught (and the pear comparison confirmed):
  - my dimple arcs rose above the shoulders: a pear's neck. An apple's
    silhouette DIPS between shoulders, the dimple sunk inside, crown folds
    radiating down-out across the shoulders.
  - straight hatch on a curved taper leaks. The stem gets filled with
    curved-angle scribble: short strokes crossing the local spine at an
    angle, stepping along it.
  - the value-body law applied from the first tonal stroke this time.

Usage: python scripts/paint_apple_02.py {1|2|3|4|final}
"""

import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from painterly.session import Session  # noqa: E402
from painterly.stroke import curvature_through  # noqa: E402

DIR = ROOT / "sessions" / "apple_study_02b"

C = (58.0, 90.0)
RX, RY = 32.0, 28.0


def get_session() -> Session:
    if (DIR / "state.json").exists():
        return Session(DIR, restore=True)
    return Session(
        DIR,
        paper_id="hot_press",
        seed=81,
        artist_id="unnamed-artist-0",
        title="Apple, second study — the crown dips",
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
    return C[1] - RY * math.sqrt(max(0.0, 1.0 - u * u)) * 0.96


def bot_y(u):
    return C[1] + RY * math.sqrt(max(0.0, 1.0 - u * u)) * 0.99


def scribble_fill(s, spine, width_at, tag, p=0.5, step=0.55, angle_deg=28):
    """Curved-angle scribble: short strokes crossing a curved spine at an
    angle to the local tangent, stepping along it. How a hand fills a stem."""
    n = len(spine)
    for i in range(1, n):
        t = i / (n - 1)
        x, y = spine[i]
        tx, ty = spine[i][0] - spine[i - 1][0], spine[i][1] - spine[i - 1][1]
        L = math.hypot(tx, ty)
        if L < 1e-6:
            continue
        ux, uy = tx / L, ty / L
        px, py = -uy, ux
        a = math.radians(angle_deg * (1.0 if i % 2 else -1.0))
        dx = px * math.cos(a) + ux * math.sin(a)
        dy = py * math.cos(a) + uy * math.sin(a)
        w = width_at(t) * 0.9
        x0, y0 = x - dx * w / 2, y - dy * w / 2
        x1, y1 = x + dx * w / 2, y + dy * w / 2
        report(tag, s.stroke(x0, y0, x1, y1, pressure_start=p, pressure_end=p * 0.85, speed_mm_s=60, tag=tag))
        _ = step  # step is carried by the spine sampling density


def pass1() -> None:
    s = get_session()
    s.note(
        "attempt_boundary",
        "apple_study_02 rejected: tone pass crashed halfway (None guard bug "
        "in the highlight boundary), leaving state diverged from the log. "
        "Preserved; restarted clean on apple_study_02b.",
    )
    s.note(
        "reflection",
        "Sheet 1's apple grew a pear's neck: my dimple arcs rose ABOVE the "
        "shoulders. An apple's crown is a depression — shoulders rise on both "
        "sides of the stem, the silhouette dips between them, the dimple sits "
        "sunk inside, and the crown folds radiate down-and-out across the "
        "shoulders. Also: straight hatch on a curved stem leaks. The stem "
        "gets curved-angle scribble this time, and the tone starts at proper "
        "density — the value-body law from the first stroke, not pass five.",
    )
    s.select_tool("fineliner_03")

    # Construction: axis, width, shoulders-and-dip guide across the top.
    gline(s, C[0], 44, C[0], 128)
    gline(s, 24, C[1], 92, C[1])
    gline(s, 44, 62.5, 76, 60.5)   # the shoulder line — silhouette dips below
    gline(s, 54, 58.0, 68, 58.2)   # the dimple's seat, sunk inside it
    gline(s, 36, 70, 55, 92)       # highlight zone upper boundary
    gline(s, 42, 125, 84, 125)     # ground line

    # Contour: shoulders rise, silhouette DIPS to the notch, no peak.
    contour = [
        (46.0, 62.0), (35.0, 70.5), (28.0, 82.5), (26.2, 92.0), (29.8, 105.0),
        (37.5, 114.5), (48.0, 119.6), (58.0, 120.8), (67.5, 119.2),
        (76.5, 114.5), (83.5, 106.0), (87.2, 95.5), (86.6, 82.0),
        (82.2, 69.5), (75.0, 60.8), (67.0, 57.6), (59.5, 56.6),
    ]
    contour.append((48.5, 60.5))
    fb = s.stroke_path([v for p in contour for v in p], pressure=0.30, speed_mm_s=60, tag="contour")
    report("contour", fb)

    s.save()
    print("pass1 view:", s.view("pass1"))


def pass2() -> None:
    s = get_session()
    s.select_tool("fineliner_03")
    rng = random.Random(272)

    # Dimple: a depression INSIDE the shoulders — rim arcs stay below them.
    stroke_through(s, (54.0, 60.0), (61.0, 56.8), (68.5, 59.4), 0.30, "dimple", taper=0.9)
    stroke_through(s, (55.5, 61.8), (61.8, 59.6), (67.8, 61.4), 0.34, "dimple", taper=0.9)
    # interior: dark on the shadow side (right/under the stem base)
    for f, p in ((0.4, 0.42), (0.6, 0.48)):
        stroke_through(s, (65.0 + f * 2.5, 60.6), (67.0, 59.4), (68.6, 60.2), p, "dimple-dark", taper=0.9)
    stroke_through(s, (61.0, 57.6), (63.4, 58.0), (65.2, 59.4), 0.50, "under-stem", taper=0.95)

    # Crown folds radiate DOWN-and-out across the shoulders — no peak.
    for (a, m, b) in (
        ((59.5, 59.0), (56.0, 61.8), (52.0, 64.2)),
        ((62.5, 58.8), (62.2, 62.2), (60.8, 65.4)),
        ((65.8, 59.2), (67.4, 62.4), (68.6, 65.6)),
        ((68.4, 59.6), (71.0, 62.2), (73.0, 65.0)),
        ((56.2, 59.2), (53.2, 61.6), (49.8, 63.6)),
    ):
        stroke_through(s, a, m, b, 0.23, "crown", speed=55, taper=0.65)

    # Stem: spine curves slightly; filled with curved-angle scribble.
    line(s, 62.0, 55.6, 59.2, 43.0, 0.40, "stem-edge", taper=0.95)
    line(s, 64.3, 55.0, 61.0, 43.4, 0.40, "stem-edge", taper=0.95)
    spine = [(63.2, 55.2), (62.6, 52.4), (61.9, 49.6), (61.0, 47.0), (60.4, 45.2), (60.0, 43.6)]
    scribble_fill(
        s,
        spine,
        width_at=lambda t: 2.3 - 1.0 * t,
        tag="stem-fill",
        p=0.52,
    )
    report("stem-tip", s.stroke(59.9, 43.4, 60.7, 43.0, pressure_start=0.55, pressure_end=0.5, speed_mm_s=45, tag="stem"))

    s.save()
    print("pass2 view:", s.view("pass2"))


def pass3() -> None:
    s = get_session()
    s.select_tool("fineliner_03")
    rng = random.Random(838)

    def wob(p, a):
        return (p[0] + rng.uniform(-a, a), p[1] + rng.uniform(-a, a))

    def start_y(u):
        if u >= -0.15:
            return None
        return 97.0 - (u + 0.85) * (30.0 / 0.35)

    def tone_rows(u0, u1, du, frac0, frac1, p0, p1, tag, skip_above=None):
        u = u0
        while u <= u1:
            x = C[0] + u * RX * 0.98
            yt, yb = top_y(u) + 1.2, bot_y(u) - 1.6
            ya = yt + frac0 * (yb - yt)
            ybb = yt + frac1 * (yb - yt)
            if skip_above is not None:
                lim = skip_above(u)
                if lim is not None:
                    ya = max(ya, lim)
            if ybb - ya > 2.0:
                a, b, m = wob((x, ya), 0.22), wob((x, ybb), 0.22), wob((C[0] + u * RX * 1.045, (ya + ybb) / 2), 0.22)
                p = p0 + (p1 - p0) * (u - u0) / max(1e-6, u1 - u0)
                report(tag[:9], s.stroke(a[0], a[1], b[0], b[1], curvature=curvature_through(a, m, b),
                                         pressure_start=p, pressure_end=p * 0.82, speed_mm_s=85, tag=tag))
            u += du

    # L1: full body at proper density from the start — two interleaved rows.
    tone_rows(-0.9, 0.9, 0.045, 0.0, 1.0, 0.17, 0.17, "tone-L1", skip_above=start_y)
    tone_rows(-0.8725, 0.9, 0.045, 0.06, 0.94, 0.14, 0.14, "tone-L1b", skip_above=start_y)

    # L2: shadow side fill.
    tone_rows(0.28, 0.9, 0.03, 0.30, 1.0, 0.20, 0.22, "tone-L2")

    # L3: the core, tight, inset from the rim for reflected light.
    tone_rows(0.46, 0.84, 0.018, 0.25, 0.85, 0.27, 0.33, "tone-L3")

    # Bridge the terminator seam.
    tone_rows(0.33, 0.47, 0.03, 0.30, 0.80, 0.22, 0.23, "tone-bridge")

    # Darkest accents: dimple interior done in pass2; here the bottom crease
    # and the terminator's upper reach under the right shoulder.
    stroke_through(s, (57.5, 118.4), (63.0, 119.2), (68.5, 118.0), 0.42, "accent", taper=0.9)
    stroke_through(s, (77.5, 64.0), (80.2, 67.5), (82.2, 72.0), 0.40, "accent", taper=0.85)

    s.save()
    print("pass3 view:", s.view("pass3"))


def pass4() -> None:
    s = get_session()
    s.select_tool("fineliner_03")
    rng = random.Random(942)

    # Cast shadow: dense at the contact, spilling right.
    y = 122.0
    while y <= 129.5:
        x0 = 52.0 + rng.uniform(0.0, 3.0)
        x1 = 66.0 + (y - 120.5) * 2.3 + rng.uniform(0.0, 3.0)
        p = 0.34 * math.exp(-((y - 123.6) ** 2) / 14.0) + 0.10
        report("cast", s.stroke(x0, y, x1, y + rng.uniform(-0.4, 0.4),
                                pressure_start=p, pressure_end=p * 0.55, speed_mm_s=70, tag="cast"))
        y += 1.15
    line(s, 54.0, 121.6, 70.0, 122.2, 0.44, "contact", taper=0.7)
    line(s, 57.0, 122.8, 72.0, 123.2, 0.36, "contact", taper=0.7)
    fb = s.erase(82, 122.5, 96, 127.5, width_mm=4.5, strength=0.35, pattern="loop", tag="soften-cast")
    print(f"  [loop-erase ] removed={fb['removed']} damage={fb['peak_damage']}")
    # integrate the smudge into the penumbra
    y = 123.0
    while y <= 128.0:
        report("penumbra", s.stroke(80.0 + rng.uniform(-1, 1), y, 97.0 + rng.uniform(0, 3), y + rng.uniform(-0.3, 0.3),
                                    pressure_start=0.12, pressure_end=0.08, speed_mm_s=80, tag="penumbra"))
        y += 0.9

    # Lenticels: the precision rake.
    done = 0
    while done < 26:
        ang = rng.uniform(0, 2 * math.pi)
        rr = math.sqrt(rng.random())
        x = C[0] + rr * (RX - 6) * math.cos(ang)
        y = C[1] + rr * (RY - 6) * math.sin(ang)
        if x < 52 and y < 96:
            continue
        if 50 < x < 102 and 119 < y < 131:
            continue
        s.erase(x, y, x + rng.uniform(0.5, 1.1), y + rng.uniform(-0.2, 0.3),
                width_mm=0.75, strength=0.55, tag="lenticel")
        done += 1

    s.save()
    print("pass4 view:", s.view("pass4"))


def final() -> None:
    s = get_session()
    print("loupe:", s.view("loupe", region_mm=[22.0, 40.0, 106.0, 136.0], px_per_cell=2))
    s.note(
        "artist_statement",
        "An apple, second study. The first one grew a pear's neck because the "
        "dimple rose above the shoulders; here the crown dips, the dimple "
        "sits sunk inside it, and the folds radiate down the shoulders the "
        "way gravity and growth actually pull. The stem is filled with "
        "curved-angle scribble — short strokes crossing the spine at an "
        "angle, the way a hand works a taper. One light, upper left; the "
        "highlights are untouched paper; the speckles are raked back out of "
        "the tone. Second study from observation.",
    )
    print("export:", s.export_artwork("apple_study_02"))
    kinds = {}
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
            kinds["erases"] = kinds.get("erases", 0) + 1
    print("session log:", kinds)


if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else "1"
    {"1": pass1, "2": pass2, "3": pass3, "4": pass4, "final": final}[stage]()
