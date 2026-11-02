"""Shared panel-drawing primitives — the tested versions of what page scripts
kept re-implementing (and re-bugging).

The balloon here CLOSES correctly: the arc list loops back to its first point
and the tail is drawn as two converging ticks from the rim toward the
speaker — never as a chord through the interior. Hair is strands and clumps
that taper along a flow direction, never stipple. Gulls are two arches side
by side — not raindrops.
"""

from __future__ import annotations

import math
import random

from .fonts import stamp_text, text_width_mm
from .stroke import curvature_through


def stroke_through(s, a, mid, b, p, tag, speed=60.0, taper=0.88, passes=1):
    """The workhorse: a stroke planned through three points."""
    k = curvature_through(a, mid, b)
    for _ in range(passes):
        s.stroke(*a, *b, curvature=k, pressure_start=p, pressure_end=p * taper,
                 speed_mm_s=speed, tag=tag)


def balloon(s, cx, cy, rx, ry, lines, font_h=2.6, tail=None,
            tool="fineliner_03", subdabs=2, whiteout_strength=0.97, tag="balloon"):
    """Speech balloon: full whiteout interior, correctly-closed outline,
    optional tail pointing at `tail=(tx, ty)`, auto-fit stamped script."""
    from painterly.stroke import execute_whiteout  # noqa: F401  (engine check)

    max_chars = max(len(l) for l in lines)
    fit_h = min(font_h,
                (ry * 2 * 0.60) / (len(lines) * 1.5),
                (rx * 2 * 0.66) / (max_chars * 6 / 7))
    width = min(4.6, ry * 0.75)
    yy = cy - ry
    while yy <= cy + ry:
        s.whiteout(cx - rx * 0.9, yy, cx + rx * 0.9, yy + 0.3,
                   width_mm=width, strength=whiteout_strength, tag="whiteout")
        yy += width * 0.4

    n = 12
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        pts.append((cx + rx * math.cos(a), cy + ry * math.sin(a)))

    def arc(a, b, p=0.5):
        m = (cx + 1.06 * ((a[0] + b[0]) / 2 - cx), cy + 1.06 * ((a[1] + b[1]) / 2 - cy))
        k = curvature_through(a, m, b)
        for _ in range(2):
            s.stroke(a[0], a[1], b[0], b[1], curvature=k,
                     pressure_start=p, pressure_end=p * 0.92, speed_mm_s=70, tag=tag)

    for i in range(n):
        arc(pts[i], pts[(i + 1) % n])  # CLOSED — never a chord across the pan

    if tail is not None:
        dx, dy = tail[0] - cx, tail[1] - cy
        d = math.hypot(dx, dy) or 1.0
        ux, uy = dx / d, dy / d
        rim = (cx + ux * rx * 0.94, cy + uy * ry * 0.94)
        tip = (cx + ux * (rx + 2.4), cy + uy * (ry + 2.4))
        px, py = -uy, ux
        lw = 0.45
        s.stroke(rim[0] - px * 0.55, rim[1] - py * 0.55, tip[0], tip[1],
                 pressure_start=lw, pressure_end=lw * 0.8, speed_mm_s=60, tag=tag)
        s.stroke(rim[0] + px * 0.55, rim[1] + py * 0.55, tip[0], tip[1],
                 pressure_start=lw, pressure_end=lw * 0.8, speed_mm_s=60, tag=tag)

    lh = fit_h * 1.5
    y0 = cy - (len(lines) - 1) * lh / 2 - fit_h / 2
    for i, ln in enumerate(lines):
        w = text_width_mm(ln, fit_h)
        stamp_text(s, cx - w / 2, y0 + i * lh, ln, height_mm=fit_h, tool=tool, subdabs=subdabs)


def gull(s, x, y, w, p=0.28, tag="gull"):
    """Two arches SIDE BY SIDE — a gull in flight, not a raindrop."""
    stroke_through(s, (x, y), (x + w * 0.25, y - 1.35), (x + w * 0.5, y), p, tag)
    stroke_through(s, (x + w * 0.5, y), (x + w * 0.75, y - 1.35), (x + w, y), p, tag)


def hair_strands(s, roots, flow, length, n, p=0.42, seed=0, tag="hair",
                 taper=0.5, spread=0.35):
    """Hair as strands: n curved strokes per root, following `flow`, each
    tapering to a fine end, jittered so clumps read organic. One direction,
    one flow — hair drawn a strand at a time, as it grows."""
    rng = random.Random(seed)
    fx, fy = flow
    fl = math.hypot(fx, fy) or 1.0
    fx, fy = fx / fl, fy / fl
    px, py = -fy, fx
    base_a = math.atan2(fy, fx)
    for (rx_, ry_) in roots:
        for i in range(n):
            j = rng.uniform(-1, 1)
            a = base_a + j * spread
            ln = length * rng.uniform(0.75, 1.15)
            sx = rx_ + rng.uniform(-0.15, 0.15)
            sy = ry_ + rng.uniform(-0.15, 0.15)
            ex = sx + math.cos(a) * ln + fx * ln * 0.25
            ey = sy + math.sin(a) * ln + fy * ln * 0.25
            mx = (sx + ex) / 2 + math.cos(a + math.pi / 2) * j * length * 0.18
            my = (sy + ey) / 2 + math.sin(a + math.pi / 2) * j * length * 0.18
            stroke_through(s, (sx, sy), (mx, my), (ex, ey), p * rng.uniform(0.85, 1.05),
                           tag, speed=60, taper=taper)


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
