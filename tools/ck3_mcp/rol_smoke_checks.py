#!/usr/bin/env python3
"""Run a dependency-free structural smoke check for RoL script files."""

from __future__ import annotations

import re
import sys
from pathlib import Path


EVENTS = {
    "rome": "events/rol_quest_rome_events.txt",
    "munich": "events/rol_quest_munich_events.txt",
    "naxos": "events/rol_quest_naxos_events.txt",
    "sevilla": "events/rol_quest_sevilla_events.txt",
    "carthage": "events/rol_quest_carthage_events.txt",
}


def balanced(text: str) -> bool:
    depth = 0
    for char in text:
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth < 0:
                return False
    return depth == 0


def main(root: Path) -> int:
    errors: list[str] = []
    for name, relative in EVENTS.items():
        path = root / relative
        if not path.exists():
            errors.append(f"{name}: missing {relative}")
            continue
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        if not balanced(text):
            errors.append(f"{name}: braces are unbalanced")
        if not re.search(r"^namespace\s*=\s*rol_", text, re.MULTILINE):
            errors.append(f"{name}: missing rol_ namespace")
        if "random_list = {" not in text:
            errors.append(f"{name}: missing challenge random_list")
    if errors:
        print(f"[FAIL] RoL smoke checks failed: {len(errors)} issue(s)")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(f"[OK] RoL smoke checks passed: {len(EVENTS)} quest namespaces")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2]))
