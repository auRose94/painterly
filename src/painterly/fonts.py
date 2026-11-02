"""Stamp typography: a 5x7 bitmap font inked one cell at a time.

The user's directive: a text system that simulates stamps for typography.
Real manga studios letter with pre-cut sets, so a stamp medium is faithful
to the pipeline — every glyph is a little letterpress plate, every cell a
dab of ink through the same physics as any other stroke.
"""

from __future__ import annotations

FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("11111", "00100", "00100", "00100", "00100", "00100", "11111"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    ".": ("00000", "00000", "00000", "00000", "00000", "00000", "00100"),
    ",": ("00000", "00000", "00000", "00000", "00000", "00100", "01000"),
    "'": ("00100", "00100", "00000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
}

COLS = 5
ROWS = 7


def glyph(ch: str) -> tuple[str, ...]:
    return FONT.get(ch.upper(), FONT[" "])


def text_width_mm(text: str, height_mm: float) -> float:
    """Ink width of a stamped line (advance per char is 6 cells)."""
    return len(text) * 6 * (height_mm / ROWS) - height_mm / ROWS


def stamp_text(session, x: float, y: float, text: str, height_mm: float = 2.6,
               tool: str = "fineliner_03", p: float = 0.52, tag: str = "type",
               subdabs: int = 1) -> float:
    """Stamp a line of text, top-left anchored. Returns the line width.

    Each set cell is inked through the ordinary stroke physics — the stamp is
    a medium, not a raster blit. `subdabs=2` inks each cell with four
    overlapping dabs: heavier, rounder letterforms at display sizes.
    """
    cell = height_mm / ROWS
    sub = 1.0 / (subdabs + 1)
    cursor = x
    if session.held != tool:
        session.select_tool(tool)
    for ch in text:
        g = glyph(ch)
        for row in range(ROWS):
            for col in range(COLS):
                if g[row][col] == "1":
                    for i in range(subdabs):
                        for j in range(subdabs):
                            cx = cursor + col * cell + (i + 1) * cell * sub
                            cy = y + row * cell + (j + 1) * cell * sub
                            session.stroke(cx, cy, cx + cell * 0.34, cy + cell * 0.2,
                                           pressure_start=p, pressure_end=p * 0.9,
                                           speed_mm_s=90, tag=tag)
        cursor += 6 * cell
    return cursor - x - cell
