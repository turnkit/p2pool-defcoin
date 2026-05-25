#!/usr/bin/env python3
"""Compile-check all Python sources during the Python 3 migration.

This is a syntax gate only. Passing it does not prove runtime correctness
because p2pool still needs a byte/string audit before it can safely process
shares or network messages under Python 3.
"""

from pathlib import Path
import py_compile


SKIP_DIRS = {".git", ".venv", "__pycache__"}


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    failures = []
    total = 0
    for path in root.rglob("*.py"):
        if SKIP_DIRS.intersection(path.parts):
            continue
        total += 1
        try:
            py_compile.compile(str(path), doraise=True)
        except Exception as exc:  # pragma: no cover - diagnostic script
            failures.append((path.relative_to(root), exc))

    print(f"python_files {total}")
    print(f"py3_compile_failures {len(failures)}")
    for path, exc in failures:
        print(f"{path}\t{type(exc).__name__}\t{str(exc).splitlines()[-1]}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
