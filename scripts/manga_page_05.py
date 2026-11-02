"""Manga page 5 — no stick figures. Masses, contact, and clean balloons.

From the reference pages and the user's critique:
  - distant crew are SOLID SILHOUETTES (dark masses with head + shoulders +
    legs), never sticks; the bulwark is drawn OVER them (they stand behind it)
  - Zoro's three swords are drawn as swords: three blades, cross guards,
    hilts, at his left hip where the eye can find them
  - Nami is simplified to what survives a bust: hair mass, ring-eye, shoulders
  - the balloon interior is white-out in FULL coverage after all panel art —
    no stroke may cross the script
  - gulls are 'm' curves placed away from balloons; no egg-under-cloud
  - no erasure smudges on open sea

Character designs © Eiichiro Oda / Shueisha — disclosed fan study.

Usage: python scripts/manga_page_05.py {1|2|3|4|final}
"""

import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from painterly.fonts import stamp_text, text_width_mm  # noqa: E402
from painterly.session import Session  # noqa: E402
from painterly.stroke import curvature_through  # noqa: E402

DIR = ROOT / "sessions" / "manga_page_05"

PANELS = {
    "P1": (12.0, 12.0, 164.0, 96.0),
    "P2": (12.0, 104.0, 86.0, 164.0),
    "P3": (94.0, 104.0, 164.0, 164.0),
    "P4": (12.0, 172.0, 164.0, 236.0),
}

LW = {"outline": 0.58, "struct": 0.40, "detail": 0.22, "bg": 0.15}


def get_session() -> Session:
    if (DIR / "state.json").exists():
        return Session(DIR, restore=True)
    return Session(
        DIR,
        paper_id="hot_press",
        seed=141,
        size_mm=(176.0, 250.0),
        cell_mm=0.2,
        artist_id="unnamed-artist-0",
        title="Going Merry — fan study, silhouettes and letterpress",
    )


def lw_line(s, x0, y0, x1, y1, level, tag, taper=0.96, passes=1):
    p = LW[level]
    for _ in range(passes):
        s.stroke(x0, y0, x1, y1, pressure_start=p, pressure_end=p * taper, speed_mm_s=70, tag=tag)


def stroke_through(s, a, mid, b, p, tag, speed=60.0, taper=0.88, passes=1):
    k = curvature_through(a, mid, b)
    for _ in range(passes):
        s.stroke(*a, *b, curvature=k, pressure_start=p, pressure_end=p * taper, speed_mm_s=speed, tag=tag)


def tone(s, x0, y0, x1, y1, pitch=1.0, p=0.30, skip=0.55, seed=0, tag="tone"):
    rng = random.Random(seed)
    row = 0
    y = y0
    while y <= y1:
        off = (pitch / 2) if row % 2 else 0.0
        x = x0 + off
        while x <= x1:
            if rng.random() > skip:
                s.stroke(x, y, x + 0.26, y + 0.16, pressure_start=p, pressure_end=p * 0.9,
                         speed_mm_s=90, tag=tag)
            x += pitch
        y += pitch
        row += 1


def dot_fill(s, cx, cy, rx, ry, p, tag, seed, skip=(), pitch=None):
    rng = random.Random(seed)
    pitch = pitch or (min(rx, ry) * 0.55)
    y = cy - ry
    while y <= cy + ry:
        x = cx - rx
        while x <= cx + rx:
            if (x - cx) ** 2 / max(rx * rx, 1e-6) + (y - cy) ** 2 / max(ry * ry, 1e-6) <= 1.0:
                if any((x - hx) ** 2 + (y - hy) ** 2 <= hr * hr for hx, hy, hr in skip):
                    x += pitch
                    continue
                jx, jy = rng.uniform(-0.05, 0.05), rng.uniform(-0.05, 0.05)
                s.stroke(x + jx, y + jy, x + jx + pitch * 0.62, y + jy + pitch * 0.36,
                         pressure_start=p, pressure_end=p * 0.9, speed_mm_s=90, tag=tag)
            x += pitch
        y += pitch * 0.8


def silhouette_figure(s, x, feet_y, h, tag, hat=False, spiky=False):
    """A distant crew member as the reference shows them: a SOLID dark
    silhouette with head, shoulders, waist, legs — mass, not sticks.
    Feet 0.2 into the ground line."""
    y_top = feet_y - h
    head_r = h * 0.17
    # head: dabbed solid
    dot_fill(s, x, y_top + head_r, head_r * 1.05, head_r * 1.05, 0.62, tag + "-head", seed=int(x * 10))
    # body: shoulders tapering to waist, then two legs — filled
    body = [
        (x - h * 0.17, y_top + head_r * 1.9), (x + h * 0.17, y_top + head_r * 1.9),
        (x + h * 0.14, y_top + h * 0.42), (x + h * 0.10, feet_y - h * 0.48 + 0.2),
        (x - h * 0.10, feet_y - h * 0.48 + 0.2), (x - h * 0.14, y_top + h * 0.42),
    ]
    cx_avg = sum(p[0] for p in body) / len(body)
    cy_avg = sum(p[1] for p in body) / len(body)
    dot_fill(s, cx_avg, cy_avg, h * 0.18, (h * 0.55) / 2, 0.62, tag + "-body", seed=int(x * 10 + 1))
    # legs: two filled strokes from the waist to the ground
    lw_line(s, x - h * 0.05, feet_y - h * 0.44, x - h * 0.09, feet_y + 0.2, "outline", tag + "-leg")
    lw_line(s, x + h * 0.05, feet_y - h * 0.44, x + h * 0.09, feet_y + 0.2, "outline", tag + "-leg")
    lw_line(s, x - h * 0.05, feet_y - h * 0.44, x - h * 0.09, feet_y + 0.2, "outline", tag + "-leg")
    # hat / hair reads INSIDE the silhouette
    if hat:
        lw_line(s, x - head_r * 1.45, y_top + head_r * 0.55, x + head_r * 1.45, y_top + head_r * 0.55,
                "outline", tag + "-hat-brim", passes=2)
        stroke_through(s, (x - head_r * 1.15, y_top + head_r * 0.4),
                       (x, y_top - head_r * 1.3), (x + head_r * 1.15, y_top + head_r * 0.4),
                       0.5, tag + "-hat-dome", passes=2)
    if spiky:
        lw_line(s, x - head_r, y_top + head_r * 0.4, x + head_r, y_top + head_r * 0.4,
                "outline", tag + "-hairline", passes=1)


def balloon_lettered(s, cx, cy, rx, ry, lines, font_h=2.8):
    """FULL whiteout coverage (the industry finishing step) so no panel stroke
    survives under the script; outline; tail; auto-fit subdabbed type."""
    max_chars = max(len(l) for l in lines)
    fit_h = min(font_h,
                (ry * 2 * 0.60) / (len(lines) * 1.5),
                (rx * 2 * 0.66) / (max_chars * 6 / 7))
    width = min(4.6, ry * 0.75)
    yy = cy - ry * 1.05
    while yy <= cy + ry * 1.05:
        s.whiteout(cx - rx * 0.88, yy, cx + rx * 0.88, yy + 0.3,
                   width_mm=width, strength=0.97, tag="whiteout")
        yy += width * 0.4
    pts = []
    for i in range(13):
        a = 2 * math.pi * i / 12
        pts.append((cx + rx * math.cos(a), cy + ry * math.sin(a)))
    pts.append((cx - rx * 0.92, cy + ry * 0.6))
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        m = (cx + 1.06 * ((a[0] + b[0]) / 2 - cx), cy + 1.06 * ((a[1] + b[1]) / 2 - cy))
        stroke_through(s, a, m, b, 0.5, "balloon", speed=70, passes=2)
    lw_line(s, cx - rx * 0.3, cy + ry * 0.95, cx - rx * 0.15, cy + ry * 1.35, "detail", "balloon")
    lh = fit_h * 1.5
    y0 = cy - (len(lines) - 1) * lh / 2 - fit_h / 2
    for i, ln in enumerate(lines):
        w = text_width_mm(ln, fit_h)
        stamp_text(s, cx - w / 2, y0 + i * lh, ln, height_mm=fit_h, subdabs=2)


def eye(s, cx, cy, flip=1.0, scale=1.0):
    w, h = 3.2 * scale, 2.6 * scale
    stroke_through(s, (cx - w, cy - h * 0.55), (cx, cy - h), (cx + w, cy - h * 0.55),
                   0.52, "eye-lid", passes=2)
    lw_line(s, cx + flip * w * 1.05, cy - h * 0.5, cx + flip * w * 1.35, cy - h * 0.1,
            "detail", "lash")
    s.stroke(cx - w * 0.45, cy - h * 0.62, cx + w * 0.45, cy - h * 0.5,
             pressure_start=0.48, pressure_end=0.42, speed_mm_s=70, tag="lid-shadow")
    dot_fill(s, cx + flip * 0.3, cy + h * 0.18, w * 0.72, h * 0.95, 0.6, "pupil",
             seed=int(cx * 7 + cy), skip=[(cx - flip * 0.55, cy - h * 0.28, 0.62 * scale)])
    lw_line(s, cx - w * 0.62, cy + h * 0.82, cx + w * 0.62, cy + h * 0.82, "bg", "eye-lower")


def pass1() -> None:
    s = get_session()
    s.note(
        "derivative_work",
        "Fan study, page 5. One Piece © Eiichiro Oda / Shueisha — "
        "interpretation from memory, disclosed, non-commercial.",
    )
    s.note(
        "material_choice",
        "The stick figures are retired. Distant crew are solid silhouettes — "
        "mass with head, shoulders, waist, legs — standing BEHIND a bulwark "
        "that is drawn over them after. Zoro's three swords are drawn as "
        "swords: blades, cross guards, hilts. Nami keeps only what survives a "
        "bust. Balloon interiors get full whiteout coverage after all panel "
        "art, so nothing crosses the script. Gulls are 'm' curves away from "
        "balloons, and the sea carries no erasure smudges.",
    )
    s.select_tool("fineliner_03")
    for (x0, y0, x1, y1) in PANELS.values():
        lw_line(s, x0, y0, x1, y0, "outline", "border", passes=2)
        lw_line(s, x1, y0, x1, y1, "outline", "border", passes=2)
        lw_line(s, x1, y1, x0, y1, "outline", "border", passes=2)
        lw_line(s, x0, y1, x0, y0, "outline", "border", passes=2)
    s.save()
    print("pass1 view:", s.view("pass1", px_per_cell=1))


def pass2() -> None:
    """P1: Merry + silhouette crew BEHIND the bulwark. No smudges."""
    s = get_session()
    s.select_tool("fineliner_03")

    tone(s, 14, 14, 162, 46, pitch=1.15, p=0.20, skip=0.78, seed=141, tag="sky")
    tone(s, 26, 24, 44, 31, pitch=0.8, p=0.28, skip=0.25, seed=142, tag="cloud")
    tone(s, 122, 27, 148, 33, pitch=0.8, p=0.28, skip=0.25, seed=143, tag="cloud")
    lw_line(s, 14, 50, 162, 50, "bg", "horizon")
    tone(s, 14, 51, 162, 60, pitch=1.05, p=0.24, skip=0.66, seed=144, tag="sea-far")
    rng = random.Random(741)
    y = 62.0
    while y <= 92.0:
        x = 15.0 + rng.uniform(0, 6)
        while x < 160.0:
            w = rng.uniform(3.0, 7.0)
            if rng.random() < 0.68:
                lw_line(s, x, y, x + w, y + rng.uniform(-0.3, 0.3), "bg", "wave", taper=0.7)
            x += w + rng.uniform(2.0, 6.0)
        y += 2.3

    # Crew: solid silhouettes first; the bulwark is drawn over them after.
    silhouette_figure(s, 74.5, 67.6, 7.0, "usopp", hat=False)
    silhouette_figure(s, 80.0, 67.6, 7.2, "zoro", spiky=True)
    silhouette_figure(s, 86.0, 67.6, 6.8, "nami")
    silhouette_figure(s, 97.5, 67.6, 7.4, "luffy", hat=True)

    # Hull, then bulwark + deck floor OVER the silhouettes' legs.
    hull = [(66, 67), (74, 73), (88, 75), (102, 73), (113, 67)]
    for i in range(len(hull) - 1):
        stroke_through(s, hull[i], ((hull[i][0] + hull[i + 1][0]) / 2,
                                    (hull[i][1] + hull[i + 1][1]) / 2 + 0.6),
                       hull[i + 1], LW["outline"], "hull", passes=2)
    lw_line(s, 66, 64.5, 113, 64.5, "struct", "bulwark-top", passes=2)
    lw_line(s, 66, 67.5, 113, 67.5, "struct", "deck-floor", passes=2)
    for px in range(72, 110, 7):
        lw_line(s, px, 64.6, px, 67.4, "detail", "bulwark-post")
    lw_line(s, 66, 66, 113, 66, "detail", "deck-edge")

    # Figurehead: neck from inside the hull into the head.
    lw_line(s, 66.5, 68.5, 60.8, 61.0, "struct", "fig-neck", passes=2)
    head = []
    for i in range(10):
        a = 2 * math.pi * i / 9
        head.append((60 + 4.6 * math.cos(a), 60 + 4.6 * math.sin(a)))
    head.append(head[0])
    for i in range(len(head) - 1):
        a, b = head[i], head[i + 1]
        m = (60 + 1.12 * ((a[0] + b[0]) / 2 - 60), 60 + 1.12 * ((a[1] + b[1]) / 2 - 60))
        stroke_through(s, a, m, b, 0.42, "figurehead", passes=1)
    stroke_through(s, (57.5, 56.5), (55.0, 54.6), (56.6, 52.6), 0.40, "horn")
    stroke_through(s, (62.5, 56.5), (65.0, 54.6), (63.4, 52.6), 0.40, "horn")
    lw_line(s, 58.2, 61.0, 58.2, 62.0, "detail", "face")
    lw_line(s, 61.8, 61.0, 61.8, 62.0, "detail", "face")
    stroke_through(s, (58.5, 63.6), (60.0, 64.6), (61.5, 63.6), 0.40, "face")

    lw_line(s, 89, 70.0, 89, 26, "struct", "mast", passes=2)
    lw_line(s, 76, 30, 102, 30, "struct", "yard")
    stroke_through(s, (78.5, 30.5), (77.0, 42.0), (80.5, 55.0), 0.40, "sail")
    stroke_through(s, (99.5, 30.5), (101.0, 42.0), (97.5, 55.0), 0.40, "sail")
    stroke_through(s, (78.5, 55.0), (88.5, 56.8), (97.5, 55.0), 0.38, "sail")
    tone(s, 80, 32, 97, 54, pitch=0.95, p=0.24, skip=0.48, seed=145, tag="sail-tone")
    lw_line(s, 89, 26, 93.5, 27.2, "detail", "flag")
    lw_line(s, 93.5, 27.2, 89, 28.4, "detail", "flag")
    lw_line(s, 89, 30, 66.5, 63.0, "bg", "rigging")
    lw_line(s, 89, 30, 112.5, 62.0, "bg", "rigging")
    lw_line(s, 104, 67.5, 104, 54, "struct", "cabin")
    lw_line(s, 104, 54, 112, 55, "struct", "cabin")
    lw_line(s, 112, 55, 113, 68.0, "struct", "cabin")

    s.save()
    print("pass2 view:", s.view("pass2", px_per_cell=1))


def pass3() -> None:
    """P2: Luffy bust + whitened, lettered balloon. P3: Zoro and Nami busts
    with drawn swords; no speed-line scratches."""
    s = get_session()
    s.select_tool("fineliner_03")

    tone(s, 13, 105, 85, 163, pitch=1.05, p=0.20, skip=0.70, seed=521, tag="p2-field")

    head = [
        (29.5, 128.0), (27.8, 137.0), (30.0, 146.5), (36.5, 153.5), (44.5, 155.5),
        (52.5, 153.5), (59.0, 146.5), (61.2, 137.5), (59.5, 128.5), (54.5, 122.0),
        (46.0, 120.2),
    ]
    head.append((32.0, 124.0))
    s.stroke_path([v for p in head for v in p], pressure=0.46, speed_mm_s=55, tag="face")

    stroke_through(s, (26.0, 124.0), (44.0, 107.5), (62.5, 123.0), 0.52, "hat", passes=2)
    stroke_through(s, (27.5, 121.0), (44.0, 115.0), (60.8, 120.0), 0.44, "band", passes=2)
    # brim ends earlier on the right — the balloon owns that corner now
    stroke_through(s, (21.5, 124.5), (43.0, 117.5), (62.0, 123.2), 0.52, "brim", passes=2)
    tone(s, 31, 110, 58, 116, pitch=0.8, p=0.30, skip=0.35, seed=522, tag="hat-tone")

    dot_fill(s, 29.8, 128.5, 2.0, 4.2, 0.58, "hair", seed=531)
    dot_fill(s, 58.6, 128.5, 2.0, 4.2, 0.58, "hair", seed=532)
    stroke_through(s, (40.6, 121.2), (42.2, 123.6), (43.8, 121.8), 0.46, "hair-notch", taper=0.85)
    stroke_through(s, (43.8, 121.8), (45.2, 124.0), (46.6, 121.6), 0.46, "hair-notch", taper=0.85)
    stroke_through(s, (27.2, 135.5), (25.6, 138.5), (27.6, 140.6), 0.36, "ear", taper=0.9)
    stroke_through(s, (61.0, 135.0), (62.6, 137.8), (60.8, 140.0), 0.36, "ear", taper=0.9)

    eye(s, 37.5, 137.5, flip=1.0, scale=1.05)
    eye(s, 51.5, 137.5, flip=-1.0, scale=1.05)
    lw_line(s, 52.2, 142.6, 54.6, 141.6, "detail", "scar", passes=2)
    lw_line(s, 53.2, 143.8, 55.4, 142.4, "detail", "scar")
    lw_line(s, 45.0, 141.5, 45.8, 143.2, "detail", "nose")

    mouth = []
    for i in range(11):
        a = 2 * math.pi * i / 10
        mouth.append((44.2 + 8.6 * math.cos(a), 149.5 + 5.2 * math.sin(a)))
    mouth.append(mouth[0])
    for i in range(len(mouth) - 1):
        a, b = mouth[i], mouth[i + 1]
        m = (44.2 + 1.1 * ((a[0] + b[0]) / 2 - 44.2), 149.5 + 1.1 * ((a[1] + b[1]) / 2 - 149.5))
        stroke_through(s, a, m, b, 0.52, "shout", passes=2)
    lw_line(s, 37.6, 147.3, 50.8, 147.3, "detail", "teeth", passes=1)
    stroke_through(s, (40.2, 152.3), (44.2, 153.5), (48.2, 152.3), 0.30, "tongue")

    lw_line(s, 39.8, 155.8, 39.2, 163.8, "struct", "neck", passes=2)
    lw_line(s, 48.8, 155.4, 49.4, 163.8, "struct", "neck", passes=2)
    stroke_through(s, (28.0, 163.8), (37.0, 156.8), (39.6, 155.6), 0.52, "shoulder", passes=2)
    stroke_through(s, (61.0, 163.8), (51.5, 156.6), (48.9, 155.4), 0.52, "shoulder", passes=2)
    lw_line(s, 35.5, 163.8, 40.2, 158.6, "struct", "vest")
    lw_line(s, 53.0, 163.8, 48.4, 158.4, "struct", "vest")

    # The balloon LAST in this panel: whiteout full coverage, then script.
    balloon_lettered(s, 65.5, 111.0, 18.0, 9.8,
                     ["I'M GONNA BE", "KING OF THE", "PIRATES!!"], font_h=2.6)

    s.save()
    print("pass3 view:", s.view("pass3", px_per_cell=1))


def pass4() -> None:
    s = get_session()
    s.select_tool("fineliner_03")

    tone(s, 95, 105, 163, 163, pitch=1.05, p=0.20, skip=0.70, seed=621, tag="p3-field")
    lw_line(s, 95, 139, 163, 139, "detail", "rail")
    tone(s, 95, 141, 163, 162, pitch=0.95, p=0.24, skip=0.56, seed=622, tag="p3-sea")
    rng = random.Random(623)
    for _ in range(18):
        x = rng.uniform(96, 160)
        y = rng.uniform(144, 160)
        lw_line(s, x, y, x + rng.uniform(2.5, 5.5), y + rng.uniform(-0.3, 0.3), "bg", "wave", taper=0.7)

    # ZORO BUST with real swords at his left hip.
    zhead = [(108.5, 127.0), (107.0, 135.0), (110.0, 142.5), (117.0, 145.5), (124.5, 142.5),
             (127.0, 135.0), (125.5, 127.4), (118.0, 124.6)]
    zhead.append((110.2, 126.4))
    s.stroke_path([v for p in zhead for v in p], pressure=0.46, speed_mm_s=55, tag="zoro-head")
    # hair: a solid cap that COVERS the skull top, white cuts for spikes
    dot_fill(s, 117.2, 126.0, 7.4, 4.2, 0.60, "zoro-hair", seed=624,
             skip=[(110.4, 125.2, 1.2), (114.2, 123.6, 1.0), (121.2, 123.4, 1.0), (124.8, 124.8, 1.2)])
    lw_line(s, 110.2, 123.2, 107.0, 119.4, "struct", "zoro-hair-spike", passes=2)
    lw_line(s, 124.6, 123.2, 127.4, 119.8, "struct", "zoro-hair-spike", passes=2)
    lw_line(s, 110.4, 133.0, 115.8, 134.2, "struct", "zoro-brow", passes=2)
    lw_line(s, 120.2, 134.0, 125.6, 133.0, "struct", "zoro-brow", passes=2)
    eye(s, 113.4, 136.0, flip=1.0, scale=0.9)
    eye(s, 121.4, 135.8, flip=-1.0, scale=0.9)
    lw_line(s, 123.4, 132.2, 123.6, 134.6, "detail", "zoro-scar")
    stroke_through(s, (113.8, 141.4), (117.2, 142.4), (120.4, 141.2), 0.36, "zoro-mouth")
    lw_line(s, 114.0, 145.8, 113.6, 150.5, "struct", "neck", passes=2)
    lw_line(s, 121.0, 145.4, 121.4, 150.2, "struct", "neck", passes=2)
    stroke_through(s, (104.0, 158.5), (112.0, 149.8), (117.0, 149.2), 0.52, "shoulder", passes=2)
    stroke_through(s, (132.0, 157.5), (123.5, 149.4), (121.6, 149.2), 0.52, "shoulder", passes=2)
    stroke_through(s, (106.0, 158.0), (117.5, 153.6), (128.5, 156.6), 0.44, "arms", passes=2)
    stroke_through(s, (107.5, 160.5), (117.5, 155.8), (126.0, 158.8), 0.40, "arms", passes=2)
    # THREE SWORDS at the left hip: blades + cross guards + hilts.
    for k, dx in enumerate((0.0, 1.5, 3.0)):
        bx = 105.5 + dx
        lw_line(s, bx, 150.5, bx - 0.8, 162.5, "outline", "sword-blade", passes=2)
        lw_line(s, bx - 1.4, 150.2, bx + 1.4, 150.9, "struct", "sword-guard")
        s.stroke(bx - 0.3, 149.0, bx + 0.7, 149.9, pressure_start=0.5, pressure_end=0.45,
                 speed_mm_s=45, tag="sword-hilt")

    # NAMI BUST, simplified to what survives.
    nhead = [(137.5, 133.5), (137.0, 129.0), (140.0, 126.0), (147.0, 125.7), (151.5, 129.0),
             (152.6, 134.0), (151.0, 139.0), (146.5, 141.3), (142.0, 140.1)]
    nhead.append((138.6, 134.9))
    s.stroke_path([v for p in nhead for v in p], pressure=0.46, speed_mm_s=55, tag="nami-head")
    # hair as a shaped MASS: crown fill + falling sides
    dot_fill(s, 144.3, 127.4, 7.2, 3.4, 0.52, "nami-hair-crown", seed=625)
    tone(s, 136.6, 128.0, 140.4, 138.0, pitch=0.6, p=0.40, skip=0.18, seed=626, tag="nami-hair-side")
    tone(s, 148.6, 128.0, 152.0, 138.0, pitch=0.6, p=0.40, skip=0.18, seed=627, tag="nami-hair-side")
    lw_line(s, 138.8, 133.6, 140.4, 134.4, "detail", "nami-eye-lid", passes=2)
    s.stroke(139.5, 135.2, 140.1, 136.1, pressure_start=0.6, pressure_end=0.55, speed_mm_s=40, tag="nami-pupil")
    lw_line(s, 144.0, 133.8, 145.6, 134.6, "detail", "nami-eye-lid", passes=2)
    s.stroke(144.7, 135.4, 145.3, 136.3, pressure_start=0.6, pressure_end=0.55, speed_mm_s=40, tag="nami-pupil")
    stroke_through(s, (140.8, 139.0), (142.4, 140.0), (144.0, 139.0), 0.30, "nami-o-mouth")
    lw_line(s, 144.9, 116.5, 144.9, 121.0, "detail", "surprise")
    lw_line(s, 148.1, 117.5, 147.5, 121.5, "detail", "surprise")
    s.stroke(146.3, 114.1, 147.0, 114.9, pressure_start=0.52, pressure_end=0.48, speed_mm_s=40, tag="surprise")
    stroke_through(s, (135.0, 158.5), (142.5, 150.5), (146.0, 149.8), 0.52, "shoulder", passes=2)
    stroke_through(s, (163.8, 157.0), (153.0, 150.0), (149.0, 149.6), 0.52, "shoulder", passes=2)
    lw_line(s, 145.0, 149.8, 144.4, 163.8, "struct", "neck", passes=2)

    balloon_lettered(s, 139.0, 111.0, 17.5, 9.0, ["EVERY SINGLE", "DAY...!!"], font_h=2.6)

    # P4: the Merry sails on; gulls are 'm' curves on the RIGHT, clear of the
    # balloon; Luffy stands ON the ram's head, drawn after it.
    tone(s, 13, 173, 163, 200, pitch=1.15, p=0.18, skip=0.76, seed=721, tag="p4-sky")
    tone(s, 118, 179, 140, 186, pitch=0.8, p=0.26, skip=0.25, seed=722, tag="p4-cloud")
    for (x, y, w) in ((102, 178, 3.2), (118, 190, 2.8)):
        stroke_through(s, (x, y), (x + w / 2, y - 1.7), (x + w, y), 0.28, "gull")
        stroke_through(s, (x, y + 0.4), (x + w / 2, y + 1.4), (x + w, y + 0.4), 0.28, "gull")
    lw_line(s, 14, 204, 162, 204, "bg", "horizon")
    tone(s, 14, 205, 162, 212, pitch=1.0, p=0.22, skip=0.66, seed=723, tag="sea-far")
    y = 214.0
    while y <= 234.0:
        x = 15.0 + rng.uniform(0, 6)
        while x < 160.0:
            w = rng.uniform(3.0, 6.5)
            if rng.random() < 0.7:
                lw_line(s, x, y, x + w, y + rng.uniform(-0.3, 0.3), "bg", "wave", taper=0.7)
            x += w + rng.uniform(2.0, 6.0)
        y += 2.2

    hull = [(70, 213), (76, 217), (88, 218.5), (100, 217), (106, 213)]
    for i in range(len(hull) - 1):
        stroke_through(s, hull[i], ((hull[i][0] + hull[i + 1][0]) / 2,
                                    (hull[i][1] + hull[i + 1][1]) / 2 + 0.4),
                       hull[i + 1], LW["outline"] * 0.9, "hull", passes=2)
    lw_line(s, 70, 212, 106, 212, "struct", "deck", passes=2)
    lw_line(s, 100, 213.5, 100, 206.5, "detail", "cabin")
    lw_line(s, 100, 206.5, 105.5, 207.2, "detail", "cabin")
    lw_line(s, 105.5, 207.2, 106, 213.5, "detail", "cabin")
    lw_line(s, 66.8, 213.5, 66.0, 208.5, "struct", "fig-neck", passes=2)
    head = []
    for i in range(9):
        a = 2 * math.pi * i / 8
        head.append((66.5 + 2.6 * math.cos(a), 207.5 + 2.6 * math.sin(a)))
    head.append(head[0])
    for i in range(len(head) - 1):
        a, b = head[i], head[i + 1]
        m = (66.5 + 1.12 * ((a[0] + b[0]) / 2 - 66.5), 207.5 + 1.12 * ((a[1] + b[1]) / 2 - 207.5))
        stroke_through(s, a, m, b, 0.40, "figurehead")
    stroke_through(s, (64.8, 204.6), (63.0, 203.2), (64.4, 201.8), 0.36, "horn")
    stroke_through(s, (68.2, 204.6), (70.0, 203.2), (68.6, 201.8), 0.36, "horn")
    lw_line(s, 88.5, 210.5, 88.5, 184, "struct", "mast", passes=2)
    lw_line(s, 80, 187, 97, 187, "detail", "yard")
    stroke_through(s, (81.5, 187.4), (80.4, 196.0), (83.0, 206.0), 0.38, "sail")
    stroke_through(s, (95.5, 187.4), (96.6, 196.0), (94.0, 206.0), 0.38, "sail")
    stroke_through(s, (83.0, 206.0), (88.5, 207.4), (94.0, 206.0), 0.36, "sail")
    tone(s, 83, 189, 94, 205, pitch=0.85, p=0.24, skip=0.45, seed=724, tag="sail-tone")
    lw_line(s, 88.5, 184, 91.5, 185.0, "detail", "flag")
    lw_line(s, 91.5, 185.0, 88.5, 186.0, "detail", "flag")
    stroke_through(s, (106, 214.5), (122, 219.0), (138, 224.5), 0.30, "wake", passes=2)
    stroke_through(s, (106, 217.5), (124, 223.0), (140, 229.0), 0.26, "wake", passes=2)
    for _ in range(16):
        x = rng.uniform(58, 70)
        y = rng.uniform(213.5, 219.5)
        s.stroke(x, y, x + 0.5, y + 0.3, pressure_start=0.3, pressure_end=0.26, speed_mm_s=80, tag="foam")

    # Luffy ON the ram's head, drawn after it — soles break its outline.
    silhouette_figure(s, 66.5, 205.2, 6.8, "luffy-p4", hat=True)
    stroke_through(s, (67.3, 202.4), (68.8, 200.0), (70.6, 198.2), 0.36, "luffy-arm")

    balloon_lettered(s, 44.0, 186.0, 16.5, 8.5, ["SET SAIL!"], font_h=2.6)

    s.save()
    print("pass4 view:", s.view("pass4", px_per_cell=1))


def final() -> None:
    s = get_session()
    print("loupe:", s.view("loupe", region_mm=[12.0, 12.0, 164.0, 236.0], px_per_cell=1))
    s.note(
        "artist_statement",
        "Page five: the sticks are gone. The crew on deck are silhouettes — "
        "solid dark masses with hats and hairlines, standing behind a "
        "bulwark drawn over them, feet on a floor that exists. Zoro carries "
        "three swords someone can actually count: blades, guards, hilts at "
        "his hip. Nami keeps only what a bust can hold. Every balloon was "
        "whitened to bare paper before its words were stamped, so nothing "
        "crosses the script. The gulls are gulls. Designs © Oda/Shueisha; "
        "the practice is ours.",
    )
    print("export:", s.export_artwork("manga_page_05"))
    kinds = {}
    for line_txt in (DIR / "log.jsonl").read_text().splitlines():
        import json

        rec = json.loads(line_txt)
        if rec["type"] == "stroke":
            kinds["strokes"] = kinds.get("strokes", 0) + 1
            if rec["tag"] == "type":
                kinds["typed"] = kinds.get("typed", 0) + 1
        elif rec["type"] == "whiteout":
            kinds["whiteouts"] = kinds.get("whiteouts", 0) + 1
        elif rec["type"] == "view":
            kinds["views"] = kinds.get("views", 0) + 1
        elif rec["type"] == "note":
            k = rec.get("note_kind", "note")
            kinds[k] = kinds.get(k, 0) + 1
    print("session log:", kinds)


if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else "1"
    {"1": pass1, "2": pass2, "3": pass3, "4": pass4, "final": final}[stage]()
