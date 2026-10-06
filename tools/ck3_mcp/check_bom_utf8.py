#!/usr/bin/env python3
"""Verify that RoL text assets use UTF-8 with BOM."""

from __future__ import annotations

import sys
from pathlib import Path


TEXT_SUFFIXES = {".txt", ".yml", ".gui", ".gfx", ".asset"}
TEXT_ROOTS = ("common", "decisions", "events", "gfx", "interface", "localization")


def main(root: Path) -> int:
    missing: list[str] = []
    for directory in TEXT_ROOTS:
        base = root / directory
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
                if not path.read_bytes().startswith(b"\xef\xbb\xbf"):
                    missing.append(str(path.relative_to(root)))
    if missing:
        print(f"[FAIL] UTF-8 BOM missing from {len(missing)} file(s)")
        for path in missing:
            print(f"  - {path}")
        return 1
    print("[OK] UTF-8 BOM check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2]))
