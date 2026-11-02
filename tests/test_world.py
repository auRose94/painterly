import pytest

from painterly.world import Box, Camera, Mannequin


def test_human_scale_is_automatic():
    cam = Camera(vp_mm=(60.0, 60.0), eye_height_m=1.6, focal_mm=55.0)
    # a 2.0 m door, 0.9 m wide, front face at 8 m depth
    door = Box(x=0.0, y=0.0, z=8.0, w=0.9, h=2.0)
    pts = cam.project_box(door)["front"]
    bl, br, tr, tl = pts
    height_mm = bl[1] - tl[1]
    assert height_mm == pytest.approx(55.0 * 2.0 / 8.0, rel=1e-6)  # 13.75 mm
    width_mm = br[0] - bl[0]
    assert width_mm == pytest.approx(55.0 * 0.9 / 8.0, rel=1e-6)
    # door bottom sits ON the ground line for its depth
    gx, gy = cam.ground_at(-0.45, 8.0)
    assert bl == pytest.approx((gx, gy))
    # eye height lands on the horizon
    ex, ey = cam.project(0.0, 1.6, 8.0)
    assert ey == pytest.approx(60.0)


def test_depth_scaling_and_margins():
    cam = Camera(vp_mm=(60.0, 60.0), eye_height_m=1.6, focal_mm=55.0)
    near = cam.project(0.0, 0.0, 4.0)
    far = cam.project(0.0, 0.0, 8.0)
    # ground recedes upward toward the horizon as depth grows
    assert far[1] < near[1]
    assert far[1] > 60.0  # but stays below the horizon (eye above ground)
    # two buildings with a 3 m margin between them keep that margin in
    # projection, shrinking with depth
    a = Box(x=-5.0, y=0.0, z=10.0, w=6.0, h=12.0)
    b = Box(x=4.0, y=0.0, z=10.0, w=6.0, h=9.0)
    pa = cam.project_box(a)["front"]
    pb = cam.project_box(b)["front"]
    gap_mm = pb[0][0] - pa[1][0]
    assert gap_mm == pytest.approx(55.0 * 3.0 / 10.0, rel=1e-6)


def test_rejects_behind_camera():
    cam = Camera(vp_mm=(60.0, 60.0), eye_height_m=1.6, focal_mm=55.0)
    with pytest.raises(ValueError):
        cam.project(0.0, 0.0, -1.0)


def test_mannequin_canon_proportions():
    m = Mannequin(height_m=1.7)
    head = 0.23
    assert abs(m.head_c[1] - (1.7 - head / 2)) < 1e-9
    # 7.5-head canon: total height == 7.5 heads
    assert abs(1.7 / head - 7.39) < 0.05
    # shoulders two head-widths across (2 * 0.23 m)
    assert abs((m.shoulder_r[0] - m.shoulder_l[0]) - 0.46) < 1e-9
    # eye line at mid-head, symmetric anchors
    assert m.eye_l[1] == m.eye_r[1]
    assert abs(m.eye_l[1] - (1.7 - head * 0.55)) < 1e-9
    assert m.eye_l[0] == -m.eye_r[0]


def test_mannequin_yaw_rotates_not_floats():
    m = Mannequin(height_m=1.7, yaw_deg=90.0)
    # the head is on the axis: yaw must not move it
    assert abs(m.head_c[0]) < 1e-9
    # the left shoulder swings from -x to +z
    assert abs(m.shoulder_l[0]) < 1e-6
    assert abs(m.shoulder_l[2] - 0.23) < 1e-6
    # height never changes with yaw
    assert abs(m.shoulder_l[1] - (1.7 - 0.345)) < 1e-9


def test_limb_quad_scales_with_depth():
    cam = Camera(vp_mm=(60.0, 60.0), eye_height_m=1.6, focal_mm=55.0)
    near = cam.limb_quad((0.0, 1.0, 4.0), (0.0, 1.4, 4.0), 0.05, 0.04)
    far = cam.limb_quad((0.0, 1.0, 8.0), (0.0, 1.4, 8.0), 0.05, 0.04)
    def width(q):
        return q[1][0] - q[0][0]
    assert abs(width(far) - width(near) / 2) < 1e-6, "limb width halves as depth doubles"
