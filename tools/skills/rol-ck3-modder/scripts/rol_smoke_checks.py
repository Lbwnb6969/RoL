#!/usr/bin/env python3
from __future__ import annotations
import argparse
import re
from pathlib import Path


def must_contain(path: Path, pattern: str, label: str, errors: list[str]) -> None:
    if not path.exists():
        errors.append(f"missing file: {path}")
        return
    content = path.read_text(encoding="utf-8-sig", errors="ignore")
    if not re.search(pattern, content, flags=re.MULTILINE):
        errors.append(f"missing {label} in {path}")


def main() -> int:
    ap = argparse.ArgumentParser(description="RoL smoke checks for 4 quest chains.")
    ap.add_argument("root", nargs="?", default=r"C:\CK3Mods\RoL")
    args = ap.parse_args()

    root = Path(args.root)
    errors: list[str] = []

    checks = [
        (root / "events/rol_quest_rome_events.txt", r"rol_quest_rome\.1050\s*=\s*\{", "rome guest event .1050"),
        (root / "events/rol_quest_munich_events.txt", r"rol_quest_munich\.1050\s*=\s*\{", "munich guest event .1050"),
        (root / "events/rol_quest_naxos_events.txt", r"rol_quest_naxos\.1050\s*=\s*\{", "naxos guest event .1050"),
        (root / "events/rol_quest_sevilla_events.txt", r"rol_quest_sevilla\.1050\s*=\s*\{", "sevilla guest event .1050"),
        (root / "common/scripted_effects/rol_quest_rome_effects.txt", r"desc\s*=\s*rol_mars_activity_success_toast_desc", "rome toast desc"),
        (root / "common/scripted_effects/rol_quest_munich_effects.txt", r"desc\s*=\s*rol_nibelung_activity_success_toast_desc", "munich toast desc"),
        (root / "common/scripted_effects/rol_quest_naxos_effects.txt", r"desc\s*=\s*rol_naxos_activity_success_toast_desc", "naxos toast desc"),
        (root / "common/scripted_effects/rol_quest_sevilla_effects.txt", r"desc\s*=\s*rol_astrolabe_activity_success_toast_desc", "sevilla toast desc"),
        (root / "events/rol_quest_rome_events.txt", r"\.tt\.success", "rome exact success/failure outcome tooltip usage"),
        (root / "events/rol_quest_munich_events.txt", r"\.tt\.success", "munich exact success/failure outcome tooltip usage"),
        (root / "events/rol_quest_naxos_events.txt", r"\.tt\.success", "naxos exact success/failure outcome tooltip usage"),
        (root / "events/rol_quest_sevilla_events.txt", r"\.tt\.success", "sevilla exact success/failure outcome tooltip usage"),
        (root / "localization/english/rol_l_english.yml", r"rol_relic_fail_ends_expedition_tt", "english fail warning key"),
        (root / "localization/simp_chinese/rol_rome_l_simp_chinese.yml", r"rol_relic_fail_ends_expedition_tt", "chinese fail warning key"),
        (root / "localization/english/rol_munich_l_english.yml", r"Tier 4", "munich Tier 4 localization hint"),
        (root / "localization/english/rol_naxos_l_english.yml", r"Tier 4", "naxos Tier 4 localization hint"),
        (root / "localization/english/rol_sevilla_l_english.yml", r"Tier 4", "sevilla Tier 4 localization hint"),
    ]

    for p, pat, label in checks:
        must_contain(p, pat, label, errors)

    if errors:
        print(f"[FAIL] smoke checks failed: {len(errors)}")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("[OK] smoke checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
