#!/usr/bin/env python3
"""Compatibility launcher for the backend package layout."""

import os
import runpy
import sys


ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND = os.path.join(ROOT, "backend")

sys.path.insert(0, BACKEND)
runpy.run_path(os.path.join(BACKEND, "run_p2pool.py"), run_name="__main__")
