"""Manga page 4 — the reference-informed pass.

Read from the provided One Piece pages (see RESEARCH.md):
  - busts crop at the CHEST; the border cuts the body on purpose
  - grounding is draw-order: crew drawn first, the rail/bulwark drawn over
    their legs — feet planted on a deck floor that exists between two lines
  - hair is a solid black mass with white accent cuts, not outlines
  - OP eyes are small and BOLD: heavy upper lid, solid pupil, one white spec
  - speed lines belong to ACTION panels; talking panels keep faces clean
  - balloons: full whiteout coverage, lettering subdabbed for weight

Character designs © Eiichiro Oda / Shueisha — disclosed fan study.

Usage: python scripts/manga_page_04.py {1|2|3|4|final}
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

DIR = ROOT / "sessions" / "manga_page_04b"

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
        seed=131,
        size_mm=(176.0, 250.0),
        cell_mm=0.2,
        artist_id="unnamed-artist-0",
        title="Going Merry — fan study, grounded and lettered",
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


def figure(s, x, feet_y, h=6.6, tag="crew", hat=False, hair_spikes=False, nose=False):
    """Connected figure: one continuous stroke head-to-hip, legs from the hip,
    head dab overlapping the neck, feet landing ON feet_y (+0.2 into it)."""
    y_top = feet_y - h
    head_r = h * 0.16
    stroke_through(s, (x - head_r, y_top + head_r * 0.9),
                   (x, y_top - head_r * 0.55), (x + head_r, y_top + head_r * 0.9),
                   0.44, tag + "-head", passes=2)
    s.stroke(x - head_r * 0.5, y_top + head_r * 1.5, x + head_r * 0.5, y_top + head_r * 1.5,
             pressure_start=0.42, pressure_end=0.4, speed_mm_s=50, tag=tag + "-head")
    pts = [(x, y_top + head_r * 1.9), (x, y_top + h * 0.30), (x, feet_y - h * 0.48 + 0.2)]
    s.stroke_path([v for p in pts for v in p], pressure=0.4, speed_mm_s=55, tag=tag + "-body")
    hip_y = feet_y - h * 0.48 + 0.2
    s.stroke(x, hip_y, x - h * 0.16, feet_y + 0.2, pressure_start=0.38, pressure_end=0.32,
             speed_mm_s=55, tag=tag + "-leg")
    s.stroke(x, hip_y, x + h * 0.16, feet_y + 0.2, pressure_start=0.38, pressure_end=0.32,
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
        for dx, dy in ((-0.5, -1.0), (0.0, -1.3), (0.5, -1.0)):
            s.stroke(x + dx * head_r * 0.7, y_top - 0.1, x + dx * head_r * 1.3, y_top - 0.1 + dy,
                     pressure_start=0.44, pressure_end=0.36, speed_mm_s=50, tag=tag + "-hair")
    if nose:
        s.stroke(x - head_r * 0.9, y_top + head_r * 1.05, x - head_r * 2.2, y_top + head_r * 0.95,
                 pressure_start=0.46, pressure_end=0.4, speed_mm_s=45, tag=tag + "-nose")


def balloon_lettered(s, cx, cy, rx, ry, lines, font_h=2.8):
    """FULL whiteout coverage of the interior (no dash survivors), outline,
    tail, then subdabbed type auto-fit with breathing room."""
    max_chars = max(len(l) for l in lines)
    fit_h = min(font_h,
                (ry * 2 * 0.60) / (len(lines) * 1.5),
                (rx * 2 * 0.66) / (max_chars * 6 / 7))
    width = min(4.6, ry * 0.75)
    yy = cy - ry * 0.82
    while yy <= cy + ry * 0.82:
        s.whiteout(cx - rx * 0.86, yy, cx + rx * 0.86, yy + 0.3,
                   width_mm=width, strength=0.97, tag="whiteout")
        yy += width * 0.42
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


def pass1() -> None:
    s = get_session()
    s.note(
        "derivative_work",
        "Fan study, page 4. One Piece © Eiichiro Oda / Shueisha — "
        "interpretation from memory, disclosed, non-commercial.",
    )
    s.note(
        "material_choice",
        "Reference-page pass. Busts crop at the chest with the border cutting "
        "the body. Grounding is draw order: crew first, then the bulwark "
        "drawn OVER their legs — feet on a deck floor that exists between two "
        "lines. Hair is a solid black mass with white cuts. OP eyes: small, "
        "bold, solid pupil with one white spec. Speed lines only at action. "
        "Balloons get full whiteout coverage before subdabbed letterpress. "
        "The cabin rides in both ship views.",
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
    """P1: the Merry, crew BEHIND the bulwark (drawn before it)."""
    s = get_session()
    s.select_tool("fineliner_03")

    tone(s, 14, 14, 162, 46, pitch=1.15, p=0.20, skip=0.78, seed=131, tag="sky")
    tone(s, 26, 24, 44, 31, pitch=0.8, p=0.28, skip=0.25, seed=132, tag="cloud")
    tone(s, 122, 27, 148, 33, pitch=0.8, p=0.28, skip=0.25, seed=133, tag="cloud")
    lw_line(s, 14, 50, 162, 50, "bg", "horizon")
    tone(s, 14, 51, 162, 60, pitch=1.05, p=0.24, skip=0.66, seed=134, tag="sea-far")
    rng = random.Random(431)
    y = 62.0
    while y <= 92.0:
        x = 15.0 + rng.uniform(0, 6)
        while x < 160.0:
            w = rng.uniform(3.0, 7.0)
            if rng.random() < 0.68:
                lw_line(s, x, y, x + w, y + rng.uniform(-0.3, 0.3), "bg", "wave", taper=0.7)
            x += w + rng.uniform(2.0, 6.0)
        y += 2.3

    # CREW FIRST — they stand behind the bulwark, which will be drawn over
    # their legs. Feet land ON the deck floor line (67.5) + 0.1.
    figure(s, 74.5, feet_y=67.6, h=7.0, tag="usopp", nose=True)
    figure(s, 80.0, feet_y=67.6, h=7.2, tag="zoro", hair_spikes=True)
    figure(s, 86.0, feet_y=67.6, h=6.8, tag="nami")
    figure(s, 97.5, feet_y=67.6, h=7.4, tag="luffy", hat=True)

    # Hull (silhouette weight), then rail + deck floor OVER the crew legs.
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

    # Figurehead: neck grows from inside the hull into the head.
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

    # Mast rooted in the keel; sail; flag; rigging; cabin.
    lw_line(s, 89, 70.0, 89, 26, "struct", "mast", passes=2)
    lw_line(s, 76, 30, 102, 30, "struct", "yard")
    stroke_through(s, (78.5, 30.5), (77.0, 42.0), (80.5, 55.0), 0.40, "sail")
    stroke_through(s, (99.5, 30.5), (101.0, 42.0), (97.5, 55.0), 0.40, "sail")
    stroke_through(s, (78.5, 55.0), (88.5, 56.8), (97.5, 55.0), 0.38, "sail")
    tone(s, 80, 32, 97, 54, pitch=0.95, p=0.24, skip=0.48, seed=135, tag="sail-tone")
    lw_line(s, 89, 26, 93.5, 27.2, "detail", "flag")
    lw_line(s, 93.5, 27.2, 89, 28.4, "detail", "flag")
    lw_line(s, 89, 30, 66.5, 63.0, "bg", "rigging")
    lw_line(s, 89, 30, 112.5, 62.0, "bg", "rigging")
    lw_line(s, 104, 67.5, 104, 54, "struct", "cabin")
    lw_line(s, 104, 54, 112, 55, "struct", "cabin")
    lw_line(s, 112, 55, 113, 68.0, "struct", "cabin")

    # Sea glints carved with white-out.
    for gx in (30, 74, 128):
        s.whiteout(gx, 55 + (gx % 3) * 2, gx + 12, 56.5 + (gx % 3) * 2,
                   width_mm=2.2, strength=0.6, tag="sea-glint")

    s.save()
    print("pass2 view:", s.view("pass2", px_per_cell=1))


def eye(s, cx, cy, flip=1.0, scale=1.0):
    """OP-shonen eye: heavy upper lid, cast shadow, SOLID pupil, one white
    spec reserved in the fill, faint lower line. Small and bold."""
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


def pass3() -> None:
    """P2: Luffy BUST — head, neck, shoulders, open vest; cropped by the
    panel. Solid hair masses; small bold eyes with solid pupils."""
    s = get_session()
    s.select_tool("fineliner_03")

    tone(s, 13, 105, 85, 163, pitch=1.05, p=0.20, skip=0.70, seed=521, tag="p2-field")

    # Head: egg, taller than wide — silhouette weight.
    head = [
        (29.5, 128.0), (27.8, 137.0), (30.0, 146.5), (36.5, 153.5), (44.5, 155.5),
        (52.5, 153.5), (59.0, 146.5), (61.2, 137.5), (59.5, 128.5), (54.5, 122.0),
        (46.0, 120.2),
    ]
    head.append((32.0, 124.0))
    s.stroke_path([v for p in head for v in p], pressure=0.46, speed_mm_s=55, tag="face")

    # Straw hat: dome, band, wide brim.
    stroke_through(s, (26.0, 124.0), (44.0, 107.5), (62.5, 123.0), 0.52, "hat", passes=2)
    stroke_through(s, (27.5, 121.0), (44.0, 115.0), (60.8, 120.0), 0.44, "band", passes=2)
    stroke_through(s, (21.5, 124.5), (44.0, 117.5), (66.5, 124.0), 0.52, "brim", passes=2)
    tone(s, 31, 110, 58, 116, pitch=0.8, p=0.30, skip=0.35, seed=522, tag="hat-tone")

    # Hair: SOLID black masses at the temples + the forehead notch.
    dot_fill(s, 29.8, 128.5, 2.0, 4.2, 0.58, "hair", seed=531)
    dot_fill(s, 58.6, 128.5, 2.0, 4.2, 0.58, "hair", seed=532)
    stroke_through(s, (40.6, 121.2), (42.2, 123.6), (43.8, 121.8), 0.46, "hair-notch", taper=0.85)
    stroke_through(s, (43.8, 121.8), (45.2, 124.0), (46.6, 121.6), 0.46, "hair-notch", taper=0.85)
    stroke_through(s, (27.2, 135.5), (25.6, 138.5), (27.6, 140.6), 0.36, "ear", taper=0.9)
    stroke_through(s, (61.0, 135.0), (62.6, 137.8), (60.8, 140.0), 0.36, "ear", taper=0.9)

    # Small bold eyes: lids, cast shadow, solid pupil with a white spec.
    eye(s, 37.5, 137.5, flip=1.0, scale=1.05)
    eye(s, 51.5, 137.5, flip=-1.0, scale=1.05)
    lw_line(s, 52.2, 142.6, 54.6, 141.6, "detail", "scar", passes=2)
    lw_line(s, 53.2, 143.8, 55.4, 142.4, "detail", "scar")
    lw_line(s, 45.0, 141.5, 45.8, 143.2, "detail", "nose")

    # OPEN SHOUT — outline weight, teeth, tongue.
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

    # NECK + SHOULDERS + CHEST: the bust exists, cropped by the panel border.
    lw_line(s, 39.8, 155.8, 39.2, 163.8, "struct", "neck", passes=2)
    lw_line(s, 48.8, 155.4, 49.4, 163.8, "struct", "neck", passes=2)
    stroke_through(s, (28.0, 163.8), (37.0, 156.8), (39.6, 155.6), 0.52, "shoulder", passes=2)
    stroke_through(s, (61.0, 163.8), (51.5, 156.6), (48.9, 155.4), 0.52, "shoulder", passes=2)
    lw_line(s, 35.5, 163.8, 40.2, 158.6, "struct", "vest")
    lw_line(s, 53.0, 163.8, 48.4, 158.4, "struct", "vest")

    # A few action marks at the panel edge, away from the face.
    rng = random.Random(541)
    for _ in range(5):
        y0 = rng.uniform(112.0, 130.0)
        lw_line(s, 13.5, y0, 13.5 + rng.uniform(6, 12), y0 + rng.uniform(-1.5, 1.5), "bg", "speed", taper=0.5)

    # The stamped declaration in a fully-whitened balloon.
    balloon_lettered(s, 63.0, 112.5, 17.5, 9.5,
                     ["I'M GONNA BE", "KING OF THE", "PIRATES!!"], font_h=2.6)

    s.save()
    print("pass3 view:", s.view("pass3", px_per_cell=1))


def pass4() -> None:
    """P3: Zoro and Nami as busts; P4: Merry sails on, Luffy ON the ram."""
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

    # ZORO BUST: solid hair cap, stern eyes, crossed arms, three swords.
    zhead = [(108.5, 127.0), (107.0, 135.0), (110.0, 142.5), (117.0, 145.5), (124.5, 142.5),
             (127.0, 135.0), (125.5, 127.4), (118.0, 124.6)]
    zhead.append((110.2, 126.4))
    s.stroke_path([v for p in zhead for v in p], pressure=0.46, speed_mm_s=55, tag="zoro-head")
    dot_fill(s, 117.2, 126.8, 7.0, 3.6, 0.58, "zoro-hair", seed=624,
             skip=[(110.6, 125.6, 1.1), (114.4, 124.2, 1.0), (121.0, 123.9, 1.0), (124.6, 125.2, 1.0)])
    lw_line(s, 109.9, 123.5, 107.2, 120.0, "struct", "zoro-hair-spike", passes=2)
    lw_line(s, 124.3, 123.6, 126.8, 120.4, "struct", "zoro-hair-spike", passes=2)
    lw_line(s, 110.4, 133.0, 115.8, 134.2, "struct", "zoro-brow", passes=2)
    lw_line(s, 120.2, 134.0, 125.6, 133.0, "struct", "zoro-brow", passes=2)
    eye(s, 113.4, 136.0, flip=1.0, scale=0.9)
    eye(s, 121.4, 135.8, flip=-1.0, scale=0.9)
    lw_line(s, 123.4, 132.2, 123.6, 134.6, "detail", "zoro-scar")
    stroke_through(s, (113.8, 141.4), (117.2, 142.4), (120.4, 141.2), 0.36, "zoro-mouth")
    # neck + shoulders + chest + crossed arms
    lw_line(s, 114.0, 145.8, 113.6, 150.5, "struct", "neck", passes=2)
    lw_line(s, 121.0, 145.4, 121.4, 150.2, "struct", "neck", passes=2)
    stroke_through(s, (104.0, 158.5), (112.0, 149.8), (117.0, 149.2), 0.52, "shoulder", passes=2)
    stroke_through(s, (132.0, 157.5), (123.5, 149.4), (121.6, 149.2), 0.52, "shoulder", passes=2)
    stroke_through(s, (106.0, 158.0), (117.5, 153.6), (128.5, 156.6), 0.44, "arms", passes=2)
    stroke_through(s, (107.5, 160.5), (117.5, 155.8), (126.0, 158.8), 0.40, "arms", passes=2)
    for k in range(3):
        lw_line(s, 104.5 + k * 1.5, 160.0 - k * 0.7, 99.5 + k * 1.3, 163.8, "struct", "swords", passes=2)
        s.stroke(104.1 + k * 1.5, 159.4 - k * 0.7, 105.4 + k * 1.5, 158.8 - k * 0.6,
                 pressure_start=0.5, pressure_end=0.45, speed_mm_s=45, tag="swords")

    # NAMI BUST: tone hair shaped as a mass, surprise ring-eye, small mouth.
    nhead = [(137.5, 133.5), (137.0, 129.0), (141.0, 126.0), (147.0, 125.7), (151.5, 129.0),
             (152.6, 134.0), (151.0, 139.0), (146.5, 141.3), (142.0, 140.1)]
    nhead.append((138.6, 134.9))
    s.stroke_path([v for p in nhead for v in p], pressure=0.46, speed_mm_s=55, tag="nami-head")
    tone(s, 137.0, 125.2, 151.6, 130.8, pitch=0.55, p=0.44, skip=0.10, seed=625, tag="nami-hair")
    lw_line(s, 137.6, 131.2, 137.0, 137.5, "struct", "nami-hair-edge", passes=2)
    lw_line(s, 151.2, 130.6, 151.8, 137.0, "struct", "nami-hair-edge", passes=2)
    lw_line(s, 138.6, 133.2, 140.2, 134.0, "detail", "nami-eye-lid", passes=2)
    s.stroke(139.3, 134.9, 139.9, 135.8, pressure_start=0.6, pressure_end=0.55, speed_mm_s=40, tag="nami-pupil")
    lw_line(s, 143.6, 133.4, 145.2, 134.2, "detail", "nami-eye-lid", passes=2)
    s.stroke(144.4, 135.1, 145.0, 136.0, pressure_start=0.6, pressure_end=0.55, speed_mm_s=40, tag="nami-pupil")
    stroke_through(s, (140.8, 138.8), (142.4, 139.8), (144.0, 138.8), 0.30, "nami-o-mouth")
    lw_line(s, 144.9, 116.5, 144.9, 121.0, "detail", "surprise")
    lw_line(s, 148.1, 117.5, 147.5, 121.5, "detail", "surprise")
    s.stroke(146.3, 114.1, 147.0, 114.9, pressure_start=0.52, pressure_end=0.48, speed_mm_s=40, tag="surprise")
    # her shoulders, cropped by the panel
    stroke_through(s, (135.0, 158.5), (142.5, 150.5), (146.0, 149.8), 0.52, "shoulder", passes=2)
    stroke_through(s, (163.8, 157.0), (153.0, 150.0), (149.0, 149.6), 0.52, "shoulder", passes=2)
    lw_line(s, 145.0, 149.8, 144.4, 163.8, "struct", "neck", passes=2)

    # A couple of SHORT surprise marks near her head only.
    lw_line(s, 133.0, 118.0, 133.0, 122.0, "detail", "surprise")
    s.stroke(131.8, 116.2, 132.5, 117.0, pressure_start=0.5, pressure_end=0.46, speed_mm_s=40, tag="surprise")

    balloon_lettered(s, 139.0, 111.0, 17.5, 9.0, ["EVERY SINGLE", "DAY...!!"], font_h=2.6)

    # P4: the Merry sails on, cabin present, Luffy standing ON the ram's head.
    tone(s, 13, 173, 163, 200, pitch=1.15, p=0.18, skip=0.76, seed=626, tag="p4-sky")
    tone(s, 40, 182, 52, 189, pitch=0.8, p=0.26, skip=0.25, seed=627, tag="p4-cloud")
    tone(s, 116, 178, 138, 184, pitch=0.8, p=0.26, skip=0.25, seed=628, tag="p4-cloud")
    for (x, y, w) in ((36, 190, 3.2), (44, 185.5, 2.6), (124, 188, 3.0)):
        stroke_through(s, (x, y), (x + w / 2, y - 1.6), (x + w, y), 0.28, "gull")
        stroke_through(s, (x, y + 0.5), (x + w / 2, y + 1.2), (x + w, y + 0.5), 0.28, "gull")
    lw_line(s, 14, 204, 162, 204, "bg", "horizon")
    tone(s, 14, 205, 162, 212, pitch=1.0, p=0.22, skip=0.66, seed=629, tag="sea-far")
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
    tone(s, 83, 189, 94, 205, pitch=0.85, p=0.24, skip=0.45, seed=630, tag="sail-tone")
    lw_line(s, 88.5, 184, 91.5, 185.0, "detail", "flag")
    lw_line(s, 91.5, 185.0, 88.5, 186.0, "detail", "flag")
    stroke_through(s, (106, 214.5), (122, 219.0), (138, 224.5), 0.30, "wake", passes=2)
    stroke_through(s, (106, 217.5), (124, 223.0), (140, 229.0), 0.26, "wake", passes=2)
    for _ in range(16):
        x = rng.uniform(58, 70)
        y = rng.uniform(213.5, 219.5)
        s.stroke(x, y, x + 0.5, y + 0.3, pressure_start=0.3, pressure_end=0.26, speed_mm_s=80, tag="foam")

    # Luffy ON the ram's head: feet at the head's TOP edge (contact), drawn
    # after it so his soles break its outline. Weight where it belongs.
    figure(s, 66.5, feet_y=205.2, h=6.6, tag="luffy-p4", hat=True)
    stroke_through(s, (67.3, 202.6), (68.8, 200.2), (70.6, 198.4), 0.36, "luffy-arm")

    balloon_lettered(s, 44.0, 186.0, 16.5, 8.5, ["SET SAIL!"], font_h=2.6)

    s.save()
    print("pass4 view:", s.view("pass4", px_per_cell=1))


def final() -> None:
    s = get_session()
    print("loupe:", s.view("loupe", region_mm=[12.0, 12.0, 164.0, 236.0], px_per_cell=1))
    s.note(
        "artist_statement",
        "Page four, drawn after studying actual One Piece pages. The busts "
        "crop at the chest the way emotional panels do, the crew stand behind "
        "a bulwark that was drawn over their legs, and the captain stands in "
        "contact with the ram's head — weight shared, outline broken. Hair is "
        "a black mass, eyes are small and bold with solid pupils and one "
        "white spec each, and the balloons were whitened fully before the "
        "subdabbed letterpress spoke. Designs © Oda/Shueisha; the practice is "
        "ours.",
    )
    print("export:", s.export_artwork("manga_page_04"))
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
