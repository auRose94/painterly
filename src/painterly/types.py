"""Core physical vocabulary for Painterly.

Plain-data types shared by the physics core, the MCP tool layer, and the
practice log. Everything is deterministic and serializable so a session can be
replayed, diffed, and rendered from the log alone.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from enum import Enum

# Canvas coordinates are millimeters; the model never needs to know.


class ToolKind(Enum):
    FINELINER = "fineliner"  # rigid nylon tip, consistent width
    FELT_TIP = "felt_tip"  # porous compressible tip, soft edge
    FOUNTAIN = "fountain"  # flexing metal nib, wet ink
    BALLPOINT = "ballpoint"  # viscous oil ink, pressure-hungry


class SurfaceMaterial(Enum):
    PAPER = "paper"
    CANVAS = "canvas"
    PANEL = "panel"  # gessoed wood panel
    WOOD = "wood"
    STONE = "stone"
    WALL = "wall"  # brick/plaster, for site work


@dataclass(frozen=True)
class NibSpec:
    """The physical character of a tip — this is what the hand feels."""

    kind: ToolKind
    tip_radius_mm: float  # nominal contact radius at rest
    rigidity_n_per_mm: float  # resistance to deformation (spring of the tip)
    max_pressure_n: float  # limit before splay/damage
    splay_at_max: float  # contact radius growth at max pressure
    porosity: float  # 0..1 — how readily it holds and releases medium
    reservoir_ml: float
    strand_count: int | None = None  # fiber tips only; None = solid/porous tip
    strand_length_mm: float | None = None
    pigment_channel: int | None = None  # None = monochrome ink; else R/G/B


@dataclass(frozen=True)
class SurfaceSpec:
    """A grade of support. Tooth and absorbency are what the medium reads."""

    material: SurfaceMaterial
    name: str
    tooth_amplitude_mm: float  # peak-to-valley roughness
    tooth_wavelength_mm: float
    absorbency: float  # 0 sized/plate .. 1 raw, unsized
    base_color: tuple[int, int, int]
    grain_direction_rad: float | None = None  # weave anisotropy, if any


PAPER_CATALOG: dict[str, SurfaceSpec] = {
    "plate_bristol": SurfaceSpec(SurfaceMaterial.PAPER, "plate bristol", 0.010, 0.4, 0.15, (250, 249, 244)),
    "hot_press": SurfaceSpec(SurfaceMaterial.PAPER, "hot-press watercolor", 0.030, 0.6, 0.35, (252, 250, 243)),
    "cold_press": SurfaceSpec(SurfaceMaterial.PAPER, "cold-press watercolor", 0.090, 1.2, 0.55, (253, 251, 244)),
    "rough": SurfaceSpec(SurfaceMaterial.PAPER, "rough watercolor", 0.220, 2.5, 0.65, (252, 250, 242)),
    "copy_paper": SurfaceSpec(SurfaceMaterial.PAPER, "copy paper", 0.015, 0.3, 0.45, (245, 245, 243)),
    "newsprint": SurfaceSpec(SurfaceMaterial.PAPER, "newsprint", 0.060, 1.0, 0.80, (228, 226, 218)),
}

NIB_CATALOG: dict[str, NibSpec] = {
    "fineliner_03": NibSpec(ToolKind.FINELINER, 0.15, 4.0, 2.0, 1.05, 0.25, 1.2),
    "felt_medium": NibSpec(ToolKind.FELT_TIP, 0.70, 0.8, 1.5, 1.60, 0.70, 4.0),
    "fountain_f": NibSpec(ToolKind.FOUNTAIN, 0.20, 0.5, 1.2, 2.20, 0.90, 1.5),
    "ballpoint_blue": NibSpec(ToolKind.BALLPOINT, 0.18, 8.0, 4.0, 1.02, 0.10, 0.8),
    # pigment inks: pure-color dots, optically mixed on the page
    "fineliner_red": NibSpec(ToolKind.FINELINER, 0.15, 4.0, 2.0, 1.05, 0.25, 1.2, pigment_channel=0),
    "fineliner_blue": NibSpec(ToolKind.FINELINER, 0.15, 4.0, 2.0, 1.05, 0.25, 1.2, pigment_channel=1),
    "fineliner_yellow": NibSpec(ToolKind.FINELINER, 0.15, 4.0, 2.0, 1.05, 0.25, 1.2, pigment_channel=2),
}

PIGMENT_COLORS: dict[int, tuple[int, int, int]] = {0: (196, 48, 48), 1: (48, 84, 190), 2: (230, 180, 40)}


@dataclass
class StrokeCommand:
    """One planned hand motion, expanded to samples along the path (mm).

    The model-facing MCP tool takes compact parameters (start, end, curvature,
    pressure start/end, speed); this is the internal expanded form.
    """

    tool_id: str
    xs_mm: list[float]
    ys_mm: list[float]
    pressure01: list[float]  # 0..1 of the nib's max_pressure_n
    speed_mm_s: list[float]
    nib_angle_deg: list[float]

    def __post_init__(self) -> None:
        n = len(self.xs_mm)
        if not (len(self.ys_mm) == len(self.pressure01) == len(self.speed_mm_s) == len(self.nib_angle_deg) == n):
            raise ValueError("stroke sample arrays must have equal length")
        if n < 2:
            raise ValueError("a stroke needs at least 2 samples")

    @property
    def n_samples(self) -> int:
        return len(self.xs_mm)

    def length_mm(self) -> float:
        return sum(
            math.hypot(self.xs_mm[i] - self.xs_mm[i - 1], self.ys_mm[i] - self.ys_mm[i - 1])
            for i in range(1, self.n_samples)
        )


@dataclass
class StrokeEvent:
    """A localized thing the hand felt during a stroke."""

    kind: str  # skip | pool | splay | scratch | starved | run
    t01: float  # position along the stroke, 0..1
    x_mm: float
    y_mm: float
    note: str = ""


@dataclass
class StrokeFeedback:
    """What the hand feels. The sensory channel the artist learns to read."""

    resistance_mean_n: float
    resistance_peak_n: float
    resistance_profile: list[float] = field(default_factory=list)  # downsampled along path
    events: list[StrokeEvent] = field(default_factory=list)
    bleed_mm: float = 0.0
    coverage: float = 0.0  # estimated deposit coverage along the path, 0..1
    load_after_ml: float = 0.0
    touched_bbox_mm: tuple[float, float, float, float] | None = None


@dataclass
class ToolState:
    """A concrete tool instance the hand can hold."""

    tool_id: str
    spec: NibSpec
    load_ml: float
    wear: float = 0.0  # 0..1, accumulates with use


@dataclass
class HandState:
    """Where the hand is and what it holds. Swapping and loading are explicit."""

    x_mm: float = 0.0
    y_mm: float = 0.0
    held_tool_id: str | None = None
    pressure_n: float = 0.0


class Paper:
    """A surface instance: procedural tooth heightfield, deterministic per seed.

    v0 uses a seeded sinusoid mixture; value noise can replace it later without
    changing the interface.
    """

    def __init__(
        self,
        spec: SurfaceSpec,
        seed: int = 0,
        size_mm: tuple[float, float] = (297.0, 420.0),
    ) -> None:
        self.spec = spec
        self.seed = seed
        self.size_mm = size_mm
        self.components = self._build_components()

    def _build_components(self) -> list[tuple[float, float, float, float]]:
        rng = random.Random(self.seed)
        lam = self.spec.tooth_wavelength_mm
        components = []
        # Each octave gets its own random orientation — isotropic tooth, no
        # directional striping.
        for harmonic, weight in ((1.0, 0.55), (2.1, 0.28), (3.7, 0.17)):
            amp = self.spec.tooth_amplitude_mm * weight
            k = 2.0 * math.pi * harmonic / lam
            theta = rng.uniform(0.0, math.pi)
            phase = rng.uniform(0.0, 2.0 * math.pi)
            components.append((amp, k * math.cos(theta), k * math.sin(theta), phase))
        return components

    def height_mm(self, x_mm: float, y_mm: float) -> float:
        """Surface height at a point; the tooth the nib rides over."""
        return sum(amp * math.sin(fx * x_mm + fy * y_mm + phase) for amp, fx, fy, phase in self.components)

    def catch_probability(self, pressure01: float, ink_film: float) -> float:
        """Chance the tooth catches the tip and the stroke skips.

        High tooth, low pressure, thin film → more skips. This is the felt
        difference between plate bristol and rough stock. Placeholder constants;
        to be calibrated experimentally.
        """
        p = (self.spec.tooth_amplitude_mm / 0.25) * (1.0 - pressure01) * (1.0 - min(ink_film, 1.0)) * 0.5
        return max(0.0, min(0.85, p))
