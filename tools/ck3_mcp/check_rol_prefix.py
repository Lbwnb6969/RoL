#!/usr/bin/env python3
"""Check that RoL-owned top-level script IDs keep the rol_ prefix."""

from __future__ import annotations

import re
import sys
from pathlib import Path


TOP_LEVEL_ID = re.compile(r"^([A-Za-z][A-Za-z0-9_.]*)\s*=\s*\{")


def main(root: Path) -> int:
    errors: list[str] = []
    for directory in ("common", "decisions", "events"):
        base = root / directory
        if not base.exists():
            continue
        for path in base.rglob("rol_*.txt"):
            text = path.read_text(encoding="utf-8-sig", errors="replace")
            if directory == "events":
                namespace = re.search(r"^namespace\s*=\s*([^\s]+)", text, re.MULTILINE)
                if namespace and not namespace.group(1).startswith("rol_"):
                    errors.append(f"{path}: namespace {namespace.group(1)} is not rol_*")
            # A few CK3 registries intentionally use their vanilla hook name
            # (on_action) or a registry-specific prefix (activity_rol_ and
            # CamelCase custom localization). Check the namespaces where RoL
            # owns the complete identifier contract and leave those hooks
            # untouched.
            check_ids = directory == "events" or (
                directory == "common"
                and any(part in path.parts for part in ("decisions", "script_values", "scripted_effects", "scripted_modifiers"))
            )
            if check_ids:
                for line_no, line in enumerate(text.splitlines(), 1):
                    match = TOP_LEVEL_ID.match(line)
                    if match and not match.group(1).startswith("rol_"):
                        errors.append(f"{path}:{line_no}: top-level id {match.group(1)} is not rol_*")
    if errors:
        print(f"[FAIL] rol_ prefix check failed: {len(errors)} issue(s)")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("[OK] rol_ prefix check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2]))
