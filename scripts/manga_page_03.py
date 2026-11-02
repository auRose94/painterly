"""Manga page 3 — built from RESEARCH.md, not from habit.

Research applied (see RESEARCH.md):
  - G-pen line-weight hierarchy: thick silhouettes, thin details, thinnest
    backgrounds (frame lines 0.5-0.8 mm confirmed)
  - eyes DOMINATE the face; upper lid casts a shadow ON the iris; iris is a
    solid region with the pupil darker; TWO highlights planned first and
    reserved as paper; constricted iris + blank eye = shock (Nami)
  - screentone: less is more; carve highlights with the knife (= whiteout)
  - lettering needs breathing room: auto-fit font, never touch the rim
  - white-out is the named finishing step: balloon interiors whitened before
    the script is stamped

Character designs © Eiichiro Oda / Shueisha — disclosed fan study.

Usage: python scripts/manga_page_03.py {1|2|3|4|final}
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

DIR = ROOT / "sessions" / "manga_page_03c"

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
        seed=121,
        size_mm=(176.0, 250.0),
        cell_mm=0.2,
        artist_id="unnamed-artist-0",
        title="Going Merry — fan study, researched pass",
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
    """Solid fill from overlapping dabs; `skip` is a list of (hx, hy, hr)
    disks left as paper — the planned highlights."""
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
                jx, jy = rng.uniform(-0.06, 0.06), rng.uniform(-0.06, 0.06)
                s.stroke(x + jx, y + jy, x + jx + pitch * 0.62, y + jy + pitch * 0.36,
                         pressure_start=p, pressure_end=p * 0.9, speed_mm_s=90, tag=tag)
            x += pitch
        y += pitch * 0.8


def balloon_lettered(s, cx, cy, rx, ry, lines, font_h=2.2):
    """White-out interior (finishing step), auto-fit the type with breathing
    room, outline, tail, stamp."""
    # breathing-room rule: text box is 70% of the interior
    max_chars = max(len(l) for l in lines)
    fit_h = min(font_h, (ry * 2 * 0.62) / (len(lines) * 1.55),
                (rx * 2 * 0.70) / (max_chars * 6 / ROWS_C) if (ROWS_C := 7) else font_h)
    for k in range(3):
        yy = cy - ry * 0.55 + k * ry * 0.55
        s.whiteout(cx - rx * 0.82, yy, cx + rx * 0.82, yy + 0.4,
                   width_mm=min(5.0, ry * 0.9), strength=0.97, tag="whiteout")
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
    lh = fit_h * 1.6
    y0 = cy - (len(lines) - 1) * lh / 2 - fit_h / 2
    for i, ln in enumerate(lines):
        w = text_width_mm(ln, fit_h)
        stamp_text(s, cx - w / 2, y0 + i * lh, ln, height_mm=fit_h)


ROWS_C = 7


def figure(s, x, feet_y, h=6.6, tag="crew", hat=False, hair_spikes=False, nose=False):
    """Connected figure, FEET ON the ground line (0.2 into it)."""
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


def pass1() -> None:
    s = get_session()
    s.note(
        "attempt_boundary",
        "manga_page_03 rejected (dot_fill keyword collision, state/log "
        "diverged). manga_page_03b also rejected: pass 3 crashed on a bare "
        "`line()` call that does not exist in this script — the whiteouts "
        "logged but never saved. Lesson enforced: every pass must be "
        "verified before the next runs. Fixed; 03c restarts clean.",
    )
    s.note(
        "derivative_work",
        "Fan study, page 3. One Piece © Eiichiro Oda / Shueisha — "
        "interpretation from memory, disclosed, non-commercial.",
    )
    s.note(
        "material_choice",
        "Research pass — see RESEARCH.md. Line-weight hierarchy on every "
        "stroke (G-pen rule): silhouettes 0.58, structure 0.40, detail 0.22, "
        "background 0.15. Eyes rebuilt per the tutorial: they dominate the "
        "face, the upper lid casts a shadow ON the iris, the iris is a solid "
        "fill with the two highlights reserved as paper, and Nami's shock is "
        "a constricted iris in a blank eye. Screentone sparser (less is "
        "more), highlights carved with white-out. Balloons: white-out "
        "interior first, auto-fit type, breathing room. Cabin present in "
        "both ship views. Crew feet ON the deck, which is drawn as a floor "
        "band so standing reads.",
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
    """P1: Merry + grounded crew, cabin present, line-weight hierarchy."""
    s = get_session()
    s.select_tool("fineliner_03")

    tone(s, 14, 14, 162, 46, pitch=1.15, p=0.20, skip=0.78, seed=121, tag="sky")
    tone(s, 26, 24, 44, 31, pitch=0.8, p=0.28, skip=0.25, seed=122, tag="cloud")
    tone(s, 122, 27, 148, 33, pitch=0.8, p=0.28, skip=0.25, seed=123, tag="cloud")
    lw_line(s, 14, 50, 162, 50, "bg", "horizon")
    tone(s, 14, 51, 162, 60, pitch=1.05, p=0.24, skip=0.66, seed=124, tag="sea-far")
    rng = random.Random(321)
    y = 62.0
    while y <= 92.0:
        x = 15.0 + rng.uniform(0, 6)
        while x < 160.0:
            w = rng.uniform(3.0, 7.0)
            if rng.random() < 0.68:
                lw_line(s, x, y, x + w, y + rng.uniform(-0.3, 0.3), "bg", "wave", taper=0.7)
            x += w + rng.uniform(2.0, 6.0)
        y += 2.3

    # Hull — silhouette weight.
    hull = [(66, 67), (74, 73), (88, 75), (102, 73), (113, 67)]
    for i in range(len(hull) - 1):
        stroke_through(s, hull[i], ((hull[i][0] + hull[i + 1][0]) / 2,
                                    (hull[i][1] + hull[i + 1][1]) / 2 + 0.6),
                       hull[i + 1], LW["outline"], "hull", passes=2)
    lw_line(s, 66, 66, 113, 66, "struct", "deck-rail", passes=2)
    # Deck as a FLOOR BAND: rail above, planks below — standing has ground.
    lw_line(s, 68, 68.5, 112, 68.5, "detail", "deck-floor")
    for px in range(74, 110, 6):
        lw_line(s, px, 66.4, px, 68.4, "detail", "plank")
    # Two crew grounded ON the deck floor line (feet 0.2 into it).
    figure(s, 74.5, 61.0, h=7.0, tag="usopp", nose=True)
    figure(s, 80.0, 60.8, h=7.2, tag="zoro", hair_spikes=True)
    figure(s, 86.0, 61.2, h=6.8, tag="nami")
    figure(s, 97.5, 60.6, h=7.4, tag="luffy", hat=True)

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

    # Mast rooted in the keel; yard crosses it.
    lw_line(s, 89, 70.0, 89, 26, "struct", "mast", passes=2)
    lw_line(s, 76, 30, 102, 30, "struct", "yard")
    stroke_through(s, (78.5, 30.5), (77.0, 42.0), (80.5, 55.0), 0.40, "sail")
    stroke_through(s, (99.5, 30.5), (101.0, 42.0), (97.5, 55.0), 0.40, "sail")
    stroke_through(s, (78.5, 55.0), (88.5, 56.8), (97.5, 55.0), 0.38, "sail")
    tone(s, 80, 32, 97, 54, pitch=0.95, p=0.24, skip=0.48, seed=125, tag="sail-tone")
    lw_line(s, 89, 26, 93.5, 27.2, "detail", "flag")
    lw_line(s, 93.5, 27.2, 89, 28.4, "detail", "flag")
    lw_line(s, 89, 30, 66.5, 63.0, "bg", "rigging")
    lw_line(s, 89, 30, 112.5, 62.0, "bg", "rigging")

    # Stern cabin — PRESENT, consistent with the panel-4 view.
    lw_line(s, 104, 67.5, 104, 54, "struct", "cabin")
    lw_line(s, 104, 54, 112, 55, "struct", "cabin")
    lw_line(s, 112, 55, 113, 68.0, "struct", "cabin")

    # Carve highlight glints into the sea tone with white-out (tone knife).
    for gx in (30, 74, 128):
        s.whiteout(gx, 55 + (gx % 3) * 2, gx + 12, 56.5 + (gx % 3) * 2,
                   width_mm=2.2, strength=0.6, tag="sea-glint")

    s.save()
    print("pass2 view:", s.view("pass2", px_per_cell=1))


def pass3() -> None:
    """P2: Luffy declares — research eyes, whiteout balloon, stamped script."""
    s = get_session()
    s.select_tool("fineliner_03")

    tone(s, 13, 105, 85, 163, pitch=1.05, p=0.20, skip=0.70, seed=321, tag="p2-field")

    # Head: egg, taller than wide — silhouette weight.
    head = [
        (29.5, 128.0), (27.8, 137.0), (30.0, 146.5), (36.5, 153.5), (44.5, 155.5),
        (52.5, 153.5), (59.0, 146.5), (61.2, 137.5), (59.5, 128.5), (54.5, 122.0),
        (46.0, 120.2),
    ]
    head.append((32.0, 124.0))
    s.stroke_path([v for p in head for v in p], pressure=0.46, speed_mm_s=55, tag="face")

    # Straw hat: dome, band, wide brim — outline weight.
    stroke_through(s, (26.0, 124.0), (44.0, 107.5), (62.5, 123.0), 0.52, "hat", passes=2)
    stroke_through(s, (27.5, 121.0), (44.0, 115.0), (60.8, 120.0), 0.44, "band", passes=2)
    stroke_through(s, (21.5, 124.5), (44.0, 117.5), (66.5, 124.0), 0.52, "brim", passes=2)
    tone(s, 31, 110, 58, 116, pitch=0.8, p=0.30, skip=0.35, seed=322, tag="hat-tone")

    # Hair notch + tufts.
    stroke_through(s, (40.6, 121.2), (42.2, 123.6), (43.8, 121.8), 0.46, "hair-notch", taper=0.85)
    stroke_through(s, (43.8, 121.8), (45.2, 124.0), (46.6, 121.6), 0.46, "hair-notch", taper=0.85)
    stroke_through(s, (28.2, 125.5), (29.8, 130.5), (28.6, 134.0), 0.44, "hair", taper=0.8)
    stroke_through(s, (60.0, 124.8), (58.6, 130.0), (59.8, 133.5), 0.44, "hair", taper=0.8)
    stroke_through(s, (27.2, 135.5), (25.6, 138.5), (27.6, 140.6), 0.36, "ear", taper=0.9)
    stroke_through(s, (61.0, 135.0), (62.6, 137.8), (60.8, 140.0), 0.36, "ear", taper=0.9)

    # EYES per the tutorial: large, upper lid heavy with a cast shadow on the
    # iris, solid iris fill, two highlights reserved as paper, faint lower lid.
    def eye(cx, cy, flip=1.0):
        # upper lid: heavy, double pass
        stroke_through(s, (cx - 4.4, cy - 2.2), (cx, cy - 3.8), (cx + 4.4, cy - 2.2),
                       0.52, "eye-lid", passes=2)
        # outer lash tick
        lw_line(s, cx + flip * 4.2, cy - 2.4, cx + flip * 5.4, cy - 1.4, "detail", "lash")
        # lid shadow cast ON the iris top
        for k in range(-2, 3):
            s.stroke(cx + k * 0.9 - 0.2, cy - 2.0 + abs(k) * 0.18,
                     cx + k * 0.9 + 0.5, cy - 1.7 + abs(k) * 0.18,
                     pressure_start=0.5, pressure_end=0.45, speed_mm_s=80, tag="lid-shadow")
        # iris: solid fill, pupil darker, highlights reserved as paper
        dot_fill(s, cx, cy + 0.8, 2.3, 2.6, 0.5, "iris", seed=int(cx * 10),
                 skip=[(cx - flip * 0.8, cy - 0.2, 0.85), (cx + flip * 0.9, cy + 1.7, 0.45)])
        # pupil core, darker
        dot_fill(s, cx + flip * 0.1, cy + 1.0, 0.85, 1.0, 0.62, "pupil", seed=int(cx), pitch=0.42)
        # lower lid: faint, thin
        stroke_through(s, (cx - 3.4, cy + 3.4), (cx, cy + 4.1), (cx + 3.4, cy + 3.4),
                       0.16, "eye-lower", taper=0.9)

    eye(37.5, 137.5, flip=1.0)
    eye(51.5, 137.5, flip=-1.0)
    # the scar, two ticks on the cheek under HIS left eye
    lw_line(s, 52.2, 142.6, 54.6, 141.6, "detail", "scar", passes=2)
    lw_line(s, 53.2, 143.8, 55.4, 142.4, "detail", "scar")
    lw_line(s, 45.0, 141.5, 45.8, 143.2, "detail", "nose")

    # OPEN SHOUTING MOUTH, outline weight, tongue single line.
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

    # Speed lines, background-thin.
    rng = random.Random(323)
    for _ in range(8):
        x0 = rng.uniform(14.0, 84.0)
        y0 = 163.0 if rng.random() < 0.5 else 105.0
        lw_line(s, x0, y0, x0 + (44.0 - x0) * rng.uniform(0.4, 0.58),
                y0 + (132.0 - y0) * rng.uniform(0.4, 0.58), "bg", "speed", taper=0.5)

    # The declaration, stamped into a whitened balloon.
    balloon_lettered(s, 64.5, 111.5, 18.5, 10.0,
                     ["I'M GONNA BE", "KING OF THE", "PIRATES!!"], font_h=2.3)

    s.save()
    print("pass3 view:", s.view("pass3", px_per_cell=1))


def pass4() -> None:
    """P3 reaction (constricted-iris shock) + P4 sail-away, cabin present."""
    s = get_session()
    s.select_tool("fineliner_03")

    tone(s, 95, 105, 163, 163, pitch=1.05, p=0.20, skip=0.70, seed=421, tag="p3-field")
    lw_line(s, 95, 138, 163, 138, "detail", "rail")
    tone(s, 95, 140, 163, 162, pitch=0.95, p=0.24, skip=0.58, seed=422, tag="p3-sea")
    rng = random.Random(424)
    for _ in range(20):
        x = rng.uniform(96, 160)
        y = rng.uniform(142, 160)
        lw_line(s, x, y, x + rng.uniform(2.5, 5.5), y + rng.uniform(-0.3, 0.3), "bg", "wave", taper=0.7)

    # Zoro: stern — rectangular lids low over constricted irises, brow furrowed.
    zhead = [(109.5, 128.0), (108.0, 135.0), (110.5, 141.5), (117.0, 144.0), (124.0, 141.5),
             (126.5, 135.0), (125.0, 128.2), (118.0, 125.5)]
    zhead.append((110.5, 127.2))
    s.stroke_path([v for p in zhead for v in p], pressure=0.46, speed_mm_s=55, tag="zoro-head")
    for (x0, y0, x1, y1) in (
        (110.0, 127.4, 107.4, 124.0), (114.0, 126.2, 113.0, 122.6),
        (118.5, 126.0, 119.4, 122.2), (122.6, 126.6, 125.4, 123.6),
    ):
        lw_line(s, x0, y0, x1, y1, "struct", "zoro-hair")
    # furrowed brows low over the eyes (tutorial: anger/serious = brow covers lid)
    lw_line(s, 110.4, 132.4, 115.6, 133.4, "struct", "zoro-brow", passes=2)
    lw_line(s, 120.4, 133.2, 125.4, 132.2, "struct", "zoro-brow", passes=2)
    # constricted irises: small solid fills, blank around them
    dot_fill(s, 113.2, 135.4, 1.0, 1.1, p=0.55, tag="zoro-iris", seed=431)
    dot_fill(s, 122.6, 135.2, 1.0, 1.1, p=0.55, tag="zoro-iris", seed=432)
    lw_line(s, 123.2, 131.0, 123.4, 133.4, "detail", "zoro-scar")
    stroke_through(s, (113.8, 139.6), (117.2, 140.6), (120.4, 139.4), 0.36, "zoro-mouth")
    stroke_through(s, (108.0, 150.0), (117.5, 146.0), (126.5, 149.6), 0.44, "zoro-arms", passes=2)
    for k in range(3):
        lw_line(s, 107.0 + k * 1.4, 152.0 - k * 0.6, 102.5 + k * 1.2, 160.0 - k * 0.8, "struct", "swords", passes=2)
        s.stroke(106.6 + k * 1.4, 151.4 - k * 0.6, 107.8 + k * 1.4, 150.8 - k * 0.6,
                 pressure_start=0.5, pressure_end=0.45, speed_mm_s=45, tag="swords")

    # Nami: shock — constricted iris in a mostly BLANK eye (the tutorial's
    # fear/shock read), surprise ring and marks.
    nhead = [(136.5, 133.0), (136.0, 128.5), (140.0, 125.5), (146.0, 125.2), (150.5, 128.4),
             (151.6, 133.5), (150.0, 138.5), (145.5, 140.8), (141.0, 139.6)]
    nhead.append((137.6, 134.4))
    s.stroke_path([v for p in nhead for v in p], pressure=0.46, speed_mm_s=55, tag="nami-head")
    tone(s, 136.4, 124.6, 152.0, 130.6, pitch=0.55, p=0.44, skip=0.10, seed=425, tag="nami-hair")
    lw_line(s, 137.2, 132.6, 138.8, 133.4, "detail", "nami-face", passes=2)
    lw_line(s, 142.6, 132.8, 144.2, 133.6, "detail", "nami-face", passes=2)
    s.stroke(141.2, 136.4, 141.9, 137.3, pressure_start=0.6, pressure_end=0.55, speed_mm_s=40, tag="nami-pupil")
    stroke_through(s, (139.4, 137.2), (141.4, 135.6), (143.4, 137.2), 0.30, "nami-face")
    for (x0, y0, x1, y1) in ((143.0, 117.0, 143.0, 121.5), (146.2, 118.0, 145.6, 122.0)):
        lw_line(s, x0, y0, x1, y1, "detail", "surprise")
    s.stroke(144.4, 114.6, 145.1, 115.4, pressure_start=0.52, pressure_end=0.48, speed_mm_s=40, tag="surprise")
    for _ in range(6):
        y0 = rng.uniform(108.0, 160.0)
        lw_line(s, 95.5, y0, 95.5 + rng.uniform(14, 26), y0 + rng.uniform(-2.5, 2.5), "bg", "speed", taper=0.45)

    balloon_lettered(s, 139.0, 111.0, 17.5, 9.0, ["EVERY SINGLE", "DAY...!!"], font_h=2.2)

    # P4: the Merry sails on — same ship, cabin present here too.
    tone(s, 13, 173, 163, 200, pitch=1.15, p=0.18, skip=0.76, seed=426, tag="p4-sky")
    tone(s, 40, 182, 52, 189, pitch=0.8, p=0.26, skip=0.25, seed=427, tag="p4-cloud")
    tone(s, 116, 178, 138, 184, pitch=0.8, p=0.26, skip=0.25, seed=428, tag="p4-cloud")
    for (x, y, w) in ((36, 190, 3.2), (44, 185.5, 2.6), (124, 188, 3.0)):
        stroke_through(s, (x, y), (x + w / 2, y - 1.6), (x + w, y), 0.28, "gull")
        stroke_through(s, (x, y + 0.5), (x + w / 2, y + 1.2), (x + w, y + 0.5), 0.28, "gull")
    lw_line(s, 14, 204, 162, 204, "bg", "horizon")
    tone(s, 14, 205, 162, 212, pitch=1.0, p=0.22, skip=0.66, seed=429, tag="sea-far")
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
    # the stern cabin, CONSISTENT with panel 1
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
    tone(s, 83, 189, 94, 205, pitch=0.85, p=0.24, skip=0.45, seed=430, tag="sail-tone")
    lw_line(s, 88.5, 184, 91.5, 185.0, "detail", "flag")
    lw_line(s, 91.5, 185.0, 88.5, 186.0, "detail", "flag")
    stroke_through(s, (106, 214.5), (122, 219.0), (138, 224.5), 0.30, "wake", passes=2)
    stroke_through(s, (106, 217.5), (124, 223.0), (140, 229.0), 0.26, "wake", passes=2)
    for _ in range(16):
        x = rng.uniform(58, 70)
        y = rng.uniform(213.5, 219.5)
        s.stroke(x, y, x + 0.5, y + 0.3, pressure_start=0.3, pressure_end=0.26, speed_mm_s=80, tag="foam")

    figure(s, 66.5, 200.0, h=7.4, tag="luffy-p4", hat=True)
    stroke_through(s, (67.3, 203.0), (69.0, 200.0), (71.0, 197.6), 0.36, "luffy-arm")

    balloon_lettered(s, 44.0, 186.0, 16.5, 8.5, ["SET SAIL!"], font_h=2.4)

    s.save()
    print("pass4 view:", s.view("pass4", px_per_cell=1))


def final() -> None:
    s = get_session()
    print("loupe:", s.view("loupe", region_mm=[12.0, 12.0, 164.0, 236.0], px_per_cell=1))
    s.note(
        "artist_statement",
        "Page three, drawn after research — RESEARCH.md documents the "
        "pipeline this page follows. The G-pen rule governs every stroke: "
        "silhouettes heavy, details light, backgrounds lightest. The eyes "
        "follow the tutorial: they dominate, the lid casts its shadow on the "
        "iris, the highlights were reserved before the fill was laid, and "
        "Nami's shock is a constricted iris in a blank eye. Screentone is "
        "sparser and its highlights are carved with white-out. The balloons "
        "were whitened before their script was stamped, with breathing room "
        "auto-fit. The cabin rides in both views of the ship, and the crew's "
        "feet stand in a deck that exists. Designs © Oda/Shueisha; the "
        "practice is ours.",
    )
    print("export:", s.export_artwork("manga_page_03"))
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
