#!/usr/bin/env python3
"""Verify that RoL text assets use UTF-8 with BOM."""

from __future__ import annotations

import sys
from pathlib import Path


TEXT_SUFFIXES = {".txt", ".yml", ".gui", ".gfx", ".asset"}
TEXT_ROOTS = ("common", "decisions", "events", "gfx", "gui", "interface", "localization")


def main(root: Path) -> int:
    missing: list[str] = []
    invalid: list[str] = []
    paths: list[Path] = []
    for directory in TEXT_ROOTS:
        base = root / directory
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
                paths.append(path)
    if (root / "descriptor.mod").is_file():
        paths.append(root / "descriptor.mod")
    for path in paths:
        data = path.read_bytes()
        if not data.startswith(b"\xef\xbb\xbf"):
            missing.append(str(path.relative_to(root)))
        try:
            data.decode("utf-8-sig", errors="strict")
        except UnicodeDecodeError:
            invalid.append(str(path.relative_to(root)))
    if missing:
        print(f"[FAIL] UTF-8 BOM missing from {len(missing)} file(s)")
        for path in missing:
            print(f"  - {path}")
    if invalid:
        print(f"[FAIL] Invalid UTF-8 in {len(invalid)} file(s)")
        for path in invalid:
            print(f"  - {path}")
    if missing or invalid:
        return 1
    print(f"[OK] UTF-8 BOM and strict decoding passed ({len(paths)} files, including GUI/descriptor)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2]))
