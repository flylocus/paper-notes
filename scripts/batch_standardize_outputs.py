#!/usr/bin/env python3
"""Compatibility shim for the preferred maintenance batch tool."""

from pathlib import Path
import runpy


TARGET = Path(__file__).resolve().parent / "maintenance" / "batch_standardize_outputs.py"


if __name__ == "__main__":
    runpy.run_path(str(TARGET), run_name="__main__")
