"""Per-sample stroke physics: the hand moves, the medium responds, the handle
reports what it felt.

The numeric constants below are placeholder calibrations — plausible against
real materials, to be tuned experimentally. The *structure* of the feedback
(drag rises with tooth and pressure, skips where the film is thin, pooling
where the hand slows, scratch when starved) is the contract; the numbers are
up for science.
"""

from __future__ import annotations

import math
import random

from .canvas import Canvas
from .types import NibSpec, StrokeCommand, StrokeEvent, StrokeFeedback, ToolState

SAMPLE_STEP_MM = 0.5
SEGMENT_STEP_MM = 0.2  # deposit sub-stepping, keeps thin nibs continuous
POOL_SPEED_MM_S = 15.0
PROFILE_POINTS = 64
MAX_SKIP_EVENTS = 24

# Placeholder calibration, to be tuned experimentally.
FILM_BASE_MM = 0.012  # film laid at full porosity and pressure
DRAG_TOOTH_N = 0.20
DRY_SCRATCH_N = 1.8
CATCH_LEN_MM = 0.7  # mean free path between tooth catches
BLEED_PER_ABSORBENCY_MM = 0.6
SLOW_FILM_EXP = 0.3  # film ~ speed^-0.3, clamped


def expand_stroke(
    tool: ToolState,
    start_mm: tuple[float, float],
    end_mm: tuple[float, float],
    curvature: float = 0.0,
    pressure_start: float = 0.5,
    pressure_end: float = 0.5,
    speed_mm_s: float = 60.0,
) -> StrokeCommand:
    """Expand a compact hand motion into sampled form (quadratic arc).

    `curvature` bows the stroke perpendicular to its direction, as a fraction
    of stroke length. This is the model-facing shape of a hand motion; the
    engine works on the sampled expansion.
    """
    x0, y0 = start_mm
    x1, y1 = end_mm
    length = math.hypot(x1 - x0, y1 - y0)
    n = max(2, int(length / SAMPLE_STEP_MM) + 1)

    dx, dy = x1 - x0, y1 - y0
    if length > 0:
        px, py = -dy / length, dx / length
    else:
        px, py = 0.0, 0.0
    cx = (x0 + x1) / 2 + px * curvature * length
    cy = (y0 + y1) / 2 + py * curvature * length

    xs: list[float] = []
    ys: list[float] = []
    pressure: list[float] = []
    speeds: list[float] = []
    angles: list[float] = []
    for i in range(n):
        t = i / (n - 1)
        u = 1.0 - t
        xs.append(u * u * x0 + 2 * u * t * cx + t * t * x1)
        ys.append(u * u * y0 + 2 * u * t * cy + t * t * y1)
        pressure.append(pressure_start + (pressure_end - pressure_start) * t)
        speeds.append(speed_mm_s)
        angles.append(45.0)
    return StrokeCommand(tool.tool_id, xs, ys, pressure, speeds, angles)


PATH_STEP_MM = 0.35  # sampling density for path strokes


def expand_path_stroke(
    tool: ToolState,
    points_mm: list[tuple[float, float]],
    pressure: float = 0.3,
    speed_mm_s: float = 60.0,
    ease: bool = True,
) -> StrokeCommand:
    """One continuous hand motion through waypoints (Catmull-Rom, C1 smooth).

    This is how a hand actually draws a circle: one rotational gesture, not
    four arcs spliced together. Tangents are continuous at every waypoint, so
    there are no vertices. Ends taper; speed eases in and out like a real arm.
    """
    n_pts = len(points_mm)
    if n_pts < 3:
        raise ValueError("a path stroke needs at least 3 waypoints")

    xs: list[float] = []
    ys: list[float] = []
    for i in range(n_pts - 1):
        p0x, p0y = points_mm[i]
        p1x, p1y = points_mm[i + 1]
        # tangents: backward/forward differencing, quadratic at the ends
        prx, pry = points_mm[i - 1] if i > 0 else (p0x - (p1x - p0x), p0y - (p1y - p0y))
        pnx, pny = points_mm[i + 2] if i + 2 < n_pts else (p1x + (p1x - p0x), p1y + (p1y - p0y))
        m0x, m0y = (p1x - prx) / 2, (p1y - pry) / 2
        m1x, m1y = (pnx - p0x) / 2, (pny - p0y) / 2
        # Hermite -> cubic Bezier control points
        c1x, c1y = p0x + m0x / 3, p0y + m0y / 3
        c2x, c2y = p1x - m1x / 3, p1y - m1y / 3
        seg = math.hypot(p1x - p0x, p1y - p0y)
        ns = max(2, int(seg / PATH_STEP_MM) + 1)
        for j in range(1 if xs else 0, ns + 1):
            t = j / ns
            u = 1.0 - t
            xs.append(
                u * u * u * p0x + 3 * u * u * t * c1x + 3 * u * t * t * c2x + t * t * t * p1x
            )
            ys.append(
                u * u * u * p0y + 3 * u * u * t * c1y + 3 * u * t * t * c2y + t * t * t * p1y
            )

    n = len(xs)
    taper_frac = 0.08
    pressures = []
    speeds = []
    for i in range(n):
        t = i / (n - 1)
        ramp = min(1.0, t / taper_frac, (1.0 - t) / taper_frac)
        pressures.append(pressure * (0.7 + 0.3 * ramp))
        speeds.append(speed_mm_s * (0.55 + 0.45 * math.sin(math.pi * t)) if ease else speed_mm_s)
    return StrokeCommand(tool.tool_id, xs, ys, pressures, speeds, [45.0] * n)
def curvature_through(a: tuple[float, float], mid: tuple[float, float], b: tuple[float, float]) -> float:
    """Curvature parameter so the expanded arc passes through `mid`.

    Kills the guess-and-check bow: plan the stroke by three points (ends and
    where the hand should bow to), not by a magic constant.
    """
    dx, dy = b[0] - a[0], b[1] - a[1]
    length = math.hypot(dx, dy)
    if length == 0:
        return 0.0
    px, py = -dy / length, dx / length
    mx, my = mid[0] - (a[0] + b[0]) / 2, mid[1] - (a[1] + b[1]) / 2
    return 2.0 * (mx * px + my * py) / length


def contact_radius_mm(spec: NibSpec, pressure01: float) -> float:
    """Tip radius under load: splay grows with the square of pressure."""
    return spec.tip_radius_mm * (1.0 + (spec.splay_at_max - 1.0) * pressure01**2)


def _downsample(values: list[float], points: int) -> list[float]:
    if len(values) <= points:
        return values
    chunk = len(values) / points
    out = []
    for i in range(points):
        a = int(i * chunk)
        b = max(a + 1, int((i + 1) * chunk))
        out.append(sum(values[a:b]) / (b - a))
    return out


GUIDE_GAIN = 90.0  # film-equivalent -> guide intensity


def execute_stroke(
    canvas: Canvas,
    tool: ToolState,
    cmd: StrokeCommand,
    seed: int = 0,
    layer: str = "ink",
    guide_channel: int | None = None,
    guide_opacity: float = 1.0,
) -> StrokeFeedback:
    """Run one hand motion against the canvas. Mutates deposit and tool load;
    returns what the hand felt. `layer="guide"` lays construction pencil into
    a color channel instead — same hand physics, no ink load consumed."""
    rng = random.Random(seed)
    spec = tool.spec
    absor = canvas.paper.spec.absorbency
    n = cmd.n_samples
    guide = layer == "guide"

    load_mm3 = tool.load_ml * 1000.0
    bleed_r = BLEED_PER_ABSORBENCY_MM * absor

    events: list[StrokeEvent] = []
    resistances: list[float] = []
    skip_events = 0
    starved_reported = False
    splayed_reported = False
    deposited_samples = 0
    min_x = min_y = math.inf
    max_x = max_y = -math.inf

    for i in range(n):
        x, y = cmd.xs_mm[i], cmd.ys_mm[i]
        p01 = min(1.0, max(0.0, cmd.pressure01[i]))
        speed = max(1.0, cmd.speed_mm_s[i])
        t01 = i / (n - 1)

        dist = (
            math.hypot(cmd.xs_mm[i + 1] - x, cmd.ys_mm[i + 1] - y) if i < n - 1 else SAMPLE_STEP_MM
        )

        r = contact_radius_mm(spec, p01)
        pressure_n = p01 * spec.max_pressure_n

        film = FILM_BASE_MM * spec.porosity * (0.4 + 0.6 * p01)
        film *= min(1.8, max(0.6, (60.0 / speed) ** SLOW_FILM_EXP))  # slow hand pools ink

        dry = (load_mm3 <= 0.0) and not guide
        if dry:
            film *= 0.02

        # skip: the tooth catches the tip before it can lay film
        film_ref = FILM_BASE_MM * spec.porosity
        p_catch = canvas.paper.catch_probability(p01, film / film_ref)
        p_skip = (1.0 - math.exp(-dist / CATCH_LEN_MM)) * p_catch
        skipped = (not dry) and dist > 0 and rng.random() < p_skip

        if dry:
            deposit = 0.0
            if not starved_reported:
                events.append(StrokeEvent("starved", t01, x, y, "reservoir empty: dry nib dragging"))
                starved_reported = True
        elif skipped:
            # a skip isn't a full gap: the tip still grazes the high spots
            skip_events += 1
            if skip_events <= MAX_SKIP_EVENTS:
                events.append(StrokeEvent("skip", t01, x, y, "tooth caught the tip"))
            deposit = film * 0.25
            if guide:
                canvas.stamp_guide(x, y, r, guide_channel, min(1.0, deposit * GUIDE_GAIN * guide_opacity))
            else:
                canvas.stamp_disk(x, y, r, deposit, pigment_channel=spec.pigment_channel)
                load_mm3 = max(0.0, load_mm3 - 2.0 * r * deposit * dist)
        else:
            film_s = film * 0.3 * absor * (r / (r + bleed_r)) ** 2 if bleed_r > 0 and not guide else 0.0
            # The hand glides, it doesn't hop: stamp the contact disk
            # continuously along the segment just traveled.
            if i == 0:
                targets = [(x, y)]
            else:
                px_, py_ = cmd.xs_mm[i - 1], cmd.ys_mm[i - 1]
                seg = math.hypot(x - px_, y - py_)
                steps = max(1, int(seg / SEGMENT_STEP_MM) + 1)
                targets = [
                    (px_ + (x - px_) * j / steps, py_ + (y - py_) * j / steps) for j in range(1, steps + 1)
                ]
            for sx, sy in targets:
                if guide:
                    canvas.stamp_guide(sx, sy, r, guide_channel, min(1.0, film * GUIDE_GAIN * guide_opacity))
                else:
                    canvas.stamp_disk(sx, sy, r, film, pigment_channel=spec.pigment_channel)
                    if bleed_r > 0 and film_s > 0:
                        canvas.stamp_disk(sx, sy, r + bleed_r, film_s, pigment_channel=spec.pigment_channel)
            if not guide:
                volume = (film * 2.0 * r + film_s * 2.0 * (r + bleed_r)) * dist  # band of film
                load_mm3 = max(0.0, load_mm3 - volume)
            deposited_samples += 1

            if speed < POOL_SPEED_MM_S and not guide:
                events.append(StrokeEvent("pool", t01, x, y, f"hand slowed to {speed:.0f} mm/s: ink pooling"))

        if p01 >= 0.95 and not splayed_reported:
            events.append(StrokeEvent("splay", t01, x, y, "bristles at max pressure: tip widening"))
            splayed_reported = True

        # what the handle transmits: the hand's own load plus drag from the tooth
        spring_n = pressure_n * 0.35
        tooth_drag_n = DRAG_TOOTH_N * (spec.rigidity_n_per_mm**0.5) * (0.4 + 0.6 * canvas.tooth_norm_at(x, y)) * (0.5 + 0.5 * p01)
        resistances.append(spring_n + tooth_drag_n + (DRY_SCRATCH_N if dry else 0.0))

        margin = r + bleed_r + 0.2
        min_x, max_x = min(min_x, x - margin), max(max_x, x + margin)
        min_y, max_y = min(min_y, y - margin), max(max_y, y + margin)

    tool.load_ml = load_mm3 / 1000.0

    if skip_events > MAX_SKIP_EVENTS:
        events.append(StrokeEvent("skip", 1.0, cmd.xs_mm[-1], cmd.ys_mm[-1], f"...and {skip_events - MAX_SKIP_EVENTS} more skips"))

    resistance_mean = sum(resistances) / len(resistances)
    return StrokeFeedback(
        resistance_mean_n=resistance_mean,
        resistance_peak_n=max(resistances),
        resistance_profile=_downsample(resistances, PROFILE_POINTS),
        events=events,
        bleed_mm=bleed_r,
        coverage=deposited_samples / n,
        load_after_ml=tool.load_ml,
        touched_bbox_mm=(min_x, min_y, max_x, max_y),
    )


def erase_pattern_points(
    a: tuple[float, float],
    b: tuple[float, float],
    width_mm: float,
    pattern: str = "linear",
) -> list[tuple[float, float]]:
    """Waypoints for how a hand actually erases.

    linear — one pass along the path.
    scribble — tight left-right zigzag across the band, traveling along it.
    loop — overlapping circular loops, so every micro-face of the paper is
    lifted from all directions the loop turns.
    """
    import math as _m

    dx, dy = b[0] - a[0], b[1] - a[1]
    length = _m.hypot(dx, dy)
    if length < 1e-6:
        return [a, b]
    ux, uy = dx / length, dy / length
    px, py = -uy, ux

    if pattern == "linear":
        return [a, b]

    if pattern == "scribble":
        pts = [a]
        step = max(1.2, width_mm * 0.55)
        n = max(2, int(length / step))
        for i in range(1, n):
            t = i / n
            side = width_mm * 0.38 * (1.0 if i % 2 else -1.0)
            pts.append((a[0] + dx * t + px * side, a[1] + dy * t + py * side))
        pts.append(b)
        return pts

    if pattern == "loop":
        pts = []
        r = width_mm * 0.45
        advance = r * 1.1
        n_loops = max(1, int(length / advance))
        for k in range(n_loops + 1):
            t = min(1.0, k * advance / length)
            cx, cy = a[0] + dx * t, a[1] + dy * t
            for j in range(9):
                ang = 2.0 * _m.pi * j / 8.0
                pts.append((cx + px * r * _m.cos(ang) + ux * r * _m.sin(ang) * 0.4,
                            cy + py * r * _m.cos(ang) + uy * r * _m.sin(ang) * 0.4))
        return pts

    raise ValueError(f"unknown erase pattern: {pattern}")


def execute_erase(canvas: Canvas, cmd: StrokeCommand, width_mm: float, strength: float) -> dict:
    """Drag a soft eraser along a hand path. Lifts ink toward a ghost of its
    peak, smears gently, abrades the paper. The surface remembers."""
    removed = 0.0
    for i in range(cmd.n_samples):
        x, y = cmd.xs_mm[i], cmd.ys_mm[i]
        if i == 0:
            targets = [(x, y)]
        else:
            px_, py_ = cmd.xs_mm[i - 1], cmd.ys_mm[i - 1]
            seg = math.hypot(x - px_, y - py_)
            step = max(SEGMENT_STEP_MM, width_mm * 0.5)
            steps = max(1, int(seg / step) + 1)
            targets = [(px_ + (x - px_) * j / steps, py_ + (y - py_) * j / steps) for j in range(1, steps + 1)]
        for sx, sy in targets:
            removed += canvas.erase_disk(sx, sy, width_mm / 2.0, strength)
    return {
        "removed": round(removed, 3),
        "peak_damage": round(float(canvas.damage.max()), 3),
        "width_mm": width_mm,
        "strength": strength,
    }


def execute_whiteout(canvas: Canvas, cmd: StrokeCommand, width_mm: float, strength: float) -> dict:
    """Drag opaque white-out along a hand path. Covers fully — no ghost, no
    abrasion. The finishing step: clean paper anywhere, then draw on it."""
    removed = 0.0
    for i in range(cmd.n_samples):
        x, y = cmd.xs_mm[i], cmd.ys_mm[i]
        if i == 0:
            targets = [(x, y)]
        else:
            px_, py_ = cmd.xs_mm[i - 1], cmd.ys_mm[i - 1]
            seg = math.hypot(x - px_, y - py_)
            step = max(SEGMENT_STEP_MM, width_mm * 0.5)
            steps = max(1, int(seg / step) + 1)
            targets = [(px_ + (x - px_) * j / steps, py_ + (y - py_) * j / steps) for j in range(1, steps + 1)]
        for sx, sy in targets:
            removed += canvas.whiteout_disk(sx, sy, width_mm / 2.0, strength)
    return {
        "removed": round(removed, 3),
        "width_mm": width_mm,
        "strength": strength,
    }
