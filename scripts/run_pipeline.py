#!/usr/bin/env python3
"""Archived experimental entrypoint."""

from __future__ import annotations

import sys


def main() -> int:
    sys.stderr.write(
        "ERROR: run_pipeline.py is archived and not the formal paper-notes runner.\n"
        "Use scripts/daily_runner.py for the formal flow.\n"
        "Experimental version moved to:\n"
        "  - scripts/experimental/run_pipeline.py\n"
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
