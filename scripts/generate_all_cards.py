#!/usr/bin/env python3
"""Archived experimental entrypoint.

This script was moved out of the main production surface.
Use scripts/experimental/generate_all_cards.py only for parallel experiments.
"""

from __future__ import annotations

import sys


def main() -> int:
    sys.stderr.write(
        "ERROR: generate_all_cards.py is archived and not part of the production baseline.\n"
        "Use one of these instead:\n"
        "  - scripts/daily_runner.py\n"
        "  - scripts/generate_cards.py\n"
        "  - scripts/generate_cover.py\n"
        "If you really need the experiment, run:\n"
        "  - scripts/experimental/generate_all_cards.py\n"
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
