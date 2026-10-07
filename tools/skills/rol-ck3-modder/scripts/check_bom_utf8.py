#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path

TEXT_EXTS = {".txt", ".yml", ".yaml", ".gui", ".md", ".mod", ".ps1", ".py"}
SKIP_DIRS = {".git", "__pycache__"}
BOM = b"\xef\xbb\xbf"


def should_check(path: Path) -> bool:
    if any(part in SKIP_DIRS for part in path.parts):
        return False
    return path.suffix.lower() in TEXT_EXTS


def main() -> int:
    ap = argparse.ArgumentParser(description="Check UTF-8 BOM for text files.")
    ap.add_argument("root", nargs="?", default=r"C:\CK3Mods\RoL")
    args = ap.parse_args()

    root = Path(args.root)
    if not root.exists():
        print(f"[ERROR] root not found: {root}")
        return 2

    missing = []
    for p in root.rglob("*"):
        if not p.is_file() or not should_check(p):
            continue
        try:
            with p.open("rb") as f:
                head = f.read(3)
            if head != BOM:
                missing.append(p)
        except Exception as e:
            print(f"[WARN] cannot read {p}: {e}")

    if missing:
        print(f"[FAIL] {len(missing)} file(s) without UTF-8 BOM:")
        for p in missing:
            print(f"  - {p}")
        return 1

    print("[OK] all checked text files have UTF-8 BOM")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
