#!/usr/bin/env python3
"""Compatibility shim for the preferred production payload builder."""

from pathlib import Path
import runpy


TARGET = Path(__file__).resolve().parent / "production" / "build_payload.py"


if __name__ == "__main__":
    runpy.run_path(str(TARGET), run_name="__main__")
