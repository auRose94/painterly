"""End-to-end MCP test: spawn the server over stdio and hold the hand."""

import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from mcp import ClientSession, StdioServerParameters  # noqa: E402
from mcp.client.stdio import stdio_client  # noqa: E402


async def main() -> None:
    tmp = tempfile.mkdtemp(prefix="painterly_mcp_test_")
    params = StdioServerParameters(
        command=sys.executable,
        args=[str(ROOT / "src" / "painterly" / "server.py")],
        cwd=str(ROOT),
        env={**os.environ, "PAINTERLY_SESSION_DIR": str(Path(tmp) / "s")},
    )
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            tools = {t.name for t in (await s.list_tools()).tools}
            expected = {
                "prepare_session", "select_tool", "stroke", "stroke_path",
                "guide_line", "soft_erase", "view", "note", "export_artwork",
            }
            assert expected <= tools, f"missing tools: {expected - tools}"

            out = json.loads((await s.call_tool("prepare_session", {"title": "mcp self-test"})).content[0].text)
            assert out["ok"]

            out = json.loads((await s.call_tool("select_tool", {"tool_id": "fineliner_03"})).content[0].text)
            assert out["held"] == "fineliner_03" and "feel" in out

            out = json.loads(
                (
                    await s.call_tool(
                        "stroke",
                        {"x0_mm": 20, "y0_mm": 40, "x1_mm": 90, "y1_mm": 42, "pressure_start": 0.4, "tag": "test"},
                    )
                ).content[0].text
            )
            assert "resistance_mean_n" in out and out["coverage"] > 0.5, out

            out = json.loads(
                (
                    await s.call_tool(
                        "stroke_path",
                        {"points_mm": [20, 60, 35, 40, 55, 40, 70, 60, 55, 78, 35, 78], "pressure": 0.3},
                    )
                ).content[0].text
            )
            assert "resistance_mean_n" in out and out["coverage"] > 0.5, out

            out = json.loads(
                (
                    await s.call_tool(
                        "guide_line",
                        {"x0_mm": 15, "y0_mm": 15, "x1_mm": 80, "y1_mm": 15, "color": "red", "opacity": 0.4},
                    )
                ).content[0].text
            )
            assert "resistance_mean_n" in out, out

            out = json.loads(
                (
                    await s.call_tool(
                        "soft_erase",
                        {"x0_mm": 40, "y0_mm": 41, "x1_mm": 60, "y1_mm": 41, "width_mm": 3, "strength": 0.6},
                    )
                ).content[0].text
            )
            assert "removed" in out and "peak_damage" in out, out

            out = json.loads((await s.call_tool("view", {"name": "selftest"})).content[0].text)
            assert Path(out["path"]).exists(), out

            out = json.loads((await s.call_tool("export_artwork", {"name": "selftest_art"})).content[0].text)
            assert Path(out["png"]).exists() and out["strokes"] >= 1, out

    print(f"MCP E2E PASS — {len(tools)} tools, session at {tmp}")


if __name__ == "__main__":
    asyncio.run(main())
