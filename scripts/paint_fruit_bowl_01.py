"""Fruit bowl — pointillist study. Bananas, two pears, two apples, whole and
halved oranges, red and green grapes, leaves, in a footed silver bowl.

Technique: thousands of small dots of pure pigment (red, blue, yellow inks),
optically mixed by the page — the render composites pigment shares per cell,
so violet is red dots beside blue dots, orange is yellow over red, green is
yellow and blue. Shadows go blue before they go black. Highlights are the
un-dotted paper. Every stem is seated in its fruit's crown — nothing floats.

Usage: python scripts/paint_fruit_bowl_01.py {1|2|3|4|final}
"""

import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from painterly.session import Session  # noqa: E402

DIR = ROOT / "sessions" / "fruit_bowl_01"
LIGHT = (-0.707, -0.707)

COUNTS = {}


def get_session() -> Session:
    if (DIR / "state.json").exists():
        return Session(DIR, restore=True)
    return Session(
        DIR,
        paper_id="hot_press",
        seed=91,
        artist_id="unnamed-artist-0",
        title="Fruit bowl, in dots",
    )


def dot(s, x, y, tool):
    if s.held != tool:
        s.select_tool(tool)
    fb = s.stroke(x, y, x + 0.45, y + 0.28, pressure_start=0.58, pressure_end=0.5, speed_mm_s=90, tag="dot")
    return fb


def pick(rng, palette):
    r = rng.random()
    acc = 0.0
    for tool, w in palette:
        acc += w
        if r <= acc:
            return tool
    return palette[-1][0]


def zone_dots(s, cx, cy, rx, ry, n, palette, tag, seed, shade_dark=None):
    """Scatter dots in an ellipse, denser toward the light, shadow side
    pushed toward dark tools, highlight side left as paper."""
    rng = random.Random(seed)
    made = skipped = dark = 0
    while made < n:
        ang = rng.uniform(0, 2 * math.pi)
        rr = math.sqrt(rng.random())
        x = cx + rx * rr * math.cos(ang)
        y = cy + ry * rr * math.sin(ang)
        d = math.hypot(x - cx, y - cy) + 1e-6
        cos_t = ((x - cx) * LIGHT[0] + (y - cy) * LIGHT[1]) / d
        L = 0.5 + 0.38 * cos_t
        if rng.random() > L * 1.35:
            skipped += 1
            continue
        if L < 0.30 and shade_dark and rng.random() < 0.35:
            tool = shade_dark
            dark += 1
        else:
            tool = pick(rng, palette)
        dot(s, x, y, tool)
        made += 1
    COUNTS[tag] = (made, skipped, dark)


def pass5() -> None:
    """Definition pass: the bowl needs edge density, not clouds — dense dots
    ALONG the rim curve, sides darker, center light. Bananas re-laid at real
    density. Fruit bases extended to sit in the rim, not float above it."""
    import random

    s = get_session()
    rng = random.Random(5595)
    CX, RIM_Y, RX, RY = 60.0, 80.0, 36.0, 5.0

    # Bowl rim: dots hugging the ellipse curve, front edge heaviest.
    for t in range(0, 360, 2):
        ang = math.radians(t)
        x = CX + RX * math.cos(ang)
        y = RIM_Y + RY * math.sin(ang)
        edge = 1.0 - abs(math.cos(ang)) * 0.55  # sides and front denser
        n = int(2 + edge * 3)
        for k in range(n):
            dot(s, x + rng.uniform(-0.8, 0.8), y + rng.uniform(-0.9, 0.9),
                "fineliner_03" if rng.random() < 0.62 else "fineliner_blue")
            COUNTS["bowl-rim-def"] = (COUNTS.get("bowl-rim-def", (0, 0, 0))[0] + 1, 0, 0)

    # Bowl body: dense side crescents, light belly — silver turns dark at edges.
    for side in (-1, 1):
        for t in range(0, 170, 3):
            ang = math.radians(t)
            x = CX + side * RX * abs(math.cos(ang)) * (0.82 + 0.18 * (t / 170.0))
            y = 84 + 30.0 * (t / 170.0)
            for k in range(3):
                dot(s, x + rng.uniform(-1.0, 1.0), y + rng.uniform(-0.8, 0.8),
                    "fineliner_blue" if rng.random() < 0.55 else "fineliner_03")
                COUNTS["bowl-sides"] = (COUNTS.get("bowl-sides", (0, 0, 0))[0] + 1, 0, 0)

    # Foot: edge rings so the pedestal and base read as turned forms.
    for cx, cy, rx, ry, n in ((60.0, 118.0, 13.0, 5.0, 150), (60.0, 133.5, 20.0, 4.0, 180)):
        for t in range(0, 360, 360 // n):
            ang = math.radians(t)
            x = cx + rx * math.cos(ang)
            y = cy + ry * math.sin(ang)
            dot(s, x + rng.uniform(-0.7, 0.7), y + rng.uniform(-0.7, 0.7),
                "fineliner_03" if rng.random() < 0.6 else "fineliner_blue")
            COUNTS["foot-def"] = (COUNTS.get("foot-def", (0, 0, 0))[0] + 1, 0, 0)

    # Bananas: re-laid dense along the same arcs.
    for spine in (
        [(34.0, 77.0), (42.0, 71.5), (52.0, 69.8), (62.0, 71.6), (68.0, 75.4)],
        [(36.5, 81.5), (46.0, 76.0), (56.0, 74.6), (65.5, 76.8), (70.5, 80.6)],
    ):
        for i in range(len(spine) - 1):
            segs = 16
            for j in range(segs):
                t = j / segs
                x = spine[i][0] + (spine[i + 1][0] - spine[i][0]) * t
                y = spine[i][1] + (spine[i + 1][1] - spine[i][1]) * t
                taper = 0.55 + 0.45 * math.sin(math.pi * ((i + t) / (len(spine) - 1)))
                half = 4.6 * 0.5 * taper
                perp = (-(spine[i + 1][1] - spine[i][1]), spine[i + 1][0] - spine[i][0])
                pl = math.hypot(*perp) + 1e-6
                pyy = rng.uniform(-half, half)
                x += perp[0] / pl * pyy
                y += perp[1] / pl * pyy
                edge = abs(pyy) / max(0.1, half)
                r = rng.random()
                if edge > 0.72 and r < 0.30:
                    tool = pick(rng, [("fineliner_blue", 0.4), ("fineliner_03", 0.3), ("fineliner_red", 0.3)])
                elif (i + t) < 0.18 or (i + t) > 0.85:
                    tool = pick(rng, [("fineliner_blue", 0.35), ("fineliner_yellow", 0.35), ("fineliner_03", 0.30)])
                else:
                    tool = pick(rng, [("fineliner_yellow", 0.72), ("fineliner_red", 0.12), ("fineliner_03", 0.16)])
                dot(s, x, y, tool)
                c0 = COUNTS.get("bananas", (0, 0, 0))
                COUNTS["bananas"] = (c0[0] + 1, c0[1], c0[2])

    # Fruit bases sink into the rim: extra dots along each mass's lower arc.
    for cx, cy, rx, ry, n in (
        (38, 70, 11, 5, 90), (49, 75, 9.5, 5.5, 90), (63, 73, 10, 5.5, 90),
        (81, 70.5, 10, 5, 85), (91, 75, 8.5, 4.5, 70), (96, 78.5, 6.5, 4, 60),
    ):
        for _ in range(n):
            ang = rng.uniform(0.15 * math.pi, 0.85 * math.pi)
            x = cx + rx * math.cos(ang)
            y = cy + ry * math.sin(ang)
            tool = pick(rng, [("fineliner_03", 0.42), ("fineliner_blue", 0.30),
                              ("fineliner_red", 0.14), ("fineliner_yellow", 0.14)])
            dot(s, x + rng.uniform(-0.5, 0.5), y + rng.uniform(-0.5, 0.5), tool)
            COUNTS["fruit-seat"] = (COUNTS.get("fruit-seat", (0, 0, 0))[0] + 1, 0, 0)

    s.save()
    for tag, (m, sk, dk) in sorted(COUNTS.items()):
        print(f"  [{tag:14s}] dots={m}")
    print("pass5 view:", s.view("pass5"))


def pass1() -> None:
    s = get_session()
    s.note(
        "reflection",
        "Sheet 1's stems floated; here every stem mark is seated — its base "
        "inside the fruit's crown. Composition from the bowl reference: "
        "bananas front-left, two pears, two apples, a whole orange left, a "
        "halved orange crowned in the middle, red grapes in two clusters, "
        "green grapes right, leaves behind. No plums — they rarely make the "
        "bowl. Noted for a future still life.",
    )
    s.note(
        "material_choice",
        "Pointillism, in three inks. Small pure-color dots — red, blue, "
        "yellow — optically mixed where they land close: violet is red with "
        "blue, orange is yellow over red, green is yellow and blue. Shadows "
        "go blue before black. Highlights are the paper, undotted. The "
        "renderer composites pigment shares per cell, so the mixing is real "
        "and inspectable — the style translates.",
    )
    s.select_tool("fineliner_03")

    # Red construction: bowl geometry, mound envelope, ground.
    for cy, ry in ((80.0, 5.0), (100.0, 16.0)):
        s.stroke(24, cy, 96, cy, curvature=0.0, pressure_start=0.15, pressure_end=0.15,
                 speed_mm_s=70, tag="guide-red", layer="guide", guide_color="red", guide_opacity=0.3)
        s.stroke(24, cy - ry, 96, cy - ry, curvature=0.0, pressure_start=0.15, pressure_end=0.15,
                 speed_mm_s=70, tag="guide-red", layer="guide", guide_color="red", guide_opacity=0.3)
    s.stroke(40, 130, 80, 130, pressure_start=0.15, pressure_end=0.15, speed_mm_s=70,
             tag="guide-red", layer="guide", guide_color="red", guide_opacity=0.3)
    s.stroke(30, 132, 90, 132, pressure_start=0.15, pressure_end=0.15, speed_mm_s=70,
             tag="guide-red", layer="guide", guide_color="red", guide_opacity=0.3)

    s.save()
    print("pass1 view:", s.view("pass1"))


def pass2() -> None:
    s = get_session()

    # Leaves behind, upper left.
    zone_dots(s, 32, 44, 9, 5, 200,
              [("fineliner_blue", 0.42), ("fineliner_yellow", 0.40), ("fineliner_03", 0.18)],
              "leaves", seed=1101)

    # Whole orange, left.
    zone_dots(s, 38, 64, 11, 9, 380,
              [("fineliner_yellow", 0.52), ("fineliner_red", 0.36), ("fineliner_03", 0.12)],
              "orange", seed=1202, shade_dark="fineliner_blue")

    # Halved orange, crowned center: ring, face, pale core, segment rays.
    zone_dots(s, 55, 52, 11, 8, 300,
              [("fineliner_red", 0.50), ("fineliner_yellow", 0.36), ("fineliner_03", 0.14)],
              "half-ring", seed=1303, shade_dark="fineliner_blue")
    zone_dots(s, 55, 52, 8.2, 5.9, 230,
              [("fineliner_yellow", 0.72), ("fineliner_red", 0.16), ("fineliner_03", 0.12)],
              "half-face", seed=1404)

    # Red grape clusters.
    zone_dots(s, 33, 57, 8, 7, 360,
              [("fineliner_red", 0.52), ("fineliner_blue", 0.30), ("fineliner_03", 0.18)],
              "grapes-red-L", seed=1505, shade_dark="fineliner_03")
    zone_dots(s, 70, 48, 7, 5.5, 280,
              [("fineliner_red", 0.52), ("fineliner_blue", 0.30), ("fineliner_03", 0.18)],
              "grapes-red-R", seed=1606, shade_dark="fineliner_03")

    # Pears: yellow-green bodies; the right one takes a red blush.
    zone_dots(s, 49, 68, 9.5, 10, 380,
              [("fineliner_yellow", 0.58), ("fineliner_blue", 0.18), ("fineliner_03", 0.24)],
              "pear-1", seed=1707, shade_dark="fineliner_03")
    rng = random.Random(1717)
    made = 0
    while made < 300:
        ang = rng.uniform(0, 2 * math.pi)
        rr = math.sqrt(rng.random())
        x = 63 + 10 * rr * math.cos(ang)
        y = 66 + 10 * rr * math.sin(ang)
        if x > 66 and rng.random() < 0.55:
            tool = pick(rng, [("fineliner_red", 0.45), ("fineliner_yellow", 0.35), ("fineliner_03", 0.20)])
        else:
            tool = pick(rng, [("fineliner_yellow", 0.60), ("fineliner_blue", 0.18), ("fineliner_03", 0.22)])
        dot(s, x, y, tool)
        made += 1
    COUNTS["pear-2"] = (300, 0, 0)

    # Apples, right: red bodies, yellow mixed toward the light, white highs.
    zone_dots(s, 81, 64, 10, 8.5, 400,
              [("fineliner_red", 0.68), ("fineliner_yellow", 0.14), ("fineliner_03", 0.18)],
              "apple-1", seed=1808, shade_dark="fineliner_blue")
    zone_dots(s, 91, 70, 8.5, 7.5, 320,
              [("fineliner_red", 0.64), ("fineliner_yellow", 0.16), ("fineliner_03", 0.20)],
              "apple-2", seed=1909, shade_dark="fineliner_blue")

    # Green grapes, right flank: yellow and blue arguing into green.
    zone_dots(s, 96, 74, 6.5, 6.5, 300,
              [("fineliner_yellow", 0.55), ("fineliner_blue", 0.28), ("fineliner_03", 0.17)],
              "grapes-green", seed=2010, shade_dark="fineliner_03")

    # Stems, seated: stubs born inside crowns, never floating.
    s.select_tool("fineliner_03")
    for (x0, y0, x1, y1) in (
        (52.2, 57.0, 51.0, 52.6),   # pear 1 stem, seated at its crown
        (64.2, 56.6, 65.6, 52.2),   # pear 2
        (80.6, 56.4, 80.0, 52.4),   # apple 1
        (91.8, 63.2, 92.4, 60.0),   # apple 2
        (55.0, 47.6, 54.4, 45.2),   # halved orange leaf-stub
    ):
        line_stub(s, x0, y0, x1, y1)

    s.save()
    for tag, (m, sk, dk) in sorted(COUNTS.items()):
        print(f"  [{tag:12s}] dots={m} skipped_for_light={sk} dark_shade={dk}")
    print("pass2 view:", s.view("pass2"))


def line_stub(s, x0, y0, x1, y1):
    s.stroke(x0, y0, x1, y1, pressure_start=0.5, pressure_end=0.4, speed_mm_s=50, tag="stem-seated")


def pass3() -> None:
    s = get_session()
    rng = random.Random(3393)

    # Bananas: two arcs across the front, yellow with green tips, dark ends.
    for spine, w0 in (
        ([(34.0, 77.0), (42.0, 71.5), (52.0, 69.8), (62.0, 71.6), (68.0, 75.4)], 4.6),
        ([(36.5, 81.5), (46.0, 76.0), (56.0, 74.6), (65.5, 76.8), (70.5, 80.6)], 4.2),
    ):
        n = len(spine)
        for i in range(n - 1):
            segs = 9
            for j in range(segs):
                t = j / segs
                x = spine[i][0] + (spine[i + 1][0] - spine[i][0]) * t
                y = spine[i][1] + (spine[i + 1][1] - spine[i][1]) * t
                taper = 0.55 + 0.45 * math.sin(math.pi * ((i + t) / (n - 1)))
                half = w0 * 0.5 * taper
                perp = (-(spine[i + 1][1] - spine[i][1]), spine[i + 1][0] - spine[i][0])
                pl = math.hypot(*perp) + 1e-6
                pyy = rng.uniform(-half, half)
                x += perp[0] / pl * pyy
                y += perp[1] / pl * pyy
                edge = abs(pyy) / max(0.1, half)
                r = rng.random()
                if edge > 0.72 and r < 0.30:
                    tool = pick(rng, [("fineliner_blue", 0.4), ("fineliner_03", 0.3), ("fineliner_red", 0.3)])
                elif (i + t) < 0.18 or (i + t) > 0.85:
                    tool = pick(rng, [("fineliner_blue", 0.35), ("fineliner_yellow", 0.35), ("fineliner_03", 0.30)])
                else:
                    tool = pick(rng, [("fineliner_yellow", 0.72), ("fineliner_red", 0.12), ("fineliner_03", 0.16)])
                dot(s, x, y, tool)
                COUNTS["bananas"] = COUNTS.get("bananas", (0, 0, 0))
                COUNTS["bananas"] = (COUNTS["bananas"][0] + 1, COUNTS["bananas"][1], COUNTS["bananas"][2])

    # Banana stem ends, seated dark nubs.
    s.select_tool("fineliner_03")
    for (x, y) in ((34.2, 77.6), (68.6, 75.2), (36.8, 82.0), (70.6, 80.4)):
        s.stroke(x, y, x + 0.9, y + 0.4, pressure_start=0.55, pressure_end=0.45, speed_mm_s=55, tag="banana-end")

    # The bowl: silver = sparse dark dots on white, blue-gray in the shade.
    zone_dots(s, 60, 82, 35, 4.5, 260,
              [("fineliner_03", 0.62), ("fineliner_blue", 0.38)], "bowl-rim", seed=2102)
    zone_dots(s, 60, 101, 33, 14, 520,
              [("fineliner_03", 0.50), ("fineliner_blue", 0.50)], "bowl-body", seed=2203,
              shade_dark="fineliner_03")
    # pedestal and foot
    zone_dots(s, 60, 124, 14, 7, 260,
              [("fineliner_03", 0.55), ("fineliner_blue", 0.45)], "bowl-foot", seed=2304)
    zone_dots(s, 60, 134, 20, 4.5, 220,
              [("fineliner_03", 0.58), ("fineliner_blue", 0.42)], "bowl-base", seed=2405)

    s.save()
    for tag, (m, sk, dk) in sorted(COUNTS.items()):
        print(f"  [{tag:12s}] dots={m} skipped={sk} dark={dk}")
    print("pass3 view:", s.view("pass3"))


def pass4() -> None:
    s = get_session()
    rng = random.Random(4494)

    # Cast shadow, right of the bowl's foot: blue before black.
    zone_dots(s, 72, 139, 22, 5, 340,
              [("fineliner_blue", 0.55), ("fineliner_03", 0.45)], "cast-shadow", seed=2506)
    # table: sparse cool dots
    zone_dots(s, 60, 148, 44, 6, 180,
              [("fineliner_blue", 0.45), ("fineliner_yellow", 0.25), ("fineliner_03", 0.30)],
              "table", seed=2607)

    # Form accents: darker dot rows on the shadow sides of the big fruits.
    s.select_tool("fineliner_03")
    for cx, cy, rx, ry, n in (
        (41.5, 66, 9, 7.5, 60),   # orange right
        (83.5, 66, 8, 7, 60),     # apple 1 right
        (66.5, 68, 8, 8, 55),     # pear 2 right
        (51.5, 70.5, 7.5, 8, 45), # pear 1 right
    ):
        for _ in range(n):
            ang = rng.uniform(-0.9, 0.9)
            rr = 0.62 + 0.3 * rng.random()
            x = cx + rx * rr * math.sin(ang) * 1.0
            y = cy + ry * rr * math.cos(ang)
            s.stroke(x, y, x + 0.4, y + 0.25, pressure_start=0.5, pressure_end=0.42, speed_mm_s=85, tag="accent")

    s.save()
    for tag, (m, sk, dk) in sorted(COUNTS.items()):
        print(f"  [{tag:12s}] dots={m} skipped={sk} dark={dk}")
    print("pass4 view:", s.view("pass4"))


def final() -> None:
    s = get_session()
    print("loupe:", s.view("loupe", region_mm=[20.0, 40.0, 104.0, 152.0], px_per_cell=2))
    s.note(
        "artist_statement",
        "A fruit bowl in dots. Bananas, two pears, two apples, an orange and "
        "a halved orange, red grapes in two clusters, green grapes, leaves — "
        "and no plums, which rarely make the bowl; they are owed one. The "
        "style is the oldest trick in optics: small marks of pure color, let "
        "the eye do the mixing. Red beside blue is violet; yellow over red is "
        "orange; yellow and blue argue into green. The shadows go blue before "
        "they go black, the highlights are paper, and every stem is seated in "
        "its fruit. Rendered from the log, dot by dot.",
    )
    print("export:", s.export_artwork("fruit_bowl"))
    kinds = {"dots": 0}
    tools = {}
    for line_txt in (DIR / "log.jsonl").read_text().splitlines():
        import json

        rec = json.loads(line_txt)
        if rec["type"] == "stroke":
            kinds["strokes"] = kinds.get("strokes", 0) + 1
            if rec["tag"] == "dot":
                kinds["dots"] += 1
            tools[rec["tool"]] = tools.get(rec["tool"], 0) + 1
        elif rec["type"] == "view":
            kinds["views"] = kinds.get("views", 0) + 1
        elif rec["type"] == "note":
            kinds["notes"] = kinds.get("notes", 0) + 1
    print(f"session log: {kinds}")
    print(f"tools by strokes: {tools}")


if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else "1"
    {"1": pass1, "2": pass2, "3": pass3, "4": pass4, "5": pass5, "final": final}[stage]()
