"""Body study — a mannequin sheet drawn over projected 3D scaffolds.

The method: build the figure in world meters (Richer 7.5-head canon —
see RESEARCH.md), project it through the camera, draw the projection as a
red construction, then ink the body ON TOP of its own scaffold. The
hand "imagines" by tracing geometry that cannot lie about proportions.

Cells: head front / head 3/4 / head profile / standing figure /
clothed figure / hand. Labels stamped in letterpress.

Usage: python scripts/study_body_01.py {1|2|3|4|final}
"""

import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from painterly.fonts import stamp_text  # noqa: E402
from painterly.panels import tone  # noqa: E402
from painterly.session import Session  # noqa: E402
from painterly.stroke import curvature_through  # noqa: E402
from painterly.world import Camera, Mannequin  # noqa: E402

DIR = ROOT / "sessions" / "study_body_02"

LW = {"outline": 0.50, "struct": 0.36, "detail": 0.22, "bg": 0.15}


def get_session() -> Session:
    if (DIR / "state.json").exists():
        return Session(DIR, restore=True)
    return Session(
        DIR,
        paper_id="hot_press",
        seed=161,
        size_mm=(176.0, 250.0),
        cell_mm=0.2,
        artist_id="unnamed-artist-0",
        title="Body study — mannequin construction sheets",
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


def guide_line(s, x0, y0, x1, y1, tag="guide"):
    s.stroke(x0, y0, x1, y1, pressure_start=0.15, pressure_end=0.15, speed_mm_s=70,
             tag=tag, layer="guide", guide_color="red", guide_opacity=0.35)


def guide_circle(s, cx, cy, r, tag="guide", points=10):
    pts = []
    for i in range(points + 1):
        a = 2 * math.pi * i / points
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    for i in range(points):
        a, b = pts[i], pts[i + 1]
        m = (cx + 1.08 * ((a[0] + b[0]) / 2 - cx), cy + 1.08 * ((a[1] + b[1]) / 2 - cy))
        s.stroke(a[0], a[1], b[0], b[1], curvature=curvature_through(a, m, b),
                 pressure_start=0.15, pressure_end=0.15, speed_mm_s=70,
                 tag=tag, layer="guide", guide_color="red", guide_opacity=0.35)


def ink_circle(s, cx, cy, r, p, tag, points=10, passes=1):
    pts = []
    for i in range(points + 1):
        a = 2 * math.pi * i / points
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    for i in range(points):
        a, b = pts[i], pts[i + 1]
        m = (cx + 1.05 * ((a[0] + b[0]) / 2 - cx), cy + 1.05 * ((a[1] + b[1]) / 2 - cy))
        stroke_through(s, a, m, b, p, tag, passes=passes)


def quad_ink(s, quad, level, tag, close=False):
    n = len(quad)
    pairs = [(0, 1), (3, 2)] if not close else [(0, 1), (1, 2), (2, 3), (3, 0)]
    for i0, i1 in pairs:
        a, b = quad[i0], quad[i1]
        lw_line(s, a[0], a[1], b[0], b[1], level, tag)


def pass1() -> None:
    s = get_session()
    s.note(
        "material_choice",
        "Body study over projected scaffolds. The mannequin is built in world "
        "meters on the Richer 7.5-head canon: head 0.23 m, shoulders 0.46 m "
        "(two head-widths), eye line at mid-head, torso 4 units with the legs. "
        "The camera projects the figure; red construction is the projection; "
        "the ink goes on top of geometry that cannot lie about proportion.",
    )
    s.select_tool("fineliner_03")
    for (x0, y0, x1, y1) in ((12, 20, 86, 96), (90, 20, 164, 96),
                             (12, 104, 86, 164), (90, 104, 164, 164),
                             (12, 172, 86, 236), (90, 172, 164, 236)):
        lw_line(s, x0, y0, x1, y0, "detail", "cell", passes=1)
        lw_line(s, x1, y0, x1, y1, "detail", "cell", passes=1)
        lw_line(s, x1, y1, x0, y1, "detail", "cell", passes=1)
        lw_line(s, x0, y1, x0, y0, "detail", "cell", passes=1)

    for (x, y, label) in ((14, 17, "HEAD FRONT"), (92, 17, "HEAD 3/4"),
                          (14, 101, "HEAD PROFILE"), (92, 101, "FIGURE 7.5"),
                          (14, 169, "CLOTHED"), (92, 169, "HAND")):
        stamp_text(s, x, y, label, height_mm=2.0)

    s.save()
    print("pass1 view:", s.view("pass1", px_per_cell=1))


CELLS = {
    "front":   dict(vp=(49.0, 62.0), focal=55.0, yaw=0.0, z=0.52),
    "three4":  dict(vp=(127.0, 62.0), focal=55.0, yaw=35.0, z=0.52),
    "profile": dict(vp=(49.0, 138.0), focal=55.0, yaw=72.0, z=0.52),
    "figure":  dict(vp=(133.0, 148.0), focal=48.0, yaw=0.0, z=2.6),
    "clothed": dict(vp=(49.0, 206.0), focal=48.0, yaw=0.0, z=2.6),
}


def head_setup(yaw, vp, focal=55.0, z=1.15):
    cam = Camera(vp_mm=vp, eye_height_m=1.6, focal_mm=focal)
    man = Mannequin(height_m=1.7, yaw_deg=yaw).placed(z)
    hc = cam.project(*man.head_c)
    hr = cam.point_radius(man.head_c, man.head_r)
    return cam, man, hc, hr


def P(cam, p):
    return cam.project(*p)


def head_construction(s, cam, man):
    hc = P(cam, man.head_c)
    hr = cam.point_radius(man.head_c, man.head_r)
    guide_circle(s, hc[0], hc[1], hr)
    el, er = P(cam, man.eye_l), P(cam, man.eye_r)
    no, mo = P(cam, man.nose), P(cam, man.mouth)
    eal, ear = P(cam, man.ear_l), P(cam, man.ear_r)
    chin = P(cam, man.chin)
    guide_line(s, hc[0], hc[1] - hr, hc[0], hc[1] + hr * 1.05)          # axis
    guide_line(s, min(el[0], er[0]) - hr * 0.5, (el[1] + er[1]) / 2,
               max(el[0], er[0]) + hr * 0.5, (el[1] + er[1]) / 2)       # eye line
    guide_line(s, el[0], el[1] - hr * 0.28, el[0], el[1] + hr * 0.28)   # eye crosses
    guide_line(s, er[0], er[1] - hr * 0.28, er[0], er[1] + hr * 0.28)
    guide_line(s, no[0] - 1.2, no[1], no[0] + 1.2, no[1])               # nose tick
    guide_line(s, mo[0] - 1.4, mo[1], mo[0] + 1.4, mo[1])               # mouth tick
    guide_line(s, eal[0] - 1.0, eal[1], eal[0] + 1.0, eal[1])           # ear ticks
    guide_line(s, ear[0] - 1.0, ear[1], ear[0] + 1.0, ear[1])
    guide_line(s, chin[0] - 1.4, chin[1], chin[0] + 1.4, chin[1])       # chin tick
    return hc, hr, el, er, no, mo, eal, ear, chin


def pass2() -> None:
    """Red construction in every cell."""
    s = get_session()
    s.select_tool("fineliner_03")

    for name in ("front", "three4", "profile"):
        cam, man, hc, hr = head_setup(**CELLS[name])
        head_construction(s, cam, man)

    for name in ("figure", "clothed"):
        cfg = CELLS[name]
        cam = Camera(vp_mm=cfg["vp"], eye_height_m=1.6, focal_mm=cfg["focal"])
        man = Mannequin(height_m=1.7, yaw_deg=cfg["yaw"]).placed(cfg["z"])
        hc = P(cam, man.head_c)
        hr = cam.point_radius(man.head_c, man.head_r)
        guide_circle(s, hc[0], hc[1], hr)
        for (a, b, ra, rb) in man.limbs:
            q = cam.limb_quad(a, b, ra, rb)
            for i0, i1 in ((0, 1), (1, 2), (2, 3), (3, 0)):
                guide_line(s, q[i0][0], q[i0][1], q[i1][0], q[i1][1])
        t = [P(cam, p) for p in man.torso]
        for i0, i1 in ((0, 3), (1, 2), (3, 5), (2, 4), (4, 5), (0, 1)):
            guide_line(s, t[i0][0], t[i0][1], t[i1][0], t[i1][1])
        gl = P(cam, (0.0, 0.0, man.head_c[2]))
        lw_line(s, gl[0] - 16, gl[1], gl[0] + 16, gl[1], "bg", "ground")

    # Hand cell: palm + four fingers + thumb, built in world values at z 0.85.
    cam = Camera(vp_mm=(128.0, 208.0), eye_height_m=1.6, focal_mm=55.0)
    z = 0.85
    palm = cam.limb_quad((0.0, 1.35, z), (0.0, 1.44, z), 0.045, 0.038)
    quad_ink(s, palm, "bg", "hand-guide")
    for k, fx in enumerate((-0.054, -0.018, 0.018, 0.054)):
        fq = cam.limb_quad((fx, 1.45, z), (fx + fx * 0.12, 1.44 + 0.055 - k * 0.007, z),
                           0.011, 0.009)
        quad_ink(s, fq, "bg", "hand-guide")
    tq = cam.limb_quad((-0.062, 1.36, z + 0.01), (-0.095, 1.41, z + 0.02), 0.014, 0.011)
    quad_ink(s, tq, "bg", "hand-guide")
    lw_line(s, 96, 208, 160, 208, "bg", "ground-hand")

    s.save()
    print("pass2 view:", s.view("pass2", px_per_cell=1))


def pass3() -> None:
    """Ink the three heads: skull, jaw, features at their anchors."""
    s = get_session()
    s.select_tool("fineliner_03")

    for name, yaw in (("front", 0.0), ("three4", 35.0), ("profile", 72.0)):
        cfg = CELLS[name]
        cam, man, hc, hr = head_setup(**cfg)
        el, er = P(cam, man.eye_l), P(cam, man.eye_r)
        no, mo = P(cam, man.nose), P(cam, man.mouth)
        eal, ear = P(cam, man.ear_l), P(cam, man.ear_r)
        chin = P(cam, man.chin)

        if name == "profile":
            # The big profile contour: crown -> brow -> nose -> lips -> chin.
            crown = (hc[0] + hr * 0.15, hc[1] - hr * 0.98)
            brow = (hc[0] + hr * 0.88, hc[1] - hr * 0.42)
            prof = [crown, brow, (no[0] + hr * 0.16, no[1] - hr * 0.12),
                    (no[0] + hr * 0.22, no[1] + hr * 0.10),
                    (mo[0] + hr * 0.16, mo[1] + hr * 0.06),
                    (chin[0] + hr * 0.16, chin[1] + hr * 0.02)]
            for i in range(len(prof) - 1):
                a, b = prof[i], prof[i + 1]
                stroke_through(s, a, ((a[0] + b[0]) / 2 + hr * 0.10, (a[1] + b[1]) / 2),
                               b, 0.46, "profile", passes=2)
            # jaw back to the ear, then the skull's back curve.
            stroke_through(s, prof[-1], (hc[0] + hr * 0.30, chin[1] - hr * 0.30),
                           (ear[0] + 1.0, ear[1] + hr * 0.30), 0.46, "jaw", passes=2)
            ink_circle(s, hc[0], hc[1], hr, 0.44, "skull", points=10, passes=1)
            # near eye: small, bold; ear: a C.
            stroke_through(s, (er[0] - 1.6, er[1] - 0.7), (er[0] + 0.6, er[1] - 1.1),
                           (er[0] + 1.6, er[1] - 0.2), 0.42, "eye-lid", passes=2)
            s.stroke(er[0] + 0.2, er[1] + 0.6, er[0] + 0.8, er[1] + 0.9,
                     pressure_start=0.6, pressure_end=0.55, speed_mm_s=40, tag="eye")
            stroke_through(s, (ear[0] + 0.6, ear[1] - 1.6), (ear[0] + 1.6, ear[1]),
                           (ear[0] + 0.4, ear[1] + 1.6), 0.30, "ear-c")
            lw_line(s, no[0] + hr * 0.2, no[1] + hr * 0.22, no[0] - hr * 0.05, mo[1] - 0.6,
                    "detail", "lips")
        else:
            # skull + jaw (both sides to the chin)
            ink_circle(s, hc[0], hc[1], hr, 0.44, "skull", points=10, passes=1)
            jaw = hr * 0.82
            stroke_through(s, (el[0] - hr * 0.34, el[1] + hr * 0.10),
                           (hc[0] - jaw, (el[1] + chin[1]) / 2 + hr * 0.10),
                           (chin[0] - hr * 0.10, chin[1]), 0.44, "jaw", passes=2)
            stroke_through(s, (er[0] + hr * 0.34, er[1] + hr * 0.10),
                           (hc[0] + jaw, (er[1] + chin[1]) / 2 + hr * 0.10),
                           (chin[0] + hr * 0.10, chin[1]), 0.44, "jaw", passes=2)
            eye_w = hr * (0.78 if name == "front" else 0.52)
            for ex, fl in ((el[0], 1.0), (er[0], -1.0)) if name == "front" else ((er[0], -1.0),):
                ey = el[1] if name == "front" else er[1]
                stroke_through(s, (ex - eye_w / 2, ey + hr * 0.06),
                               (ex + fl * eye_w * 0.10, ey - hr * 0.14),
                               (ex + eye_w / 2, ey + hr * 0.04), 0.46, "eye-lid", passes=2)
                lw_line(s, ex - eye_w / 2 + 0.6, ey + hr * 0.30, ex + eye_w / 2 - 0.6,
                        ey + hr * 0.30, "detail", "eye-lower")
                dot = min(1.0, eye_w * 0.30)
                s.stroke(ex + fl * eye_w * 0.08 - dot / 2, ey + hr * 0.14,
                         ex + fl * eye_w * 0.08 + dot / 2, ey + hr * 0.14 + dot * 0.6,
                         pressure_start=0.62, pressure_end=0.56, speed_mm_s=40, tag="pupil")
                lw_line(s, ex - eye_w / 2, ey - hr * 0.42, ex + eye_w / 2, ey - hr * 0.36,
                        "detail", "brow")
            # nose wedge + mouth at anchors
            stroke_through(s, (no[0] - hr * 0.14, no[1] - hr * 0.28),
                           (no[0] + hr * 0.10, no[1] + hr * 0.06),
                           (no[0] + hr * 0.18, no[1] + hr * 0.16), 0.36, "nose")
            lw_line(s, mo[0] - hr * 0.42, mo[1], mo[0] + hr * 0.42, mo[1], "detail", "mouth")
            lw_line(s, mo[0] - hr * 0.30, mo[1] + hr * 0.14, mo[0] + hr * 0.30, mo[1] + hr * 0.14,
                    "bg", "mouth-shadow")
            # ears
            for ea in ((eal, 1.0), (ear, -1.0)) if name == "front" else ((ear, -1.0),):
                stroke_through(s, (ea[0][0] - 0.9, ea[0][1] - 1.5),
                               (ea[0][0] + 1.3 * ea[1], ea[0][1]),
                               (ea[0][0] - 0.7, ea[0][1] + 1.7), 0.30, "ear-c")
        # neck for every head
        nl, nr = hc[0] - hr * 0.32, hc[0] + hr * 0.32
        lw_line(s, nl, hc[1] + hr * 0.86, nl - 0.6, hc[1] + hr * 1.55, "struct", "neck")
        lw_line(s, nr, hc[1] + hr * 0.86, nr + 0.6, hc[1] + hr * 1.55, "struct", "neck")

    s.save()
    print("pass3 view:", s.view("pass3", px_per_cell=1))


def pass4() -> None:
    """Figure inked over its mannequin; clothed variant; hand inked."""
    s = get_session()
    s.select_tool("fineliner_03")

    def ink_figure(cell, clothed=False):
        cfg = CELLS[cell]
        cam = Camera(vp_mm=cfg["vp"], eye_height_m=1.6, focal_mm=cfg["focal"])
        man = Mannequin(height_m=1.7, yaw_deg=cfg["yaw"]).placed(cfg["z"])
        hc = P(cam, man.head_c)
        hr = cam.point_radius(man.head_c, man.head_r)
        off = 1.1 if clothed else 0.0
        # head + neck
        ink_circle(s, hc[0], hc[1], hr + (0.5 if clothed else 0.0), 0.46, "head",
                   points=10, passes=1)
        nl, nr = hc[0] - hr * 0.32, hc[0] + hr * 0.32
        lw_line(s, nl, hc[1] + hr * 0.86, nl - 0.5, hc[1] + hr * 1.7, "struct", "neck")
        lw_line(s, nr, hc[1] + hr * 0.86, nr + 0.5, hc[1] + hr * 1.7, "struct", "neck")
        # torso sides from the projected torso polygon, inflated by `off`
        t = [P(cam, p) for p in man.torso]
        lw_line(s, t[0][0] - off, t[0][1], t[3][0] - off, t[3][1], "outline", "torso-L", passes=2)
        lw_line(s, t[1][0] + off, t[1][1], t[2][0] + off, t[2][1], "outline", "torso-R", passes=2)
        lw_line(s, t[3][0] - off, t[3][1], t[5][0] - off * 0.6, t[5][1], "struct", "hip-L")
        lw_line(s, t[2][0] + off, t[2][1], t[4][0] + off * 0.6, t[4][1], "struct", "hip-R")
        # limbs: trace each quad's two side edges
        for (a, b, ra, rb) in man.limbs[1:]:
            q = cam.limb_quad(a, b, ra + (0.012 if clothed else 0.0),
                              rb + (0.012 if clothed else 0.0))
            lw_line(s, q[0][0], q[0][1], q[1][0], q[1][1], "struct", "limb")
            lw_line(s, q[3][0], q[3][1], q[2][0], q[2][1], "struct", "limb")
        # hands: small dabs at the wrists' end; feet: ground strokes
        for hand in (man.hand_l, man.hand_r):
            hp = P(cam, hand)
            ink_circle(s, hp[0], hp[1], 1.4, 0.38, "hand", points=8)
        ground = P(cam, (0.0, 0.0, man.head_c[2]))[1]
        for an in (man.ankle_l, man.ankle_r):
            ap = P(cam, an)
            lw_line(s, ap[0] - 1.6, ground - 0.4, ap[0] + 1.6, ground - 0.4,
                    "struct", "foot", passes=2)
        if clothed:
            # collar, hem, sleeve hems, cuff marks, fold ticks at the joints
            lw_line(s, nl - 1.6, hc[1] + hr * 1.62, nl + 1.6, hc[1] + hr * 1.62,
                    "detail", "collar")
            lw_line(s, t[0][0] - off - 0.4, hc[1] + hr * 2.05, t[1][0] + off + 0.4,
                    hc[1] + hr * 2.05, "detail", "shirt-hem")
            for sx in (t[0], t[1]):
                lw_line(s, sx[0] - off - 1.2, sx[1] + 4.0, sx[0] - off + 1.2, sx[1] + 4.0,
                        "detail", "sleeve-hem")
            for jy in (man.chest[1], man.waist[1]):
                jp = P(cam, (0.0, jy, 0.1))
                lw_line(s, jp[0] - 2.2, jp[1] + 1.2, jp[0] + 2.4, jp[1] + 1.6,
                        "bg", "fold")
            for kn in (man.knee_l, man.knee_r):
                kp = P(cam, kn)
                lw_line(s, kp[0] - 1.4, kp[1] + 1.0, kp[0] + 1.6, kp[1] + 1.3,
                        "bg", "fold")

    ink_figure("figure", clothed=False)
    ink_figure("clothed", clothed=True)

    # HAND: palm contour, fingers, thumb — traced over the red quads.
    cam = Camera(vp_mm=(128.0, 208.0), eye_height_m=1.6, focal_mm=55.0)
    z = 0.85
    palm = cam.limb_quad((0.0, 1.35, z), (0.0, 1.44, z), 0.045, 0.038)
    quad_ink(s, palm, "struct", "palm", close=True)
    for k, fx in enumerate((-0.054, -0.018, 0.018, 0.054)):
        fq = cam.limb_quad((fx, 1.45, z), (fx + fx * 0.12, 1.44 + 0.055 - k * 0.007, z),
                           0.011, 0.009)
        quad_ink(s, fq, "struct", "finger", close=True)
    tq = cam.limb_quad((-0.062, 1.36, z + 0.01), (-0.095, 1.41, z + 0.02), 0.014, 0.011)
    quad_ink(s, tq, "struct", "thumb", close=True)
    # knuckle ticks
    lw_line(s, P(cam, (-0.06, 1.451, z))[0], P(cam, (-0.06, 1.451, z))[1],
            P(cam, (0.06, 1.451, z))[0], P(cam, (0.06, 1.451, z))[1], "bg", "knuckles")

    s.save()
    print("pass4 view:", s.view("pass4", px_per_cell=1))


def final() -> None:
    s = get_session()
    print("loupe:", s.view("loupe", region_mm=[10.0, 14.0, 166.0, 240.0], px_per_cell=1))
    s.note(
        "artist_statement",
        "A body study built the way the ateliers teach: construct the figure "
        "in real proportions, project it, trace it, then earn the details on "
        "top. The mannequin is the Richer canon in world meters — 7.5 heads, "
        "shoulders two head-widths, eye line at mid-head — and every red line "
        "is the camera's honest projection of that canon. Three heads turn; "
        "a figure stands; the same figure wears a shirt that rests on its "
        "shoulders and folds at its joints; a hand is a palm, four fingers, "
        "a thumb. The imagination the craft needs is externalized here as "
        "geometry the hand can trust.",
    )
    print("export:", s.export_artwork("body_study"))
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
            k = rec.get("note_kind", "note")
            kinds[k] = kinds.get(k, 0) + 1
    print("session log:", kinds)


if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else "1"
    {"1": pass1, "2": pass2, "3": pass3, "4": pass4, "final": final}[stage]()
