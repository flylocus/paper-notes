#!/usr/bin/env python3
"""Compatibility shim for the preferred maintenance backfill tool."""

from pathlib import Path
import runpy


TARGET = Path(__file__).resolve().parent / "maintenance" / "backfill_output_dir.py"


if __name__ == "__main__":
    runpy.run_path(str(TARGET), run_name="__main__")
