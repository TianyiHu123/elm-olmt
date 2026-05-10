#!/usr/bin/env python
"""Backward-compatible entry point; use train_surrogate_forcing.py for the CLI driver."""
from __future__ import annotations

import sys

from train_surrogate_forcing import main


if __name__ == "__main__":
    raise SystemExit(main())
