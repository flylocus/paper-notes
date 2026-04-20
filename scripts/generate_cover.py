#!/usr/bin/env python3
"""Compatibility shim for the preferred production cover generator."""

from pathlib import Path
import runpy


TARGET = Path(__file__).resolve().parent / "production" / "generate_cover.py"


if __name__ == "__main__":
    runpy.run_path(str(TARGET), run_name="__main__")
