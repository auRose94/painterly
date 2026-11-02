import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import painterly as pl
from painterly.fonts import FONT, ROWS, glyph, text_width_mm
from painterly.session import Session


def test_font_glyphs_are_well_formed():
    for ch, rows in FONT.items():
        assert len(rows) == ROWS, ch
        assert all(len(r) == 5 for r in rows), ch


def test_glyph_lookup_is_case_insensitive():
    assert glyph("a") == glyph("A")
    assert glyph("~") == FONT[" "]


def test_stamp_text_writes_ink_for_the_right_dab_count():
    tmp = Path(__file__).resolve().parents[1] / "sessions" / "_test_type"
    import shutil

    shutil.rmtree(tmp, ignore_errors=True)
    s = Session(tmp, paper_id="plate_bristol", seed=5, size_mm=(60.0, 40.0))
    dabs_before = sum(1 for ln in (tmp / "log.jsonl").read_text().splitlines() if '"type"' in ln and "stroke" in ln)
    from painterly.fonts import stamp_text

    w = stamp_text(s, 20.0, 10.0, "L", height_mm=2.8)
    lines = (tmp / "log.jsonl").read_text().splitlines()
    dabs_after = sum(1 for ln in lines if '"type"' in ln and "stroke" in ln)
    bits = sum(r.count("1") for r in FONT["L"])
    assert dabs_after - dabs_before == bits, f"L should stamp {bits} dabs"
    assert w > 0
    shutil.rmtree(tmp, ignore_errors=True)
