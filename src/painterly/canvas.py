"""Canvas state: a surface instance plus the fields the work changes."""

from __future__ import annotations

import numpy as np

from .types import Paper


class Canvas:
    """Surface + deposit + damage, all in millimeters.

    The deposit field is ink film thickness (mm) per cell. Damage accumulates
    from erasing/scraping (v0: unwritten). All fields are deterministic given
    the paper seed and the stroke log.
    """

    def __init__(self, paper: Paper, cell_mm: float = 0.2) -> None:
        self.paper = paper
        self.cell_mm = cell_mm
        self.nx = int(paper.size_mm[0] / cell_mm)
        self.ny = int(paper.size_mm[1] / cell_mm)
        self.deposit = np.zeros((self.ny, self.nx), dtype=np.float32)
        self.damage = np.zeros((self.ny, self.nx), dtype=np.float32)
        self.guides = np.zeros((3, self.ny, self.nx), dtype=np.float32)  # R, G, B
        self.pigment = np.zeros((3, self.ny, self.nx), dtype=np.float32)  # ink pigment shares
        self.stain = np.zeros((self.ny, self.nx), dtype=np.float32)  # peak ink ever
        self._build_tooth()

    def _build_tooth(self) -> None:
        ys, xs = np.mgrid[0 : self.ny, 0 : self.nx]
        x = (xs + 0.5) * self.cell_mm
        y = (ys + 0.5) * self.cell_mm
        tooth = np.zeros((self.ny, self.nx), dtype=np.float32)
        for amp, fx, fy, phase in self.paper.components:
            tooth += amp * np.sin(fx * x + fy * y + phase)
        self.tooth = tooth

    def tooth_norm_at(self, x_mm: float, y_mm: float) -> float:
        """Local tooth as 0..1 against the paper grade's peak amplitude."""
        amp = self.paper.spec.tooth_amplitude_mm
        if amp <= 0:
            return 0.5
        return (self.paper.height_mm(x_mm, y_mm) / amp + 1.0) / 2.0

    def stamp_disk(self, cx_mm: float, cy_mm: float, radius_mm: float, film_mm: float, pigment_channel: int | None = None) -> None:
        """Add film thickness inside a disk (tip radii are sub-cell to a few cells).
        Pigmented tools also record which color channel the film belongs to."""
        if radius_mm <= 0 or film_mm <= 0:
            return
        r_cells = radius_mm / self.cell_mm
        cx, cy = cx_mm / self.cell_mm, cy_mm / self.cell_mm
        x0, x1 = max(0, int(cx - r_cells - 1)), min(self.nx, int(cx + r_cells + 2))
        y0, y1 = max(0, int(cy - r_cells - 1)), min(self.ny, int(cy + r_cells + 2))
        if x0 >= x1 or y0 >= y1:
            return
        dx = np.arange(x0, x1) + 0.5 - cx
        dy = np.arange(y0, y1) + 0.5 - cy
        mask = dy[:, None] ** 2 + dx[None, :] ** 2 <= r_cells * r_cells
        self.deposit[y0:y1, x0:x1] += film_mm * mask
        if pigment_channel is not None:
            self.pigment[pigment_channel, y0:y1, x0:x1] += film_mm * mask
        self.stain[y0:y1, x0:x1] = np.maximum(self.stain[y0:y1, x0:x1], self.deposit[y0:y1, x0:x1])

    def stamp_guide(self, cx_mm: float, cy_mm: float, radius_mm: float, channel: int, intensity: float) -> None:
        """Lay down colored construction medium (pencil) in one guide channel."""
        if radius_mm <= 0 or intensity <= 0:
            return
        r_cells = radius_mm / self.cell_mm
        cx, cy = cx_mm / self.cell_mm, cy_mm / self.cell_mm
        x0, x1 = max(0, int(cx - r_cells - 1)), min(self.nx, int(cx + r_cells + 2))
        y0, y1 = max(0, int(cy - r_cells - 1)), min(self.ny, int(cy + r_cells + 2))
        if x0 >= x1 or y0 >= y1:
            return
        dx = np.arange(x0, x1) + 0.5 - cx
        dy = np.arange(y0, y1) + 0.5 - cy
        mask = dy[:, None] ** 2 + dx[None, :] ** 2 <= r_cells * r_cells
        ch = self.guides[channel]
        ch[y0:y1, x0:x1][mask] = np.minimum(1.0, ch[y0:y1, x0:x1][mask] + intensity)

    def whiteout_disk(self, cx_mm: float, cy_mm: float, radius_mm: float, strength: float) -> float:
        """Gouache white-out: opaque correction. Fully lifts deposit, guides,
        and pigment beneath — no ghost floor, no abrasion (the white protects
        the paper). The named finishing step of real manga production.
        Returns volume removed."""
        if radius_mm <= 0 or strength <= 0:
            return 0.0
        r_cells = radius_mm / self.cell_mm
        cx, cy = cx_mm / self.cell_mm, cy_mm / self.cell_mm
        x0, x1 = max(0, int(cx - r_cells - 1)), min(self.nx, int(cx + r_cells + 2))
        y0, y1 = max(0, int(cy - r_cells - 1)), min(self.ny, int(cy + r_cells + 2))
        if x0 >= x1 or y0 >= y1:
            return 0.0
        dx = np.arange(x0, x1) + 0.5 - cx
        dy = np.arange(y0, y1) + 0.5 - cy
        mask = dy[:, None] ** 2 + dx[None, :] ** 2 <= r_cells * r_cells
        d = self.deposit[y0:y1, x0:x1]
        before = float(d[mask].sum())
        d[mask] *= 1.0 - strength
        for c in range(3):
            self.guides[c, y0:y1, x0:x1][mask] *= 1.0 - strength
            self.pigment[c, y0:y1, x0:x1][mask] *= 1.0 - strength
        return before - float(d[mask].sum())

    def erase_disk(self, cx_mm: float, cy_mm: float, radius_mm: float, strength: float) -> float:
        """A soft eraser pass: lift ink toward a permanent ghost of its peak,
        gray and smear it, abrade the paper. Returns volume removed."""
        if radius_mm <= 0 or strength <= 0:
            return 0.0
        GHOST = 0.18  # dye stays in the fibers: ink lightens, never vanishes
        r_cells = radius_mm / self.cell_mm
        cx, cy = cx_mm / self.cell_mm, cy_mm / self.cell_mm
        x0, x1 = max(0, int(cx - r_cells - 1)), min(self.nx, int(cx + r_cells + 2))
        y0, y1 = max(0, int(cy - r_cells - 1)), min(self.ny, int(cy + r_cells + 2))
        if x0 >= x1 or y0 >= y1:
            return 0.0
        dx = np.arange(x0, x1) + 0.5 - cx
        dy = np.arange(y0, y1) + 0.5 - cy
        mask = dy[:, None] ** 2 + dx[None, :] ** 2 <= r_cells * r_cells

        d = self.deposit[y0:y1, x0:x1]
        before = float(d[mask].sum())
        d[mask] *= 1.0 - strength

        # pencil construction lifts more cleanly than ink dye, but not fully
        for c in range(3):
            g = self.guides[c, y0:y1, x0:x1]
            g[mask] *= 1.0 - strength * 0.9
            self.pigment[c, y0:y1, x0:x1][mask] *= 1.0 - strength

        self.damage[y0:y1, x0:x1][mask] = np.minimum(1.0, self.damage[y0:y1, x0:x1][mask] + strength * 0.3)

        # gentle smear: one soft 3x3 blur where the eraser traveled
        yc0, yc1 = max(1, y0), min(self.ny - 1, y1)
        xc0, xc1 = max(1, x0), min(self.nx - 1, x1)
        if yc1 > yc0 and xc1 > xc0:
            sub = self.deposit[yc0 - 1 : yc1 + 1, xc0 - 1 : xc1 + 1]
            blurred = (
                sub
                + np.roll(sub, 1, 0)
                + np.roll(sub, -1, 0)
                + np.roll(sub, 1, 1)
                + np.roll(sub, -1, 1)
            ) / 5.0
            core = blurred[1:-1, 1:-1]
            self.deposit[yc0:yc1, xc0:xc1] = 0.6 * self.deposit[yc0:yc1, xc0:xc1] + 0.4 * core
            self.stain[yc0:yc1, xc0:xc1] = np.maximum(
                self.stain[yc0:yc1, xc0:xc1], self.deposit[yc0:yc1, xc0:xc1]
            )

        # ghost floor LAST — smear spreads the dye but cannot erase it
        d[mask] = np.maximum(d[mask], self.stain[y0:y1, x0:x1][mask] * GHOST)
        after = float(d[mask].sum())
        return before - after
