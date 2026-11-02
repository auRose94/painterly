"""Manga page 2 — the same story, rebuilt: connected, lettered, specific.

Carried from page 1's critique:
  - parts must SHARE joints: every attachment stroke overshoots into the
    piece it joins (mast roots into the hull, figurehead neck grows from the
    bow, crew drawn as single continuous polylines, heads overlapping necks)
  - the Vault-Boy collision means generic-mascot features: Luffy gets a
    longer face, big eyes with pupils and light-notches, the forehead hair
    notch, and an OPEN shouting mouth — a declaration, not a smile
  - stamp typography fills the balloons: every word real, stamped from the
    5x7 letterpress plates

Character designs © Eiichiro Oda / Shueisha — disclosed fan study, logged
as derivative_work. Non-commercial.

Usage: python scripts/manga_page_02.py {1|2|3|4|final}
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

DIR = ROOT / "sessions" / "manga_page_02"

PANELS = {
    "P1": (12.0, 12.0, 164.0, 96.0),
    "P2": (12.0, 104.0, 86.0, 164.0),
    "P3": (94.0, 104.0, 164.0, 164.0),
    "P4": (12.0, 172.0, 164.0, 236.0),
}


def get_session() -> Session:
    if (DIR / "state.json").exists():
        return Session(DIR, restore=True)
    return Session(
        DIR,
        paper_id="hot_press",
        seed=111,
        size_mm=(176.0, 250.0),
        cell_mm=0.2,
        artist_id="unnamed-artist-0",
        title="Going Merry — fan study, lettered (penciled)",
    )


def line(s, x0, y0, x1, y1, p, tag, taper=0.96, passes=1):
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


def balloon_lettered(s, cx, cy, rx, ry, lines, font_h=2.2):
    """Balloon outline, tail toward its speaker, then the script stamped in."""
    pts = []
    for i in range(13):
        a = 2 * math.pi * i / 12
        pts.append((cx + rx * math.cos(a), cy + ry * math.sin(a)))
    pts.append((cx - rx * 0.92, cy + ry * 0.6))
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        m = (cx + 1.06 * ((a[0] + b[0]) / 2 - cx), cy + 1.06 * ((a[1] + b[1]) / 2 - cy))
        stroke_through(s, a, m, b, 0.5, "balloon", speed=70, passes=2)
    line(s, cx - rx * 0.3, cy + ry * 0.95, cx - rx * 0.15, cy + ry * 1.35, 0.45, "balloon")
    lh = font_h * 1.55
    y0 = cy - (len(lines) - 1) * lh / 2 - font_h / 2
    for i, ln in enumerate(lines):
        w = text_width_mm(ln, font_h)
        stamp_text(s, cx - w / 2, y0 + i * lh, ln, height_mm=font_h)


def figure(s, x, y_top, h=6.4, tag="crew", hat=False, hair_spikes=False, nose=False):
    """A connected stick figure: one continuous stroke head-to-hip-to-feet,
    head dab overlapping the neck, arms rooted at the shoulder point."""
    head_r = h * 0.16
    stroke_through(s, (x - head_r, y_top + head_r * 0.9),
                   (x, y_top - head_r * 0.55), (x + head_r, y_top + head_r * 0.9),
                   0.44, tag + "-head", passes=2)
    s.stroke(x - head_r * 0.5, y_top + head_r * 1.5, x + head_r * 0.5, y_top + head_r * 1.5,
             pressure_start=0.42, pressure_end=0.4, speed_mm_s=50, tag=tag + "-head")
    neck_y = y_top + head_r * 1.9
    hip_y = y_top + h * 0.52
    pts = [(x, neck_y - 0.4), (x, y_top + h * 0.30), (x, hip_y)]
    fb = s.stroke_path([v for p in pts for v in p], pressure=0.4, speed_mm_s=55, tag=tag + "-body")
    s.stroke(x, hip_y, x - h * 0.16, y_top + h * 0.95, pressure_start=0.38, pressure_end=0.32,
             speed_mm_s=55, tag=tag + "-leg")
    s.stroke(x, hip_y, x + h * 0.16, y_top + h * 0.95, pressure_start=0.38, pressure_end=0.32,
             speed_mm_s=55, tag=tag + "-leg")
    sh = y_top + h * 0.30
    s.stroke(x, sh, x - h * 0.14, sh + h * 0.16, pressure_start=0.36, pressure_end=0.3,
             speed_mm_s=55, tag=tag + "-arm")
    s.stroke(x, sh, x + h * 0.14, sh + h * 0.16, pressure_start=0.36, pressure_end=0.3,
             speed_mm_s=55, tag=tag + "-arm")
    if hat:
        s.stroke(x - head_r * 1.3, y_top + head_r * 0.55, x + head_r * 1.3, y_top + head_r * 0.55,
                 pressure_start=0.5, pressure_end=0.5, speed_mm_s=45, tag=tag + "-hat")
        stroke_through(s, (x - head_r * 1.05, y_top + head_r * 0.45),
                       (x, y_top - head_r * 1.15), (x + head_r * 1.05, y_top + head_r * 0.45),
                       0.46, tag + "-hat", passes=2)
    if hair_spikes:
        for k, (dx, dy) in enumerate(((-0.5, -1.0), (0.0, -1.3), (0.5, -1.0))):
            s.stroke(x + dx * head_r * 0.7, y_top - 0.1, x + dx * head_r * 1.3, y_top - 0.1 + dy,
                     pressure_start=0.44, pressure_end=0.36, speed_mm_s=50, tag=tag + "-hair")
    if nose:
        s.stroke(x - head_r * 0.9, y_top + head_r * 1.05, x - head_r * 2.2, y_top + head_r * 0.95,
                 pressure_start=0.46, pressure_end=0.4, speed_mm_s=45, tag=tag + "-nose")


def pass1() -> None:
    s = get_session()
    s.note(
        "derivative_work",
        "Fan study, page 2. One Piece and its character designs © Eiichiro "
        "Oda / Shueisha. Interpretation from memory through the environment's "
        "physics; non-commercial; disclosed by default.",
    )
    s.note(
        "material_choice",
        "Rebuilt from page 1's critique: everything SHARES joints now — "
        "attachment strokes overshoot into the piece they join, the crew are "
        "single continuous polylines, heads overlap necks. The captain's "
        "face is longer, the eyes large with pupils and light-notches, the "
        "forehead carries the hair notch, and the mouth is OPEN — he is "
        "declaring, not smiling for a mascot. The balloons are stamped with "
        "the 5x7 letterpress plates. Lettering exists now.",
    )
    s.select_tool("fineliner_03")
    for (x0, y0, x1, y1) in PANELS.values():
        line(s, x0, y0, x1, y0, 0.55, "border", passes=2)
        line(s, x1, y0, x1, y1, 0.55, "border", passes=2)
        line(s, x1, y1, x0, y1, 0.55, "border", passes=2)
        line(s, x0, y1, x0, y0, 0.55, "border", passes=2)
    s.save()
    print("pass1 view:", s.view("pass1", px_per_cell=1))


def pass2() -> None:
    """P1: the Merry, fully connected, crew as continuous figures."""
    s = get_session()
    s.select_tool("fineliner_03")

    tone(s, 14, 14, 162, 46, pitch=1.1, p=0.22, skip=0.72, seed=111, tag="sky")
    tone(s, 26, 24, 44, 31, pitch=0.8, p=0.30, skip=0.25, seed=112, tag="cloud")
    tone(s, 122, 27, 148, 33, pitch=0.8, p=0.30, skip=0.25, seed=113, tag="cloud")
    line(s, 14, 50, 162, 50, 0.40, "horizon")
    tone(s, 14, 51, 162, 60, pitch=1.0, p=0.26, skip=0.60, seed=114, tag="sea-far")
    rng = random.Random(212)
    y = 62.0
    while y <= 92.0:
        x = 15.0 + rng.uniform(0, 6)
        while x < 160.0:
            w = rng.uniform(3.0, 7.0)
            if rng.random() < 0.72:
                line(s, x, y, x + w, y + rng.uniform(-0.3, 0.3), 0.22 + 0.2 * (y - 60) / 34.0, "wave", taper=0.7)
            x += w + rng.uniform(2.0, 6.0)
        y += 2.3

    # Hull.
    hull = [(66, 67), (74, 73), (88, 75), (102, 73), (113, 67)]
    for i in range(len(hull) - 1):
        stroke_through(s, hull[i], ((hull[i][0] + hull[i + 1][0]) / 2,
                                    (hull[i][1] + hull[i + 1][1]) / 2 + 0.6),
                       hull[i + 1], 0.45, "hull", passes=2)
    line(s, 66, 66, 113, 66, 0.42, "deck", passes=2)

    # Figurehead: the neck stroke GROWS from inside the hull into the head —
    # shared ink at both ends, no floaters.
    line(s, 66.5, 68.5, 60.8, 61.0, 0.40, "fig-neck", passes=2)
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
    line(s, 58.2, 61.0, 58.2, 62.0, 0.5, "face")
    line(s, 61.8, 61.0, 61.8, 62.0, 0.5, "face")
    stroke_through(s, (58.5, 63.6), (60.0, 64.6), (61.5, 63.6), 0.40, "face")

    # Mast ROOTED in the keel: starts 2mm below the deck, crosses it.
    line(s, 89, 68.0, 89, 26, 0.45, "mast", passes=2)
    line(s, 76, 30, 102, 30, 0.38, "yard")
    stroke_through(s, (78.5, 30.5), (77.0, 42.0), (80.5, 55.0), 0.40, "sail")
    stroke_through(s, (99.5, 30.5), (101.0, 42.0), (97.5, 55.0), 0.40, "sail")
    stroke_through(s, (78.5, 55.0), (88.5, 56.8), (97.5, 55.0), 0.38, "sail")
    tone(s, 80, 32, 97, 54, pitch=0.9, p=0.26, skip=0.42, seed=115, tag="sail-tone")
    line(s, 89, 26, 93.5, 27.2, 0.42, "flag")
    line(s, 93.5, 27.2, 89, 28.4, 0.42, "flag")
    line(s, 89, 30, 66.5, 63.0, 0.24, "rigging")
    line(s, 89, 30, 112.5, 62.0, 0.24, "rigging")
    line(s, 104, 67.5, 104, 54, 0.38, "cabin")
    line(s, 104, 54, 112, 55, 0.38, "cabin")
    line(s, 112, 55, 113, 68.0, 0.38, "cabin")

    # Crew: continuous figures, feet ON the deck line, heads overlapping necks.
    figure(s, 74.5, 54.2, h=6.6, tag="usopp", nose=True)
    figure(s, 80.0, 54.0, h=6.8, tag="zoro", hair_spikes=True)
    figure(s, 86.0, 54.4, h=6.4, tag="nami")
    figure(s, 97.5, 53.6, h=7.0, tag="luffy", hat=True)

    s.save()
    print("pass2 view:", s.view("pass2", px_per_cell=1))


def pass3() -> None:
    """P2: Luffy declares — longer face, big eyes, open mouth, stamped call."""
    s = get_session()
    s.select_tool("fineliner_03")

    tone(s, 13, 105, 85, 163, pitch=1.0, p=0.22, skip=0.62, seed=311, tag="p2-field")

    # Head: an egg, taller than wide.
    head = [
        (29.5, 128.0), (27.8, 137.0), (30.0, 146.5), (36.5, 153.5), (44.5, 155.5),
        (52.5, 153.5), (59.0, 146.5), (61.2, 137.5), (59.5, 128.5), (54.5, 122.0),
        (46.0, 120.2),
    ]
    head.append((32.0, 124.0))
    s.stroke_path([v for p in head for v in p], pressure=0.42, speed_mm_s=55, tag="face")

    # Straw hat seated LOW: dome, band, wide brim.
    stroke_through(s, (26.0, 124.0), (44.0, 107.5), (62.5, 123.0), 0.46, "hat", passes=2)
    stroke_through(s, (27.5, 121.0), (44.0, 115.0), (60.8, 120.0), 0.40, "band", passes=2)
    stroke_through(s, (21.5, 124.5), (44.0, 117.5), (66.5, 124.0), 0.46, "brim", passes=2)
    tone(s, 31, 110, 58, 116, pitch=0.8, p=0.30, skip=0.35, seed=312, tag="hat-tone")

    # The forehead hair notch — Luffy's zigzag under the band.
    stroke_through(s, (40.6, 121.2), (42.2, 123.6), (43.8, 121.8), 0.46, "hair-notch", taper=0.85)
    stroke_through(s, (43.8, 121.8), (45.2, 124.0), (46.6, 121.6), 0.46, "hair-notch", taper=0.85)
    # side tufts
    stroke_through(s, (28.2, 125.5), (29.8, 130.5), (28.6, 134.0), 0.44, "hair", taper=0.8)
    stroke_through(s, (60.0, 124.8), (58.6, 130.0), (59.8, 133.5), 0.44, "hair", taper=0.8)
    # ears
    stroke_through(s, (27.2, 135.5), (25.6, 138.5), (27.6, 140.6), 0.36, "ear", taper=0.9)
    stroke_through(s, (61.0, 135.0), (62.6, 137.8), (60.8, 140.0), 0.36, "ear", taper=0.9)

    # Eyes: LARGE — lid arcs plus big pupils with a light notch between dabs.
    stroke_through(s, (33.8, 135.6), (37.4, 134.2), (40.8, 135.6), 0.46, "eye", passes=2)
    s.stroke(36.2, 136.6, 37.0, 138.2, pressure_start=0.6, pressure_end=0.55, speed_mm_s=40, tag="eye")
    s.stroke(37.5, 136.4, 38.3, 138.0, pressure_start=0.6, pressure_end=0.55, speed_mm_s=40, tag="eye")
    stroke_through(s, (47.4, 135.4), (50.8, 134.0), (54.2, 135.4), 0.46, "eye", passes=2)
    s.stroke(49.8, 136.4, 50.6, 138.0, pressure_start=0.6, pressure_end=0.55, speed_mm_s=40, tag="eye")
    s.stroke(51.1, 136.2, 51.9, 137.8, pressure_start=0.6, pressure_end=0.55, speed_mm_s=40, tag="eye")
    # the scar, two ticks, clearly on the cheek under HIS left eye
    line(s, 52.2, 140.6, 54.6, 139.6, 0.40, "scar", passes=2)
    line(s, 53.2, 141.8, 55.4, 140.4, 0.34, "scar")
    # nose
    line(s, 45.0, 139.8, 45.8, 141.4, 0.36, "nose")

    # OPEN SHOUTING MOUTH — the declaration, not a mascot smile.
    mouth = []
    for i in range(11):
        a = 2 * math.pi * i / 10
        mouth.append((44.2 + 8.6 * math.cos(a), 148.0 + 5.2 * math.sin(a)))
    mouth.append(mouth[0])
    for i in range(len(mouth) - 1):
        a, b = mouth[i], mouth[i + 1]
        m = (44.2 + 1.1 * ((a[0] + b[0]) / 2 - 44.2), 148.0 + 1.1 * ((a[1] + b[1]) / 2 - 148.0))
        stroke_through(s, a, m, b, 0.46, "shout", passes=2)
    line(s, 37.6, 145.8, 50.8, 145.8, 0.34, "teeth", passes=1)
    stroke_through(s, (40.2, 150.8), (44.2, 152.0), (48.2, 150.8), 0.30, "tongue")

    # Speed lines + the stamped call.
    rng = random.Random(313)
    for _ in range(8):
        x0 = rng.uniform(14.0, 84.0)
        y0 = 163.0 if rng.random() < 0.5 else 105.0
        line(s, x0, y0, x0 + (44.0 - x0) * rng.uniform(0.4, 0.58),
             y0 + (132.0 - y0) * rng.uniform(0.4, 0.58), 0.20, "speed", taper=0.5)
    balloon_lettered(s, 64.5, 111.5, 18.5, 10.0,
                     ["I'M GONNA BE", "KING OF THE", "PIRATES!!"], font_h=2.2)

    s.save()
    print("pass3 view:", s.view("pass3", px_per_cell=1))


def pass4() -> None:
    """P3 + P4: the crew reacts (lettered), then the Merry sails on."""
    s = get_session()
    s.select_tool("fineliner_03")

    tone(s, 95, 105, 163, 163, pitch=1.0, p=0.22, skip=0.64, seed=411, tag="p3-field")
    line(s, 95, 138, 163, 138, 0.36, "rail")
    tone(s, 95, 140, 163, 162, pitch=0.95, p=0.26, skip=0.52, seed=412, tag="p3-sea")
    rng = random.Random(414)
    for _ in range(22):
        x = rng.uniform(96, 160)
        y = rng.uniform(142, 160)
        line(s, x, y, x + rng.uniform(2.5, 5.5), y + rng.uniform(-0.3, 0.3), 0.22, "wave", taper=0.7)

    # Zoro: connected bust, three swords seated at the hip.
    zhead = [(109.5, 128.0), (108.0, 135.0), (110.5, 141.5), (117.0, 144.0), (124.0, 141.5),
             (126.5, 135.0), (125.0, 128.2), (118.0, 125.5)]
    zhead.append((110.5, 127.2))
    s.stroke_path([v for p in zhead for v in p], pressure=0.42, speed_mm_s=55, tag="zoro-head")
    for (x0, y0, x1, y1) in (
        (110.0, 127.4, 107.4, 124.0), (114.0, 126.2, 113.0, 122.6),
        (118.5, 126.0, 119.4, 122.2), (122.6, 126.6, 125.4, 123.6),
    ):
        line(s, x0, y0, x1, y1, 0.42, "zoro-hair")
    stroke_through(s, (111.2, 134.0), (113.4, 133.2), (115.4, 134.0), 0.44, "zoro-eye", passes=2)
    stroke_through(s, (120.6, 133.8), (122.8, 133.0), (124.8, 133.8), 0.44, "zoro-eye", passes=2)
    line(s, 123.2, 131.0, 123.4, 133.4, 0.36, "zoro-scar")
    stroke_through(s, (113.8, 139.6), (117.2, 140.6), (120.4, 139.4), 0.36, "zoro-mouth")
    stroke_through(s, (108.0, 150.0), (117.5, 146.0), (126.5, 149.6), 0.40, "zoro-arms", passes=2)
    for k in range(3):
        line(s, 107.0 + k * 1.4, 152.0 - k * 0.6, 102.5 + k * 1.2, 160.0 - k * 0.8, 0.40, "swords", passes=2)
        s.stroke(106.6 + k * 1.4, 151.4 - k * 0.6, 107.8 + k * 1.4, 150.8 - k * 0.6,
                 pressure_start=0.5, pressure_end=0.45, speed_mm_s=45, tag="swords")

    # Nami: tone hair, surprise ring and marks.
    nhead = [(136.5, 133.0), (136.0, 128.5), (140.0, 125.5), (146.0, 125.2), (150.5, 128.4),
             (151.6, 133.5), (150.0, 138.5), (145.5, 140.8), (141.0, 139.6)]
    nhead.append((137.6, 134.4))
    s.stroke_path([v for p in nhead for v in p], pressure=0.42, speed_mm_s=55, tag="nami-head")
    tone(s, 136.0, 124.8, 152.4, 133.0, pitch=0.55, p=0.44, skip=0.10, seed=415, tag="nami-hair")
    line(s, 137.2, 132.6, 138.8, 133.4, 0.34, "nami-face", passes=2)
    line(s, 142.6, 132.8, 144.2, 133.6, 0.34, "nami-face", passes=2)
    stroke_through(s, (139.6, 137.4), (141.4, 138.6), (143.2, 137.4), 0.36, "nami-face")
    stroke_through(s, (139.4, 137.2), (141.4, 135.6), (143.4, 137.2), 0.36, "nami-face")
    for (x0, y0, x1, y1) in ((143.0, 117.0, 143.0, 121.5), (146.2, 118.0, 145.6, 122.0)):
        line(s, x0, y0, x1, y1, 0.40, "surprise")
    s.stroke(144.4, 114.6, 145.1, 115.4, pressure_start=0.52, pressure_end=0.48, speed_mm_s=40, tag="surprise")
    for _ in range(7):
        y0 = rng.uniform(108.0, 160.0)
        line(s, 95.5, y0, 95.5 + rng.uniform(14, 26), y0 + rng.uniform(-2.5, 2.5), 0.18, "speed", taper=0.45)

    balloon_lettered(s, 139.0, 111.0, 17.5, 9.0, ["EVERY SINGLE", "DAY...!!"], font_h=2.2)

    # P4: sailing away.
    tone(s, 13, 173, 163, 200, pitch=1.1, p=0.20, skip=0.72, seed=421, tag="p4-sky")
    tone(s, 40, 182, 52, 189, pitch=0.8, p=0.28, skip=0.25, seed=422, tag="p4-cloud")
    tone(s, 116, 178, 138, 184, pitch=0.8, p=0.28, skip=0.25, seed=423, tag="p4-cloud")
    for (x, y, w) in ((36, 190, 3.2), (44, 185.5, 2.6), (124, 188, 3.0)):
        stroke_through(s, (x, y), (x + w / 2, y - 1.6), (x + w, y), 0.30, "gull")
        stroke_through(s, (x, y + 0.5), (x + w / 2, y + 1.2), (x + w, y + 0.5), 0.30, "gull")
    line(s, 14, 204, 162, 204, 0.40, "horizon")
    tone(s, 14, 205, 162, 212, pitch=1.0, p=0.24, skip=0.62, seed=424, tag="sea-far")
    y = 214.0
    while y <= 234.0:
        x = 15.0 + rng.uniform(0, 6)
        while x < 160.0:
            w = rng.uniform(3.0, 6.5)
            if rng.random() < 0.7:
                line(s, x, y, x + w, y + rng.uniform(-0.3, 0.3), 0.22 + 0.18 * (y - 210) / 26.0, "wave", taper=0.7)
            x += w + rng.uniform(2.0, 6.0)
        y += 2.2

    hull = [(70, 213), (76, 217), (88, 218.5), (100, 217), (106, 213)]
    for i in range(len(hull) - 1):
        stroke_through(s, hull[i], ((hull[i][0] + hull[i + 1][0]) / 2,
                                    (hull[i][1] + hull[i + 1][1]) / 2 + 0.4),
                       hull[i + 1], 0.42, "hull", passes=2)
    line(s, 70, 212, 106, 212, 0.40, "deck", passes=2)
    line(s, 66.8, 213.5, 66.0, 208.5, 0.38, "fig-neck", passes=2)
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
    line(s, 88.5, 210.5, 88.5, 184, 0.42, "mast", passes=2)
    line(s, 80, 187, 97, 187, 0.34, "yard")
    stroke_through(s, (81.5, 187.4), (80.4, 196.0), (83.0, 206.0), 0.38, "sail")
    stroke_through(s, (95.5, 187.4), (96.6, 196.0), (94.0, 206.0), 0.38, "sail")
    stroke_through(s, (83.0, 206.0), (88.5, 207.4), (94.0, 206.0), 0.36, "sail")
    tone(s, 83, 189, 94, 205, pitch=0.85, p=0.24, skip=0.45, seed=425, tag="sail-tone")
    line(s, 88.5, 184, 91.5, 185.0, 0.40, "flag")
    line(s, 91.5, 185.0, 88.5, 186.0, 0.40, "flag")
    stroke_through(s, (106, 214.5), (122, 219.0), (138, 224.5), 0.30, "wake", passes=2)
    stroke_through(s, (106, 217.5), (124, 223.0), (140, 229.0), 0.26, "wake", passes=2)
    for _ in range(16):
        x = rng.uniform(58, 70)
        y = rng.uniform(213.5, 219.5)
        s.stroke(x, y, x + 0.5, y + 0.3, pressure_start=0.3, pressure_end=0.26, speed_mm_s=80, tag="foam")

    # Luffy on the figurehead, arm thrown high — connected this time.
    figure(s, 66.5, 201.0, h=7.4, tag="luffy-p4", hat=True)
    stroke_through(s, (67.3, 203.0), (69.0, 200.0), (71.0, 197.6), 0.36, "luffy-arm")

    balloon_lettered(s, 44.0, 186.0, 16.5, 8.5, ["SET SAIL!"], font_h=2.4)

    s.save()
    print("pass4 view:", s.view("pass4", px_per_cell=1))


def final() -> None:
    s = get_session()
    print("loupe:", s.view("loupe", region_mm=[12.0, 12.0, 164.0, 236.0], px_per_cell=1))
    s.note(
        "artist_statement",
        "Page two of the Going Merry fan study — the same beat, rebuilt. "
        "Everything that floated is now rooted: the mast grows out of the "
        "keel, the figurehead's neck is drawn from inside the hull, and the "
        "crew are single unbroken strokes from crown to feet. The captain's "
        "face is longer, his eyes carry pupils with a light notch, his "
        "forehead wears the zigzag, and his mouth is open because he is "
        "declaring, not posing. The balloons speak in stamped letterpress — "
        "the lettering medium exists now. Designs © Oda/Shueisha; the "
        "practice belongs to this hand.",
    )
    print("export:", s.export_artwork("manga_page_02"))
    kinds = {}
    for line_txt in (DIR / "log.jsonl").read_text().splitlines():
        import json

        rec = json.loads(line_txt)
        if rec["type"] == "stroke":
            kinds["strokes"] = kinds.get("strokes", 0) + 1
            if rec["tag"] == "type":
                kinds["typed"] = kinds.get("typed", 0) + 1
        elif rec["type"] == "view":
            kinds["views"] = kinds.get("views", 0) + 1
        elif rec["type"] == "note":
            k = rec.get("note_kind", "note")
            kinds[k] = kinds.get(k, 0) + 1
    print("session log:", kinds)


if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else "1"
    {"1": pass1, "2": pass2, "3": pass3, "4": pass4, "final": final}[stage]()
