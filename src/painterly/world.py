"""World-space perspective: design in meters, draw in millimeters.

The artist's rule this encodes: a building exists first as 3D values —
extents, margins, door heights — and every stroke's start and stop comes
from projecting those values through the camera. Human scale is automatic:
a door is 2.0 m tall because people are, and the projection makes it so.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

HEAD_M = 0.23  # chin-to-crown, adult; realistic canon is 7.5 heads tall



@dataclass
class Box:
    """An axis-aligned box in world meters: x lateral, z depth toward the
    vanishing point, y up from the ground."""

    x: float  # lateral center
    y: float  # bottom (ground = 0)
    z: float  # depth of the front face
    w: float  # width along x
    h: float  # height along y
    d: float = 0.0  # depth extent toward the viewer's vanishing direction

    @property
    def corners_front(self) -> list[tuple[float, float, float]]:
        x0, x1 = self.x - self.w / 2, self.x + self.w / 2
        z = self.z
        return [
            (x0, self.y, z),
            (x1, self.y, z),
            (x1, self.y + self.h, z),
            (x0, self.y + self.h, z),
        ]


@dataclass
class Camera:
    """One-point perspective camera.

    vp: the vanishing point on paper (mm) — where z = infinity lands.
    horizon_mm: the horizon line (mm). Equal to vp[1] by construction.
    eye_height_m: how high the camera floats above the ground plane.
    focal_mm: focal length in paper-millimeters per unit depth.
    """

    vp_mm: tuple[float, float]
    eye_height_m: float
    focal_mm: float
    horizon_mm: float = field(default=None)  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.horizon_mm is None:
            self.horizon_mm = self.vp_mm[1]

    def project(self, x_m: float, y_m: float, z_m: float) -> tuple[float, float]:
        """World meters -> paper millimeters. z must be > 0."""
        if z_m <= 0:
            raise ValueError("z must be positive (in front of the camera)")
        sx = self.vp_mm[0] + self.focal_mm * x_m / z_m
        sy = self.horizon_mm - self.focal_mm * (y_m - self.eye_height_m) / z_m
        return (sx, sy)

    def project_box(self, box: Box) -> dict[str, list[tuple[float, float]]]:
        """Project a box's front face corners (and back face, if it has depth)."""
        front = [self.project(*c) for c in box.corners_front]
        out = {"front": front}
        if box.d > 0:
            back = [self.project(c[0], c[1], c[2] - box.d) for c in box.corners_front]
            out["back"] = back
        return out

    def ground_at(self, x_m: float, z_m: float) -> tuple[float, float]:
        """Where the ground plane at (x, z) lands on paper."""
        return self.project(x_m, 0.0, z_m)

    def point_radius(self, p: tuple[float, float, float], r_m: float) -> float:
        """Screen radius (mm) of a sphere of r_m meters centered at p."""
        return r_m * self.focal_mm / p[2]

    def limb_quad(self, a, b, ra_m: float, rb_m: float):
        """Screen corners of a tapered limb between two world joints."""
        A = self.project(*a)
        B = self.project(*b)
        ra = ra_m * self.focal_mm / a[2]
        rb = rb_m * self.focal_mm / b[2]
        dx, dy = B[0] - A[0], B[1] - A[1]
        L = math.hypot(dx, dy) or 1.0
        px, py = -dy / L, dx / L
        return [(A[0] + px * ra, A[1] + py * ra), (B[0] + px * rb, B[1] + py * rb),
                (B[0] - px * rb, B[1] - py * rb), (A[0] - px * ra, A[1] - py * ra)]


@dataclass
class Mannequin:
    """A human figure in world meters, on the Richer 7.5-head canon:
    head + torso = 4 units, legs = the rest; shoulders ~2 head-widths
    (2.33 for the male canon); the eye line sits at mid-head.

    yaw_deg rotates the figure about its vertical axis (0 = facing camera).
    Face anchors ride the head so features land correctly at any yaw.
    """

    height_m: float = 1.7
    yaw_deg: float = 0.0

    def __post_init__(self) -> None:
        H = self.height_m
        head = HEAD_M
        a = math.radians(self.yaw_deg)
        c, sn = math.cos(a), math.sin(a)

        def R(x: float, y: float, z: float = 0.0):
            return (x * c + z * sn, y, -x * sn + z * c)

        self.head_c = R(0.0, H - head / 2, 0.0)
        self.head_r = head / 2
        self.chin = R(0.0, H - head, 0.0)
        self.neck = R(0.0, H - head - 0.05, 0.0)
        self.shoulder_l = R(-0.23, H - 0.345, 0.0)
        self.shoulder_r = R(0.23, H - 0.345, 0.0)
        self.chest = R(0.0, H - 0.46, 0.0)
        self.waist = R(0.0, H - 0.69, 0.0)
        self.hip_l = R(-0.17, H - 0.92, 0.0)
        self.hip_r = R(0.17, H - 0.92, 0.0)
        self.elbow_l = R(-0.26, H - 0.69, 0.03)
        self.elbow_r = R(0.26, H - 0.69, 0.03)
        self.wrist_l = R(-0.27, H - 0.94, 0.05)
        self.wrist_r = R(0.27, H - 0.94, 0.05)
        self.hand_l = R(-0.27, H - 1.04, 0.06)
        self.hand_r = R(0.27, H - 1.04, 0.06)
        self.hip_c = R(0.0, H - 0.92, 0.0)
        self.knee_l = R(-0.09, 0.42, 0.0)
        self.knee_r = R(0.09, 0.42, 0.0)
        self.ankle_l = R(-0.09, 0.07, 0.0)
        self.ankle_r = R(0.09, 0.07, 0.0)
        # face anchors, on the front of the head and rotating with it
        self.eye_l = R(-0.055, H - head * 0.55, head * 0.42)
        self.eye_r = R(0.055, H - head * 0.55, head * 0.42)
        self.nose = R(0.0, H - head * 0.66, head * 0.46)
        self.mouth = R(0.0, H - head * 0.80, head * 0.40)
        self.ear_l = R(-head / 2, H - head * 0.55, 0.0)
        self.ear_r = R(head / 2, H - head * 0.55, 0.0)
        # limbs: (world_a, world_b, radius_a_m, radius_b_m)
        self.limbs = [
            ((0.0, H - head * 0.35, 0.0), self.neck, 0.050, 0.045),
            (self.shoulder_l, self.elbow_l, 0.048, 0.038),
            (self.elbow_l, self.wrist_l, 0.038, 0.030),
            (self.shoulder_r, self.elbow_r, 0.048, 0.038),
            (self.elbow_r, self.wrist_r, 0.038, 0.030),
            (self.hip_l, self.knee_l, 0.075, 0.052),
            (self.knee_l, self.ankle_l, 0.052, 0.036),
            (self.hip_r, self.knee_r, 0.075, 0.052),
            (self.knee_r, self.ankle_r, 0.052, 0.036),
        ]
        # torso: shoulders -> waist -> hips, half-widths in meters
        self.torso = [
            R(-0.23, H - 0.345, 0.0), R(0.23, H - 0.345, 0.0),
            R(0.16, H - 0.69, 0.0), R(-0.16, H - 0.69, 0.0),
            R(0.17, H - 0.92, 0.0), R(-0.17, H - 0.92, 0.0),
        ]

    def placed(self, z_offset: float) -> "Mannequin":
        """A shallow copy of this figure slid forward `z_offset` meters —
        posed at the origin, placed in front of the camera."""
        import copy

        m2 = copy.copy(self)
        for name, val in self.__dict__.items():
            if isinstance(val, tuple) and len(val) == 3 and all(
                    isinstance(v, (int, float)) for v in val):
                setattr(m2, name, (val[0], val[1], val[2] + z_offset))
        if hasattr(self, "limbs"):
            m2.limbs = [((a[0], a[1], a[2] + z_offset), (b[0], b[1], b[2] + z_offset), ra, rb)
                        for (a, b, ra, rb) in self.limbs]
        if hasattr(self, "torso"):
            m2.torso = [(p[0], p[1], p[2] + z_offset) for p in self.torso]
        return m2
