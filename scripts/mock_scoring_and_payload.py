#!/usr/bin/env python3
"""Archived experimental entrypoint."""

from __future__ import annotations

import sys


def main() -> int:
    sys.stderr.write(
        "ERROR: mock_scoring_and_payload.py is archived and not production-safe.\n"
        "Experimental version moved to:\n"
        "  - scripts/experimental/mock_scoring_and_payload.py\n"
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
