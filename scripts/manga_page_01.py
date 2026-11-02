"""Manga page — One Piece fan study, penciled stage.

Luffy and crew on the Going Merry. Character designs © Eiichiro Oda /
Shueisha; this sheet is a disclosed non-commercial fan study drawn stroke by
stroke through the environment's physics — an interpretation from memory, not
a reproduction. The disclosure lives in the log as a derivative_work note.

Format: B4-proportioned page (176 x 250 mm), four panels, ruling-pen borders,
screentone as regular halftone dot grids (v0 of the tone medium), balloons
placed for a script the hand cannot letter yet — penciled stage, honestly.

Usage: python scripts/manga_page_01.py {1|2|3|4|5|final}
"""

import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from painterly.session import Session  # noqa: E402
from painterly.stroke import curvature_through  # noqa: E402

DIR = ROOT / "sessions" / "manga_page_01b"

PANELS = {
    "P1": (12.0, 12.0, 164.0, 96.0),
    "P2": (12.0, 104.0, 86.0, 164.0),
    "P3": (94.0, 104.0, 164.0, 164.0),
    "P4": (12.0, 172.0, 164.0, 236.0),
}

COUNTS = {}


def get_session() -> Session:
    if (DIR / "state.json").exists():
        return Session(DIR, restore=True)
    return Session(
        DIR,
        paper_id="hot_press",
        seed=101,
        size_mm=(176.0, 250.0),
        cell_mm=0.2,
        artist_id="unnamed-artist-0",
        title="Going Merry — One Piece fan study (penciled)",
    )


def line(s, x0, y0, x1, y1, p, tag, taper=0.96, passes=1):
    for k in range(passes):
        fb = s.stroke(x0, y0, x1, y1, pressure_start=p, pressure_end=p * taper,
                      speed_mm_s=70, tag=tag)
        COUNTS[tag] = COUNTS.get(tag, 0) + 1
    return fb


def stroke_through(s, a, mid, b, p, tag, speed=60.0, taper=0.88, passes=1):
    k = curvature_through(a, mid, b)
    for _ in range(passes):
        s.stroke(*a, *b, curvature=k, pressure_start=p, pressure_end=p * taper,
                 speed_mm_s=speed, tag=tag)
        COUNTS[tag] = COUNTS.get(tag, 0) + 1


def tone(s, x0, y0, x1, y1, pitch=1.0, p=0.30, skip=0.55, seed=0, tag="tone"):
    """Screentone v0: a regular halftone dot grid, density via skip."""
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
                COUNTS[tag] = COUNTS.get(tag, 0) + 1
            x += pitch
        y += pitch
        row += 1


def balloon(s, cx, cy, rx, ry, tag="balloon"):
    """An empty balloon, two passes, tail ticks toward its speaker."""
    pts = []
    for i in range(13):
        a = 2 * math.pi * i / 12
        pts.append((cx + rx * math.cos(a), cy + ry * math.sin(a)))
    pts.append((cx - rx * 0.92, cy + ry * 0.6))
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        m = (cx + 1.06 * ((a[0] + b[0]) / 2 - cx), cy + 1.06 * ((a[1] + b[1]) / 2 - cy))
        stroke_through(s, a, m, b, 0.5, tag, speed=70, passes=2)
    line(s, cx - rx * 0.3, cy + ry * 0.95, cx - rx * 0.15, cy + ry * 1.35, 0.45, tag, passes=1)


def pass1() -> None:
    """Panel borders, ruling-pen straight, two passes each."""
    s = get_session()
    s.note(
        "attempt_boundary",
        "manga_page_01 rejected: giant arcs streaked the whole page — an "
        "algebra slip in the balloon and figurehead loops wrote the arc "
        "midpoint as C + k*X instead of C + k*(X - C), flinging every "
        "ellipse segment forty millimeters wide of its target. Fixed; "
        "restarting clean on manga_page_01b.",
    )
    s.note(
        "derivative_work",
        "Fan study. Character designs, Going Merry, and One Piece © Eiichiro "
        "Oda / Shueisha. Drawn stroke by stroke from memory of the designs — "
        "an interpretation through the environment's physics, not a trace or "
        "a reproduction. Non-commercial; disclosure is the default, not an "
        "afterthought.",
    )
    s.note(
        "material_choice",
        "B4 manuscript proportions, penciled stage. Borders in double-ruled "
        "ink. Screentone v0: regular halftone grids, density via skip. "
        "Balloons are placed but empty — the hand cannot letter yet; the "
        "script comes when a lettering medium exists. Panels read left to "
        "right for this study.",
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
    """P1: the Going Merry at sea, crew on deck, sky and waves."""
    s = get_session()
    s.select_tool("fineliner_03")

    # Sky tone, sparse; two clouds.
    tone(s, 14, 14, 162, 46, pitch=1.1, p=0.22, skip=0.72, seed=101, tag="sky")
    tone(s, 26, 24, 44, 31, pitch=0.8, p=0.30, skip=0.25, seed=102, tag="cloud")
    tone(s, 122, 27, 148, 33, pitch=0.8, p=0.30, skip=0.25, seed=103, tag="cloud")

    # Sea: horizon, wave dashes, tone near the horizon.
    line(s, 14, 50, 162, 50, 0.40, "horizon")
    tone(s, 14, 51, 162, 60, pitch=1.0, p=0.26, skip=0.60, seed=104, tag="sea-far")
    rng = random.Random(202)
    y = 62.0
    while y <= 92.0:
        x = 15.0 + rng.uniform(0, 6)
        while x < 160.0:
            w = rng.uniform(3.0, 7.0)
            if rng.random() < 0.72:
                line(s, x, y, x + w, y + rng.uniform(-0.3, 0.3), 0.22 + 0.2 * (y - 60) / 34.0, "wave", taper=0.7)
            x += w + rng.uniform(2.0, 6.0)
        y += 2.3

    # The Going Merry, center. Hull first.
    hull = [(66, 67), (74, 73), (88, 75), (102, 73), (113, 67)]
    for i in range(len(hull) - 1):
        stroke_through(s, hull[i], ((hull[i][0] + hull[i + 1][0]) / 2, (hull[i][1] + hull[i + 1][1]) / 2 + 0.6),
                       hull[i + 1], 0.45, "hull", passes=2)
    line(s, 66, 66, 113, 66, 0.42, "deck", passes=2)

    # Sheep figurehead at the bow: head circle, curled horns, wool curls, face.
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
    for (wx, wy) in ((56.5, 58.5), (60.0, 56.6), (63.5, 58.5), (58.0, 60.0), (62.0, 60.2)):
        stroke_through(s, (wx - 0.8, wy), (wx, wy + 0.7), (wx + 0.8, wy), 0.30, "wool", taper=0.7)

    # Mast, yard, sail (bulging quad), flag, rigging, stern cabin.
    line(s, 89, 64, 89, 26, 0.45, "mast", passes=2)
    line(s, 76, 30, 102, 30, 0.38, "yard")
    stroke_through(s, (78.5, 30.5), (77.0, 42.0), (80.5, 55.0), 0.40, "sail")
    stroke_through(s, (99.5, 30.5), (101.0, 42.0), (97.5, 55.0), 0.40, "sail")
    stroke_through(s, (78.5, 55.0), (88.5, 56.8), (97.5, 55.0), 0.38, "sail")
    tone(s, 80, 32, 97, 54, pitch=0.9, p=0.26, skip=0.42, seed=105, tag="sail-tone")
    line(s, 89, 26, 93.5, 27.2, 0.42, "flag")
    line(s, 93.5, 27.2, 89, 28.4, 0.42, "flag")
    line(s, 89, 30, 66.5, 63.0, 0.24, "rigging")
    line(s, 89, 30, 112.5, 62.0, 0.24, "rigging")
    line(s, 104, 66, 104, 54, 0.38, "cabin")
    line(s, 104, 54, 112, 55, 0.38, "cabin")
    line(s, 112, 55, 113, 66, 0.38, "cabin")

    # Crew silhouettes, seated in the scene, each a few honest strokes.
    # Luffy at the bow rail, straw hat clear.
    s.stroke(97.4, 60.2, 97.0, 55.8, pressure_start=0.4, pressure_end=0.35, speed_mm_s=50, tag="luffy-p1")
    s.stroke(95.6, 60.2, 95.9, 56.0, pressure_start=0.4, pressure_end=0.35, speed_mm_s=50, tag="luffy-p1")
    s.stroke(94.8, 55.9, 98.2, 55.9, pressure_start=0.48, pressure_end=0.48, speed_mm_s=45, tag="hat-p1")
    stroke_through(s, (95.4, 55.6), (96.5, 53.8), (97.6, 55.5), 0.44, "hat-p1", passes=2)
    # Zoro amidships: spiky hair, sword slung.
    s.stroke(79.2, 60.4, 79.4, 56.2, pressure_start=0.4, pressure_end=0.35, speed_mm_s=50, tag="zoro-p1")
    s.stroke(80.6, 60.4, 80.5, 56.4, pressure_start=0.4, pressure_end=0.35, speed_mm_s=50, tag="zoro-p1")
    for k, (dx, dy) in enumerate(((-0.8, -1.1), (0.0, -1.3), (0.8, -1.1))):
        s.stroke(79.9 + dx, 56.4, 79.9 + dx * 1.6, 56.4 + dy, pressure_start=0.42, pressure_end=0.34,
                 speed_mm_s=50, tag="zoro-hair")
    line(s, 78.6, 60.6, 74.8, 64.6, 0.34, "sword")
    # Nami beside him: long hair mass, tone-filled.
    s.stroke(85.2, 60.4, 85.0, 55.8, pressure_start=0.4, pressure_end=0.35, speed_mm_s=50, tag="nami-p1")
    s.stroke(86.6, 60.4, 86.8, 56.0, pressure_start=0.4, pressure_end=0.35, speed_mm_s=50, tag="nami-p1")
    tone(s, 84.6, 55.2, 87.4, 58.6, pitch=0.6, p=0.42, skip=0.15, seed=106, tag="nami-hair")
    # Usopp forward: the nose announces him.
    s.stroke(72.8, 60.6, 72.6, 56.6, pressure_start=0.4, pressure_end=0.35, speed_mm_s=50, tag="usopp-p1")
    s.stroke(72.6, 57.6, 70.6, 57.2, pressure_start=0.44, pressure_end=0.4, speed_mm_s=45, tag="usopp-nose")

    s.save()
    print("pass2 view:", s.view("pass2", px_per_cell=1))


def pass3() -> None:
    """P2: Luffy close-up — straw hat, grin, scar, speed lines, balloon."""
    s = get_session()
    s.select_tool("fineliner_03")

    # Gray field behind the bust.
    tone(s, 13, 105, 85, 163, pitch=1.0, p=0.22, skip=0.62, seed=301, tag="p2-field")

    # Head: round with a firm jaw, one motion.
    head = [
        (34.5, 126.0), (29.5, 132.0), (28.2, 139.0), (31.0, 146.5), (37.5, 152.0),
        (45.0, 154.0), (53.0, 152.0), (59.5, 146.0), (62.2, 138.5), (61.0, 130.0),
        (57.0, 123.0),
    ]
    head.append((36.0, 124.5))
    fb = s.stroke_path([v for p in head for v in p], pressure=0.42, speed_mm_s=55, tag="face")
    COUNTS["face"] = 1

    # Straw hat: dome + wide brim + dark band (double pass).
    stroke_through(s, (25.5, 122.5), (44.0, 105.5), (62.5, 121.0), 0.46, "hat", passes=2)
    stroke_through(s, (22.0, 124.0), (43.5, 116.5), (66.0, 122.5), 0.46, "brim", passes=2)
    stroke_through(s, (27.0, 120.0), (44.0, 113.0), (61.5, 119.0), 0.40, "band", passes=2)
    tone(s, 30, 108, 59, 115, pitch=0.8, p=0.30, skip=0.35, seed=302, tag="hat-tone")

    # Hair tufts under the brim; ears.
    for (x0, y0, x1, y1, xm, ym) in (
        (27.5, 124.5, 30.0, 130.5, 27.0, 127.5),
        (60.5, 124.0, 58.5, 130.0, 61.5, 127.0),
        (33.0, 124.0, 35.5, 128.0, 33.2, 126.2),
    ):
        stroke_through(s, (x0, y0), (xm, ym), (x1, y1), 0.44, "hair", taper=0.7)
    stroke_through(s, (26.8, 133.0), (25.2, 136.0), (27.2, 138.2), 0.36, "ear", taper=0.9)
    stroke_through(s, (61.8, 132.6), (63.2, 135.4), (61.4, 137.6), 0.36, "ear", taper=0.9)

    # Eyes: bold arcs with dot pupils; Luffy's scar under HIS left (our right).
    stroke_through(s, (36.0, 130.5), (38.6, 129.6), (41.0, 130.6), 0.46, "eye", passes=2)
    s.stroke(38.6, 131.6, 38.9, 133.0, pressure_start=0.55, pressure_end=0.5, speed_mm_s=40, tag="eye")
    stroke_through(s, (49.5, 130.5), (52.0, 129.6), (54.5, 130.4), 0.46, "eye", passes=2)
    s.stroke(51.8, 131.5, 52.1, 132.9, pressure_start=0.55, pressure_end=0.5, speed_mm_s=40, tag="eye")
    line(s, 52.6, 135.6, 55.0, 134.6, 0.40, "scar", passes=2)
    line(s, 53.6, 136.6, 55.6, 135.2, 0.34, "scar")
    # Nose tick, then the grin — wide, corners up, teeth line inside.
    line(s, 45.4, 135.4, 46.2, 137.2, 0.36, "nose")
    stroke_through(s, (34.5, 140.5), (44.5, 145.0), (55.5, 140.0), 0.48, "grin", passes=2)
    stroke_through(s, (37.0, 141.6), (44.6, 143.6), (52.8, 141.2), 0.38, "grin", passes=1)
    stroke_through(s, (33.2, 139.2), (34.4, 141.2), (36.0, 142.2), 0.34, "grin-corner")
    stroke_through(s, (56.8, 138.6), (56.2, 140.4), (54.6, 141.4), 0.34, "grin-corner")

    # Speed lines radiating from the panel corners toward the face.
    rng = random.Random(303)
    for _ in range(9):
        x0 = rng.uniform(14.0, 84.0)
        y0 = 163.0 if rng.random() < 0.5 else 105.0
        x1 = x0 + (44.0 - x0) * rng.uniform(0.42, 0.6)
        y1 = y0 + (132.0 - y0) * rng.uniform(0.42, 0.6)
        line(s, x0, y0, x1, y1, 0.20, "speed", taper=0.5)

    # Balloon, placed for the script.
    balloon(s, 66.0, 111.0, 15.5, 8.5)

    s.save()
    print("pass3 view:", s.view("pass3", px_per_cell=1))


def pass4() -> None:
    """P3: Zoro and Nami react; sea behind; surprise marks, balloon."""
    s = get_session()
    s.select_tool("fineliner_03")

    tone(s, 95, 105, 163, 163, pitch=1.0, p=0.22, skip=0.64, seed=401, tag="p3-field")
    line(s, 95, 138, 163, 138, 0.36, "rail")
    tone(s, 95, 140, 163, 162, pitch=0.95, p=0.26, skip=0.52, seed=402, tag="p3-sea")
    rng = random.Random(404)
    for _ in range(22):
        x = rng.uniform(96, 160)
        y = rng.uniform(142, 160)
        line(s, x, y, x + rng.uniform(2.5, 5.5), y + rng.uniform(-0.3, 0.3), 0.22, "wave", taper=0.7)

    # Zoro: head, spiky hair, stern eye ticks, scar over his left brow,
    # crossed arms, three swords at the hip.
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
    line(s, 123.2, 131.0, 123.4, 133.4, 0.36, "zoro-scar", passes=1)
    stroke_through(s, (113.8, 139.6), (117.2, 140.6), (120.4, 139.4), 0.36, "zoro-mouth")
    stroke_through(s, (108.0, 150.0), (117.5, 146.0), (126.5, 149.6), 0.40, "zoro-arms", passes=2)
    for k in range(3):
        line(s, 107.0 + k * 1.4, 152.0 - k * 0.6, 102.5 + k * 1.2, 160.0 - k * 0.8, 0.40, "swords", passes=2)
        s.stroke(106.6 + k * 1.4, 151.4 - k * 0.6, 107.8 + k * 1.4, 150.8 - k * 0.6,
                 pressure_start=0.5, pressure_end=0.45, speed_mm_s=45, tag="swords")

    # Nami: hair mass in tone, surprised mouth-ring, surprise marks above.
    nhead = [(136.5, 133.0), (136.0, 128.5), (140.0, 125.5), (146.0, 125.2), (150.5, 128.4),
             (151.6, 133.5), (150.0, 138.5), (145.5, 140.8), (141.0, 139.6)]
    nhead.append((137.6, 134.4))
    s.stroke_path([v for p in nhead for v in p], pressure=0.42, speed_mm_s=55, tag="nami-head")
    tone(s, 136.0, 124.8, 152.4, 133.0, pitch=0.55, p=0.44, skip=0.10, seed=405, tag="nami-hair")
    line(s, 137.2, 132.6, 138.8, 133.4, 0.34, "nami-face", passes=2)
    line(s, 142.6, 132.8, 144.2, 133.6, 0.34, "nami-face", passes=2)
    stroke_through(s, (139.6, 137.4), (141.4, 138.6), (143.2, 137.4), 0.36, "nami-face")
    stroke_through(s, (139.4, 137.2), (141.4, 135.6), (143.4, 137.2), 0.36, "nami-face")
    for (x0, y0, x1, y1) in ((143.0, 117.0, 143.0, 121.5), (146.2, 118.0, 145.6, 122.0)):
        line(s, x0, y0, x1, y1, 0.40, "surprise")
    s.stroke(144.4, 114.6, 145.1, 115.4, pressure_start=0.52, pressure_end=0.48, speed_mm_s=40, tag="surprise")

    # Speed lines from the left edge (the punch happening off-panel).
    for _ in range(7):
        y0 = rng.uniform(108.0, 160.0)
        line(s, 95.5, y0, 95.5 + rng.uniform(14, 26), y0 + rng.uniform(-2.5, 2.5), 0.18, "speed", taper=0.45)

    # Balloon for the script.
    balloon(s, 138.0, 111.5, 17.0, 8.5)

    s.save()
    print("pass4 view:", s.view("pass4", px_per_cell=1))


def pass5() -> None:
    """P4: the Merry sails on — smaller, wake behind, Luffy on the figurehead."""
    s = get_session()
    s.select_tool("fineliner_03")

    tone(s, 13, 173, 163, 200, pitch=1.1, p=0.20, skip=0.72, seed=501, tag="p4-sky")
    tone(s, 40, 182, 52, 189, pitch=0.8, p=0.28, skip=0.25, seed=502, tag="p4-cloud")
    tone(s, 116, 178, 138, 184, pitch=0.8, p=0.28, skip=0.25, seed=503, tag="p4-cloud")
    for (x, y, w) in ((36, 190, 3.2), (44, 185.5, 2.6), (124, 188, 3.0)):
        stroke_through(s, (x, y), (x + w / 2, y - 1.6), (x + w, y), 0.30, "gull")
        stroke_through(s, (x, y + 0.5), (x + w / 2, y + 1.2), (x + w, y + 0.5), 0.30, "gull")

    # Sea.
    line(s, 14, 204, 162, 204, 0.40, "horizon")
    tone(s, 14, 205, 162, 212, pitch=1.0, p=0.24, skip=0.62, seed=504, tag="sea-far")
    rng = random.Random(505)
    y = 214.0
    while y <= 234.0:
        x = 15.0 + rng.uniform(0, 6)
        while x < 160.0:
            w = rng.uniform(3.0, 6.5)
            if rng.random() < 0.7:
                line(s, x, y, x + w, y + rng.uniform(-0.3, 0.3), 0.22 + 0.18 * (y - 210) / 26.0, "wave", taper=0.7)
            x += w + rng.uniform(2.0, 6.0)
        y += 2.2

    # The Merry, half scale, sailing left to right.
    hull = [(70, 213), (76, 217), (88, 218.5), (100, 217), (106, 213)]
    for i in range(len(hull) - 1):
        stroke_through(s, hull[i], ((hull[i][0] + hull[i + 1][0]) / 2, (hull[i][1] + hull[i + 1][1]) / 2 + 0.4),
                       hull[i + 1], 0.42, "hull", passes=2)
    line(s, 70, 212, 106, 212, 0.40, "deck", passes=2)
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
    line(s, 88.5, 210, 88.5, 184, 0.42, "mast", passes=2)
    line(s, 80, 187, 97, 187, 0.34, "yard")
    stroke_through(s, (81.5, 187.4), (80.4, 196.0), (83.0, 206.0), 0.38, "sail")
    stroke_through(s, (95.5, 187.4), (96.6, 196.0), (94.0, 206.0), 0.38, "sail")
    stroke_through(s, (83.0, 206.0), (88.5, 207.4), (94.0, 206.0), 0.36, "sail")
    tone(s, 83, 189, 94, 205, pitch=0.85, p=0.24, skip=0.45, seed=506, tag="sail-tone")
    line(s, 88.5, 184, 91.5, 185.0, 0.40, "flag")
    line(s, 91.5, 185.0, 88.5, 186.0, 0.40, "flag")

    # Wake behind the stern, foam at the bow.
    stroke_through(s, (106, 214.5), (122, 219.0), (138, 224.5), 0.30, "wake", passes=2)
    stroke_through(s, (106, 217.5), (124, 223.0), (140, 229.0), 0.26, "wake", passes=2)
    for _ in range(16):
        x = rng.uniform(58, 70)
        y = rng.uniform(213.5, 219.5)
        s.stroke(x, y, x + 0.5, y + 0.3, pressure_start=0.3, pressure_end=0.26, speed_mm_s=80, tag="foam")

    # Luffy on the figurehead, one arm thrown up — rubber, reaching.
    line(s, 66.5, 211.6, 66.2, 205.8, 0.40, "luffy-p4", passes=2)
    line(s, 65.8, 205.6, 64.2, 199.4, 0.36, "luffy-arm")
    stroke_through(s, (64.2, 199.4), (66.4, 197.2), (68.6, 198.4), 0.36, "luffy-arm")
    s.stroke(64.6, 205.2, 65.4, 204.9, pressure_start=0.46, pressure_end=0.42, speed_mm_s=45, tag="hat-p4")
    stroke_through(s, (64.0, 205.4), (65.0, 204.0), (66.2, 205.3), 0.44, "hat-p4", passes=2)
    # Two crew waving from the deck.
    for bx in (92.0, 99.0):
        line(s, bx, 211.4, bx - 0.3, 206.8, 0.36, "crew", passes=1)
        line(s, bx - 0.3, 206.6, bx - 1.6, 204.4, 0.30, "crew")

    # Balloon for the script.
    balloon(s, 44.0, 186.0, 16.0, 8.0)

    s.save()
    print("pass5 view:", s.view("pass5", px_per_cell=1))


def final() -> None:
    s = get_session()
    print("loupe:", s.view("loupe", region_mm=[12.0, 12.0, 164.0, 236.0], px_per_cell=1))
    s.note(
        "artist_statement",
        "A penciled page: Luffy and the crew aboard the Going Merry. Panel "
        "one finds the ship at sea; panel two comes close to the captain — "
        "the hat, the scar, the grin; panel three lets Zoro and Nami react "
        "to whatever the captain just decided; panel four sails on. The "
        "lettering is not here yet — the balloons wait for a script, because "
        "the hand cannot write. This is a fan study: the designs belong to "
        "Oda. What belongs to this hand is the practice — four panels of "
        "straightedges, screentone, and the ship we learned by drawing her "
        "twice.",
    )
    print("export:", s.export_artwork("manga_page_01"))
    kinds = {}
    for line_txt in (DIR / "log.jsonl").read_text().splitlines():
        import json

        rec = json.loads(line_txt)
        if rec["type"] == "stroke":
            kinds["strokes"] = kinds.get("strokes", 0) + 1
        elif rec["type"] == "view":
            kinds["views"] = kinds.get("views", 0) + 1
        elif rec["type"] == "note":
            k = rec.get("note_kind", "note")
            kinds[k] = kinds.get(k, 0) + 1
    print("session log:", kinds)


if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else "1"
    {"1": pass1, "2": pass2, "3": pass3, "4": pass4, "5": pass5, "final": final}[stage]()
