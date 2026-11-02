"""Deterministic renderer: canvas fields → image.

The same log always renders the same pixels. Film thickness maps to darkness
by a saturating curve; the tooth shades the paper; pigment shares mix the
ink color per cell — pure-color dots optically blending, pointillist-style.
"""

from __future__ import annotations

import numpy as np
from PIL import Image

from .types import PIGMENT_COLORS

FILM_SOLID_MM = 0.0025  # real ink film (2-4µm) is essentially opaque
TOOTH_SHADE = 0.05  # how strongly the paper texture shows
GUIDE_COLORS = [(196, 48, 48), (44, 150, 80), (48, 84, 190)]  # red, green, blue
MONO_INK = (24, 22, 30)


def render(canvas: Canvas, ink_color: tuple[int, int, int] = MONO_INK, px_per_cell: int = 2) -> Image.Image:
    darkness = 1.0 - np.exp(-canvas.deposit / FILM_SOLID_MM)
    tooth = canvas.tooth
    tmin, tmax = float(tooth.min()), float(tooth.max())
    tnorm = (tooth - tmin) / max(tmax - tmin, 1e-9)
    shade = 1.0 - TOOTH_SHADE * tnorm

    paper_rgb = np.array(canvas.paper.spec.base_color, dtype=np.float32)
    base = paper_rgb[None, None, :] * shade[..., None]

    # construction medium under the ink
    guides = getattr(canvas, "guides", None)
    if guides is not None:
        for c in range(3):
            v = guides[c][..., None]
            col = np.array(GUIDE_COLORS[c], dtype=np.float32)[None, None, :]
            base = base * (1.0 - v * 0.85) + col * (v * 0.85)

    # abraded paper reads slightly darker where the eraser worked
    damage = getattr(canvas, "damage", None)
    if damage is not None:
        base = base * (1.0 - 0.10 * damage[..., None])

    # ink color: pigment shares mix per cell where pigmented tools worked
    pig = getattr(canvas, "pigment", None)
    ink_rgb = np.array(ink_color, dtype=np.float32)
    if pig is not None:
        tot = pig.sum(axis=0)
        mix = np.zeros((*tot.shape, 3), dtype=np.float32)
        for c in range(3):
            col = np.array(PIGMENT_COLORS[c], dtype=np.float32)
            share = (pig[c] / np.maximum(tot, 1e-9))[..., None]
            mix += share * col
        has_color = (tot > 1e-9)[..., None]
        ink_rgb = np.where(has_color, mix, ink_rgb[None, None, :])

    out = base * (1.0 - darkness[..., None]) + ink_rgb * darkness[..., None]

    img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGB")
    if px_per_cell > 1:
        img = img.resize((canvas.nx * px_per_cell, canvas.ny * px_per_cell), Image.Resampling.LANCZOS)
    return img
