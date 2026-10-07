#!/usr/bin/env python3
from __future__ import annotations
import argparse
import re
from pathlib import Path

TARGET_DIRS = ["common", "events"]
SKIP_DIRS = {".git", "__pycache__", "on_action", "customizable_localization"}
TOKEN_RE = re.compile(r"^(?P<id>[A-Za-z0-9_\.\-]+)\s*=\s*\{")
ALLOWED_PREFIXES = (
    "rol_",
    "activity_rol_",
    "phase_rol_",
)
ALLOWED_EXACT = {
    "namespace",
}


def is_candidate_line(line: str) -> bool:
    if not line or line[0].isspace():
        return False
    if line.startswith("#"):
        return False
    return True


def is_violation(token: str) -> bool:
    if token in ALLOWED_EXACT:
        return False
    return not token.startswith(ALLOWED_PREFIXES)


def main() -> int:
    ap = argparse.ArgumentParser(description="Check top-level custom ID prefixes.")
    ap.add_argument("root", nargs="?", default=r"C:\CK3Mods\RoL")
    args = ap.parse_args()

    root = Path(args.root)
    if not root.exists():
        print(f"[ERROR] root not found: {root}")
        return 2

    violations: list[tuple[Path, int, str]] = []
    for d in TARGET_DIRS:
        base = root / d
        if not base.exists():
            continue
        for p in base.rglob("*.txt"):
            if any(part in SKIP_DIRS for part in p.parts):
                continue
            text = p.read_text(encoding="utf-8-sig", errors="ignore").splitlines()
            for i, line in enumerate(text, start=1):
                if not is_candidate_line(line):
                    continue
                m = TOKEN_RE.match(line)
                if not m:
                    continue
                token = m.group("id")
                if is_violation(token):
                    violations.append((p, i, token))

    if violations:
        print(f"[FAIL] prefix violations: {len(violations)}")
        for p, i, token in violations[:200]:
            print(f"  - {p}:{i}: {token}")
        if len(violations) > 200:
            print(f"  ... and {len(violations)-200} more")
        return 1

    print("[OK] no top-level ID prefix violations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
