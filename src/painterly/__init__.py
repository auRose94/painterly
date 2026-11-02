"""Painterly: a physics-honest painting environment for tool-using AI artists."""

from .types import (
    HandState,
    NIB_CATALOG,
    PAPER_CATALOG,
    NibSpec,
    Paper,
    StrokeCommand,
    StrokeEvent,
    StrokeFeedback,
    SurfaceMaterial,
    SurfaceSpec,
    ToolKind,
    ToolState,
)

__version__ = "0.0.1"

__all__ = [
    "HandState",
    "NIB_CATALOG",
    "PAPER_CATALOG",
    "NibSpec",
    "Paper",
    "StrokeCommand",
    "StrokeEvent",
    "StrokeFeedback",
    "SurfaceMaterial",
    "SurfaceSpec",
    "ToolKind",
    "ToolState",
    "__version__",
]
