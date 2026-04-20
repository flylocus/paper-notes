#!/usr/bin/env python3
"""Archived experimental entrypoint."""

from __future__ import annotations

import sys


def main() -> int:
    sys.stderr.write(
        "ERROR: generate_cards_pillow.py is archived and not part of the production baseline.\n"
        "Use scripts/generate_cards.py for formal image generation.\n"
        "Experimental version moved to:\n"
        "  - scripts/experimental/generate_cards_pillow.py\n"
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
