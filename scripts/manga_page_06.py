"""Manga page 6 — the slow pass. No shortcuts, tested primitives only.

Applied from RESEARCH.md and the user's critique:
  - hair is STRANDS: curved strokes per root along a flow direction, tapered
    — never stipple clouds (dot_fill retired for hair)
  - pupils are SOLID (tight dot fill) with a reserved white spec
  - the hat sits LOW: brim just above the eyes, no skyscraper forehead
  - every assembled part shares joints; crew are clothed line figures
    (head circle, vest outline, arms, legs) — not sticks, not censored bars
  - balloons come from panels.balloon: correct closure (no strike), full
    whiteout, tail pointing at the speaker, stamped script

Character designs © Eiichiro Oda / Shueisha — disclosed fan study.

Usage: python scripts/manga_page_06.py {1|2|3|4|final}
"""

import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from painterly.fonts import text_width_mm  # noqa: E402
from painterly.panels import balloon, gull, hair_strands, tone  # noqa: E402
from painterly.session import Session  # noqa: E402
from painterly.stroke import curvature_through  # noqa: E402

DIR = ROOT / "sessions" / "manga_page_06"

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
        seed=151,
        size_mm=(176.0, 250.0),
        cell_mm=0.2,
        artist_id="unnamed-artist-0",
        title="Going Merry — fan study, the slow pass",
    )


def lw_line(s, x0, y0, x1, y1, level, tag, taper=0.96, passes=1):
    p = LW[level]
    for _ in range(passes):
        s.stroke(x0, y0, x1, y1, pressure_start=p, pressure_end=p * taper,
                 speed_mm_s=70, tag=tag)


def stroke_through(s, a, mid, b, p, tag, speed=60.0, taper=0.88, passes=1):
    k = curvature_through(a, mid, b)
    for _ in range(passes):
        s.stroke(*a, *b, curvature=k, pressure_start=p, pressure_end=p * taper,
                 speed_mm_s=speed, tag=tag)


def dot_fill(s, cx, cy, rx, ry, p, tag, seed, pitch=0.34, skip=()):
    rng = random.Random(seed)
    y = cy - ry
    while y <= cy + ry:
        x = cx - rx
        while x <= cx + rx:
            if (x - cx) ** 2 / max(rx * rx, 1e-6) + (y - cy) ** 2 / max(ry * ry, 1e-6) <= 1.0:
                if any((x - hx) ** 2 + (y - hy) ** 2 <= hr * hr for hx, hy, hr in skip):
                    x += pitch
                    continue
                s.stroke(x, y, x + pitch * 0.7, y + pitch * 0.4,
                         pressure_start=p, pressure_end=p * 0.92, speed_mm_s=90, tag=tag)
            x += pitch
        y += pitch * 0.75


def deck_crew_line(s, x, deck_y, h, tag, hat=False, hair_spikes=False, nose=False):
    """A clothed LINE figure — head circle, vest outline, arms, legs — every
    joint shared, feet 0.2 into the deck line. No sticks, no censor bars."""
    y_top = deck_y - 0.2 - h
    head_r = h * 0.20
    hc = (x, y_top + head_r + 0.2)
    # head circle from two arcs through its side points
    stroke_through(s, (hc[0] - head_r, hc[1]),
                   (hc[0], hc[1] - head_r * 1.35), (hc[0] + head_r, hc[1]),
                   0.44, tag + "-head", passes=2)
    stroke_through(s, (hc[0] - head_r, hc[1]),
                   (hc[0], hc[1] + head_r * 1.25), (hc[0] + head_r, hc[1]),
                   0.44, tag + "-head", passes=2)
    neck_top = hc[1] + head_r * 1.15
    hip_y = deck_y - 0.2 - h * 0.28
    # vest outline: neck -> shoulder out -> hem in (closed-ish torso)
    lw_line(s, x, neck_top, x - h * 0.15, neck_top + h * 0.10, "struct", tag + "-vest")
    lw_line(s, x, neck_top, x + h * 0.15, neck_top + h * 0.10, "struct", tag + "-vest")
    lw_line(s, x - h * 0.15, neck_top + h * 0.10, x - h * 0.11, hip_y, "struct", tag + "-vest")
    lw_line(s, x + h * 0.15, neck_top + h * 0.10, x + h * 0.11, hip_y, "struct", tag + "-vest")
    lw_line(s, x - h * 0.11, hip_y, x + h * 0.11, hip_y, "struct", tag + "-vest")
    # legs share the hip corners
    lw_line(s, x - h * 0.09, hip_y, x - h * 0.10, deck_y - 0.2, "struct", tag + "-leg")
    lw_line(s, x + h * 0.09, hip_y, x + h * 0.10, deck_y - 0.2, "struct", tag + "-leg")
    # arms from the shoulder corners
    lw_line(s, x - h * 0.14, neck_top + h * 0.12, x - h * 0.22, neck_top + h * 0.34,
            "struct", tag + "-arm")
    lw_line(s, x + h * 0.14, neck_top + h * 0.12, x + h * 0.22, neck_top + h * 0.34,
            "struct", tag + "-arm")
    if hat:
        lw_line(s, x - head_r * 1.5, hc[1] - head_r * 0.15, x + head_r * 1.5, hc[1] - head_r * 0.15,
                "outline", tag + "-hat-brim", passes=2)
        stroke_through(s, (x - head_r * 1.2, hc[1] - head_r * 0.3),
                       (x, hc[1] - head_r * 2.3), (x + head_r * 1.2, hc[1] - head_r * 0.3),
                       0.5, tag + "-hat-dome", passes=2)
    if hair_spikes:
        for dx, dy in ((-0.6, -1.2), (0.0, -1.5), (0.6, -1.2)):
            lw_line(s, x + dx * head_r * 0.6, hc[1] - head_r * 0.4,
                    x + dx * head_r * 1.2, hc[1] - head_r * 0.4 + dy, "struct", tag + "-hair")
    if nose:
        lw_line(s, x - head_r * 0.8, hc[1] + head_r * 0.1, x - head_r * 2.0, hc[1],
                "struct", tag + "-nose")


def pass1() -> None:
    s = get_session()
    s.note(
        "derivative_work",
        "Fan study, page 6. One Piece © Eiichiro Oda / Shueisha — "
        "interpretation from memory, disclosed, non-commercial.",
    )
    s.note(
        "material_choice",
        "The slow pass. Panel primitives moved into tested shared code "
        "(panels.py) after the balloon-closure strike bug survived three "
        "pages by copy-paste. Hair is strands now — curved, tapered, one "
        "flow direction. Pupils are solid with a reserved spec. The hat "
        "sits LOW. Crew are clothed line figures with shared joints. No "
        "shortcuts per panel.",
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
    """P1: the Merry; crew as clothed line figures rooted on the deck."""
    s = get_session()
    s.select_tool("fineliner_03")

    tone(s, 14, 14, 162, 46, pitch=1.15, p=0.20, skip=0.78, seed=161, tag="sky")
    tone(s, 26, 24, 44, 31, pitch=0.8, p=0.28, skip=0.25, seed=162, tag="cloud")
    tone(s, 122, 27, 148, 33, pitch=0.8, p=0.28, skip=0.25, seed=163, tag="cloud")
    lw_line(s, 14, 50, 162, 50, "bg", "horizon")
    tone(s, 14, 51, 162, 60, pitch=1.05, p=0.24, skip=0.66, seed=164, tag="sea-far")
    rng = random.Random(861)
    y = 62.0
    while y <= 92.0:
        x = 15.0 + rng.uniform(0, 6)
        while x < 160.0:
            w = rng.uniform(3.0, 7.0)
            if rng.random() < 0.68:
                lw_line(s, x, y, x + w, y + rng.uniform(-0.3, 0.3), "bg", "wave", taper=0.7)
            x += w + rng.uniform(2.0, 6.0)
        y += 2.3

    # Crew: clothed line figures BEFORE the bulwark (it will occlude legs).
    deck_crew_line(s, 74.5, 67.6, 7.2, "usopp", nose=True)
    deck_crew_line(s, 80.0, 67.6, 7.4, "zoro", hair_spikes=True)
    deck_crew_line(s, 86.0, 67.6, 7.0, "nami")
    deck_crew_line(s, 97.5, 67.6, 7.6, "luffy", hat=True)

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
    tone(s, 80, 32, 97, 54, pitch=0.95, p=0.24, skip=0.48, seed=165, tag="sail-tone")
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
    """P2: Luffy declares — low hat, strand hair, solid pupils, open mouth,
    clothed bust, lettered balloon from the tested primitive."""
    s = get_session()
    s.select_tool("fineliner_03")

    tone(s, 13, 105, 85, 163, pitch=1.05, p=0.20, skip=0.70, seed=811, tag="p2-field")

    # Head: egg — the hat will sit LOW, so the forehead is short.
    head = [
        (30.0, 130.0), (28.2, 138.5), (30.5, 147.0), (37.0, 153.8), (44.5, 155.8),
        (52.5, 153.8), (58.8, 147.0), (61.0, 138.0), (59.0, 129.5), (54.0, 123.5),
        (46.5, 121.8),
    ]
    head.append((32.5, 126.0))
    s.stroke_path([v for p in head for v in p], pressure=0.46, speed_mm_s=55, tag="face")

    # Straw hat seated LOW: brim just above the eyes.
    stroke_through(s, (27.5, 128.5), (44.5, 113.5), (61.5, 127.5), 0.52, "hat", passes=2)
    stroke_through(s, (29.0, 125.5), (44.5, 119.5), (60.0, 124.5), 0.44, "band", passes=2)
    stroke_through(s, (23.0, 129.0), (44.5, 122.0), (65.5, 128.8), 0.52, "brim", passes=2)
    tone(s, 32, 117, 58, 122, pitch=0.8, p=0.30, skip=0.35, seed=812, tag="hat-tone")

    # Hair: strands at the temples following the flow DOWN the cheeks.
    hair_strands(s, [(30.2, 129.5), (30.8, 132.0), (31.4, 134.5)],
                 (-0.25, 1.0), length=4.2, n=4, p=0.42,
                 seed=821, tag="hair-L", taper=0.45)
    hair_strands(s, [(59.2, 129.5), (58.8, 132.0), (58.2, 134.5)],
                 (0.25, 1.0), length=4.2, n=4, p=0.42, seed=822, tag="hair-R", taper=0.45)
    # forehead notch under the band
    stroke_through(s, (41.6, 126.0), (43.2, 128.2), (44.8, 126.2), 0.46, "hair-notch", taper=0.85)
    stroke_through(s, (44.8, 126.2), (46.2, 128.4), (47.6, 126.0), 0.46, "hair-notch", taper=0.85)
    stroke_through(s, (28.0, 137.0), (26.6, 140.0), (28.4, 142.2), 0.36, "ear", taper=0.9)
    stroke_through(s, (60.4, 136.6), (61.8, 139.4), (60.0, 141.6), 0.36, "ear", taper=0.9)

    # Eyes: LARGE with SOLID pupils and a white spec each.
    def eye(cx, flip):
        stroke_through(s, (cx - 4.2, flip * 0 + 140.6 - flip * 0), (cx, 139.4),
                       (cx + 4.2, 140.6), 0.52, "eye-lid", passes=2)
        dot_fill(s, cx + flip * 0.35, 141.6, 1.05, 1.25, 0.66, "pupil", seed=int(cx * 7),
                 pitch=0.3, skip=[(cx - flip * 0.45, 140.9, 0.34)])
        lw_line(s, cx - 2.6, 143.6, cx + 2.6, 143.6, "bg", "eye-lower")

    eye(37.5, 1.0)
    eye(51.0, -1.0)
    lw_line(s, 52.4, 144.6, 54.8, 143.6, "detail", "scar", passes=2)
    lw_line(s, 53.4, 145.8, 55.6, 144.4, "detail", "scar")
    lw_line(s, 45.0, 143.6, 45.8, 145.2, "detail", "nose")

    # OPEN SHOUT.
    mouth = []
    for i in range(11):
        a = 2 * math.pi * i / 10
        mouth.append((44.4 + 8.4 * math.cos(a), 152.0 + 5.0 * math.sin(a)))
    mouth.append(mouth[0])
    for i in range(len(mouth) - 1):
        a, b = mouth[i], mouth[i + 1]
        m = (44.4 + 1.1 * ((a[0] + b[0]) / 2 - 44.4), 152.0 + 1.1 * ((a[1] + b[1]) / 2 - 152.0))
        stroke_through(s, a, m, b, 0.52, "shout", passes=2)
    lw_line(s, 38.0, 150.0, 51.0, 150.0, "detail", "teeth", passes=1)
    stroke_through(s, (40.4, 154.6), (44.4, 155.8), (48.4, 154.6), 0.30, "tongue")

    # Neck, shoulders, vest, chest — the bust, cropped by the border.
    lw_line(s, 39.6, 156.4, 39.0, 163.8, "struct", "neck", passes=2)
    lw_line(s, 49.4, 156.0, 50.0, 163.8, "struct", "neck", passes=2)
    stroke_through(s, (28.5, 163.8), (38.0, 157.2), (41.0, 155.9), 0.52, "shoulder", passes=2)
    stroke_through(s, (61.5, 163.8), (51.5, 156.6), (48.2, 155.6), 0.52, "shoulder", passes=2)
    lw_line(s, 34.0, 163.8, 39.4, 158.4, "struct", "vest")
    lw_line(s, 55.0, 163.8, 49.8, 158.2, "struct", "vest")
    lw_line(s, 39.4, 158.4, 44.4, 157.2, "detail", "collar")
    lw_line(s, 44.4, 157.2, 49.8, 158.2, "detail", "collar")

    # The declaration, from the tested balloon primitive.
    balloon(s, 64.0, 111.5, 18.5, 10.0,
            ["I'M GONNA BE", "KING OF THE", "PIRATES!!"], font_h=2.3,
            tail=(50.0, 122.0), subdabs=2)

    s.save()
    print("pass3 view:", s.view("pass3", px_per_cell=1))


def pass4() -> None:
    """P3 + P4: reactions with lettered balloons; the Merry sails on; Luffy
    stands line-drawn on the ram's head."""
    s = get_session()
    s.select_tool("fineliner_03")

    tone(s, 95, 105, 163, 163, pitch=1.05, p=0.20, skip=0.70, seed=921, tag="p3-field")
    lw_line(s, 95, 139, 163, 139, "detail", "rail")
    tone(s, 95, 141, 163, 162, pitch=0.95, p=0.24, skip=0.56, seed=922, tag="p3-sea")
    rng = random.Random(923)
    for _ in range(18):
        x = rng.uniform(96, 160)
        y = rng.uniform(144, 160)
        lw_line(s, x, y, x + rng.uniform(2.5, 5.5), y + rng.uniform(-0.3, 0.3), "bg", "wave", taper=0.7)

    # Zoro: strand cap, solid pupils, three real swords.
    zhead = [(108.5, 127.0), (107.0, 135.0), (110.0, 142.5), (117.0, 145.5), (124.5, 142.5),
             (127.0, 135.0), (125.5, 127.4), (118.0, 124.6)]
    zhead.append((110.2, 126.4))
    s.stroke_path([v for p in zhead for v in p], pressure=0.46, speed_mm_s=55, tag="zoro-head")
    hair_strands(s, [(110.4, 129.0), (113.4, 127.8), (117.0, 127.2), (120.6, 127.6), (123.8, 128.6)],
                 (0.0, -1.0), length=3.6, n=4, p=0.46, seed=924, tag="zoro-hair", taper=0.6)
    lw_line(s, 110.4, 133.0, 115.8, 134.2, "struct", "zoro-brow", passes=2)
    lw_line(s, 120.2, 134.0, 125.6, 133.0, "struct", "zoro-brow", passes=2)
    dot_fill(s, 113.4, 136.2, 0.95, 1.1, 0.68, "zoro-pupil", seed=925, pitch=0.32,
             skip=[(112.9, 135.6, 0.32)])
    dot_fill(s, 121.6, 136.0, 0.95, 1.1, 0.68, "zoro-pupil", seed=926, pitch=0.32,
             skip=[(121.1, 135.4, 0.32)])
    lw_line(s, 123.4, 132.2, 123.6, 134.6, "detail", "zoro-scar")
    stroke_through(s, (113.8, 141.4), (117.2, 142.4), (120.4, 141.2), 0.36, "zoro-mouth")
    lw_line(s, 114.0, 145.8, 113.6, 150.5, "struct", "neck", passes=2)
    lw_line(s, 121.0, 145.4, 121.4, 150.2, "struct", "neck", passes=2)
    stroke_through(s, (104.0, 158.5), (112.0, 149.8), (117.0, 149.2), 0.52, "shoulder", passes=2)
    stroke_through(s, (132.0, 157.5), (123.5, 149.4), (121.6, 149.2), 0.52, "shoulder", passes=2)
    stroke_through(s, (106.0, 158.0), (117.5, 153.6), (128.5, 156.6), 0.44, "arms", passes=2)
    stroke_through(s, (107.5, 160.5), (117.5, 155.8), (126.0, 158.8), 0.40, "arms", passes=2)
    for k, dx in enumerate((0.0, 1.6, 3.2)):
        bx = 105.0 + dx
        lw_line(s, bx, 150.0, bx - 0.9, 162.0, "outline", "sword-blade", passes=2)
        lw_line(s, bx - 1.5, 149.7, bx + 1.5, 150.4, "struct", "sword-guard")
        lw_line(s, bx - 0.4, 148.2, bx + 0.8, 149.2, "struct", "sword-hilt")

    # Nami: strand hair with a part, falling sides; ring-eye shock; shoulders.
    nhead = [(137.5, 133.5), (137.0, 129.0), (140.0, 126.0), (147.0, 125.7), (151.5, 129.0),
             (152.6, 134.0), (151.0, 139.0), (146.5, 141.3), (142.0, 140.1)]
    nhead.append((138.6, 134.9))
    s.stroke_path([v for p in nhead for v in p], pressure=0.46, speed_mm_s=55, tag="nami-head")
    hair_strands(s, [(144.0, 126.2), (141.5, 126.8), (146.5, 126.6)],
                 (0.0, 1.0), length=8.5, n=6, p=0.40, seed=927, tag="nami-hair", taper=0.5)
    hair_strands(s, [(138.0, 129.0), (137.4, 133.0)], (-0.4, 1.0), length=7.0, n=4,
                 p=0.38, seed=928, tag="nami-hair", taper=0.5)
    hair_strands(s, [(150.6, 129.5), (151.4, 133.0)], (0.4, 1.0), length=7.0, n=4,
                 p=0.38, seed=929, tag="nami-hair", taper=0.5)
    lw_line(s, 138.6, 133.6, 140.2, 134.4, "detail", "nami-eye-lid", passes=2)
    s.stroke(139.4, 135.2, 140.0, 136.2, pressure_start=0.62, pressure_end=0.56, speed_mm_s=40, tag="nami-pupil")
    lw_line(s, 143.8, 133.8, 145.4, 134.6, "detail", "nami-eye-lid", passes=2)
    s.stroke(144.6, 135.4, 145.2, 136.4, pressure_start=0.62, pressure_end=0.56, speed_mm_s=40, tag="nami-pupil")
    stroke_through(s, (140.8, 139.2), (142.4, 140.2), (144.0, 139.2), 0.30, "nami-o-mouth")
    lw_line(s, 144.9, 116.5, 144.9, 121.0, "detail", "surprise")
    lw_line(s, 148.1, 117.5, 147.5, 121.5, "detail", "surprise")
    s.stroke(146.3, 114.1, 147.0, 114.9, pressure_start=0.52, pressure_end=0.48, speed_mm_s=40, tag="surprise")
    stroke_through(s, (135.0, 158.5), (142.5, 150.5), (146.0, 149.8), 0.52, "shoulder", passes=2)
    stroke_through(s, (163.8, 157.0), (153.0, 150.0), (149.0, 149.6), 0.52, "shoulder", passes=2)
    lw_line(s, 145.0, 149.8, 144.4, 163.8, "struct", "neck", passes=2)

    balloon(s, 139.0, 111.0, 17.5, 9.0, ["EVERY SINGLE", "DAY...!!"], font_h=2.4,
            tail=(142.0, 124.0), subdabs=2)

    # P4: sails on; gulls from the primitive; Luffy line-drawn ON the ram.
    tone(s, 13, 173, 163, 200, pitch=1.15, p=0.18, skip=0.76, seed=931, tag="p4-sky")
    tone(s, 118, 179, 140, 186, pitch=0.8, p=0.26, skip=0.25, seed=932, tag="p4-cloud")
    gull(s, 102, 178, 4.0)
    gull(s, 120, 190, 3.4)
    lw_line(s, 14, 204, 162, 204, "bg", "horizon")
    tone(s, 14, 205, 162, 212, pitch=1.0, p=0.22, skip=0.66, seed=933, tag="sea-far")
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
    tone(s, 83, 189, 94, 205, pitch=0.85, p=0.24, skip=0.45, seed=934, tag="sail-tone")
    lw_line(s, 88.5, 184, 91.5, 185.0, "detail", "flag")
    lw_line(s, 91.5, 185.0, 88.5, 186.0, "detail", "flag")
    stroke_through(s, (106, 214.5), (122, 219.0), (138, 224.5), 0.30, "wake", passes=2)
    stroke_through(s, (106, 217.5), (124, 223.0), (140, 229.0), 0.26, "wake", passes=2)
    for _ in range(16):
        x = rng.uniform(58, 70)
        y = rng.uniform(213.5, 219.5)
        s.stroke(x, y, x + 0.5, y + 0.3, pressure_start=0.3, pressure_end=0.26, speed_mm_s=80, tag="foam")

    # Luffy, clothed line figure, standing ON the ram's head (contact).
    deck_crew_line(s, 66.5, 205.0, 7.0, "luffy-p4", hat=True)

    balloon(s, 44.0, 186.0, 16.5, 8.5, ["SET SAIL!"], font_h=2.5,
            tail=(52.0, 196.0), subdabs=2)

    s.save()
    print("pass4 view:", s.view("pass4", px_per_cell=1))


def final() -> None:
    s = get_session()
    print("loupe:", s.view("loupe", region_mm=[12.0, 12.0, 164.0, 236.0], px_per_cell=1))
    s.note(
        "artist_statement",
        "Page six: the slow pass, no shortcuts per panel. Hair is strands — "
        "curved, tapered, one flow; pupils are solid with a white spec; the "
        "hat sits low over a short forehead; the crew are clothed line "
        "figures rooted on the deck; and the balloons close properly, tails "
        "pointing at their speakers, whitened and stamped. Every primitive "
        "on this page is tested code. Designs © Oda/Shueisha; the practice "
        "is ours.",
    )
    print("export:", s.export_artwork("manga_page_06"))
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
