#!/usr/bin/env python3
"""Fast, dependency-free static audit for the RoL CK3 content contract.

This deliberately checks only RoL-owned references. Vanilla paths in GUI
overrides are resolved by CK3's base game and are outside this audit's scope.
"""

from __future__ import annotations

import re
import struct
import sys
from pathlib import Path


CHAINS = {
    "rome": {
        "activity": "activity_rol_seek_mars_blade",
        "activity_file": "common/activities/activity_types/rol_mars_activity.txt",
        "events": "events/rol_quest_rome_events.txt",
        "discovery": "rol_relic_discovery.1000",
        "entry": "rol_quest_rome.0990",
        "completion_flag": "rol_mars_blade_claimed",
    },
    "munich": {
        "activity": "activity_rol_seek_nibelung_sphere",
        "activity_file": "common/activities/activity_types/rol_nibelung_activity.txt",
        "events": "events/rol_quest_munich_events.txt",
        "discovery": "rol_relic_discovery.1300",
        "entry": "rol_quest_munich.0990",
        "completion_flag": "rol_nibelung_sphere_claimed",
    },
    "naxos": {
        "activity": "activity_rol_seek_naxos_guard",
        "activity_file": "common/activities/activity_types/rol_naxos_activity.txt",
        "events": "events/rol_quest_naxos_events.txt",
        "discovery": "rol_relic_discovery.1400",
        "entry": "rol_quest_naxos.0990",
        "completion_flag": "rol_naxos_unit_unlocked",
    },
    "sevilla": {
        "activity": "activity_rol_seek_astrolabe_of_ocean",
        "activity_file": "common/activities/activity_types/rol_astrolabe_activity.txt",
        "events": "events/rol_quest_sevilla_events.txt",
        "discovery": "rol_relic_discovery.1500",
        "entry": "rol_quest_sevilla.0990",
        "completion_flag": "rol_astrolabe_of_ocean_claimed",
    },
    "carthage": {
        "activity": "activity_rol_seek_ash_forged_mask",
        "activity_file": "common/activities/activity_types/rol_carthage_activity.txt",
        "events": "events/rol_quest_carthage_events.txt",
        "discovery": "rol_relic_discovery.1600",
        "entry": "rol_quest_carthage.0990",
        "completion_flag": "rol_ash_forged_mask_claimed",
    },
}

REQUIRED_ACTIVITY_BLOCKS = (
    "is_shown",
    "can_start_showing_failures_only",
    "is_valid",
    "on_start",
    "province_filter_target",
    "is_location_valid",
    "phases",
    "host_intents",
    "guest_intents",
    "conclusion_description",
    "on_complete",
    "header_background",
    "background",
    "window_characters",
)

# CK3 accepts both key:0 "..." and key: "..." localization forms.
LOC_KEY_RE = re.compile(r'^\s+([A-Za-z0-9_.-]+):(?:\d+)?\s*(?:"|$)')
GFX_REF_RE = re.compile(r"(?:\"|=\s*)(gfx/[^\"\s]+)")
LOC_REF_RE = re.compile(r"\b(?:title|desc|name|flavor|text)\s*=\s*(rol_[A-Za-z0-9_.-]+)")

# Newly generated event scenes are kept on the canonical CK3 background
# contract. Older RoL placeholders are intentionally left alone until their
# individual replacement batches are reviewed.
DDS_ASSETS = {
    "gfx/interface/illustrations/event_scenes/rol_event_rival_expedition.dds": (1592, 848, b"DXT1"),
    "gfx/interface/illustrations/event_scenes/rol_event_relic_scholarly_study.dds": (1592, 848, b"DXT1"),
    "gfx/interface/illustrations/event_scenes/rol_event_relic_new_owner.dds": (1592, 848, b"DXT1"),
    "gfx/interface/illustrations/event_scenes/rol_event_rival_pact.dds": (1592, 848, b"DXT1"),
    "gfx/interface/illustrations/event_scenes/rol_event_relic_legacy_transfer.dds": (1592, 848, b"DXT1"),
    "gfx/interface/illustrations/event_scenes/rol_event_fragment_expedition.dds": (1592, 848, b"DXT1"),
    "gfx/interface/illustrations/event_scenes/rol_event_fragment_upgrade.dds": (1592, 848, b"DXT1"),
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def check_chain(root: Path, name: str, chain: dict[str, str], errors: list[str]) -> None:
    activity_path = root / chain["activity_file"]
    events_path = root / chain["events"]
    discovery_path = root / "events/rol_relic_discovery_events.txt"
    if not activity_path.exists():
        errors.append(f"{name}: missing activity file {activity_path}")
        return
    if not events_path.exists():
        errors.append(f"{name}: missing event file {events_path}")
        return

    activity = read_text(activity_path)
    events = read_text(events_path)
    discovery = read_text(discovery_path)
    if not re.search(rf"^\s*{re.escape(chain['activity'])}\s*=\s*\{{", activity, re.MULTILINE):
        errors.append(f"{name}: activity id {chain['activity']} is missing")
    for block in REQUIRED_ACTIVITY_BLOCKS:
        if not re.search(rf"^\s*{re.escape(block)}\s*=", activity, re.MULTILINE):
            errors.append(f"{name}: activity missing {block}")
    if not re.search(rf"^\s*{re.escape(chain['entry'])}\s*=\s*\{{", events, re.MULTILINE):
        errors.append(f"{name}: missing activity entry event {chain['entry']}")
    if chain["discovery"] not in discovery:
        errors.append(f"{name}: discovery event {chain['discovery']} is not wired")
    if chain["completion_flag"] not in events:
        errors.append(f"{name}: completion flag {chain['completion_flag']} is not present in event chain")

    for ref in re.findall(r'header_background\s*=\s*"([^"]+)"', activity):
        path = root / ref
        if not path.exists():
            errors.append(f"{name}: missing header background {ref}")
    for ref in re.findall(r'\btexture\s*=\s*"([^"]+)"', activity):
        path = root / ref
        if not path.exists():
            errors.append(f"{name}: missing activity background {ref}")


def check_localization_parity(root: Path, errors: list[str]) -> tuple[int, int]:
    def keys(language: str) -> tuple[set[str], dict[str, str]]:
        found: set[str] = set()
        locations: dict[str, str] = {}
        for path in sorted((root / "localization" / language).glob("rol_*.yml")):
            for line_no, line in enumerate(read_text(path).splitlines(), 1):
                match = LOC_KEY_RE.match(line)
                if not match:
                    continue
                key = match.group(1)
                if key in found:
                    errors.append(f"{language}: duplicate localization key {key} at {path}:{line_no} (first {locations[key]})")
                found.add(key)
                locations.setdefault(key, f"{path}:{line_no}")
        return found, locations

    english, _ = keys("english")
    chinese, _ = keys("simp_chinese")
    for key in sorted(english - chinese):
        errors.append(f"localization: missing simp_chinese key {key}")
    for key in sorted(chinese - english):
        errors.append(f"localization: missing english key {key}")
    for directory in (root / "common", root / "events"):
        for path in directory.rglob("*.txt"):
            for value in LOC_REF_RE.findall(read_text(path)):
                # Variable names such as rol_rome_stage_count are not loc
                # keys. Dotted event keys and activity keys are display text.
                if value in english or value in chinese:
                    continue
                if "." in value or value.startswith("activity_rol_"):
                    errors.append(f"localization: missing display key {value} referenced by {path}")
    return len(english), len(chinese)


def check_rol_gfx_references(root: Path, errors: list[str]) -> int:
    references = 0
    for directory in (root / "common", root / "events", root / "localization", root / "gfx"):
        if not directory.exists():
            continue
        for path in directory.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in {".txt", ".gui", ".gfx", ".yml", ".asset"}:
                continue
            text = read_text(path)
            for ref in GFX_REF_RE.findall(text):
                if "rol_" not in ref.lower():
                    continue
                references += 1
                if not (root / ref.replace("\\", "/")).exists():
                    errors.append(f"gfx: missing RoL asset {ref} referenced by {path}")
    return references


def check_dds_assets(root: Path, errors: list[str]) -> int:
    checked = 0
    for relative, (expected_width, expected_height, expected_fourcc) in DDS_ASSETS.items():
        path = root / relative
        if not path.exists():
            errors.append(f"dds: missing generated asset {relative}")
            continue
        data = path.read_bytes()
        if len(data) < 128 or data[:4] != b"DDS ":
            errors.append(f"dds: invalid header {relative}")
            continue
        height, width = struct.unpack_from("<II", data, 12)
        fourcc = data[84:88]
        if (width, height, fourcc) != (expected_width, expected_height, expected_fourcc):
            errors.append(
                f"dds: {relative} is {width}x{height}/{fourcc!r}; "
                f"expected {expected_width}x{expected_height}/{expected_fourcc!r}"
            )
            continue
        checked += 1
    return checked


def audit(root: Path) -> int:
    errors: list[str] = []
    if not root.exists():
        print(f"[FAIL] root does not exist: {root}")
        return 1
    for name, chain in CHAINS.items():
        check_chain(root, name, chain, errors)
    english_count, chinese_count = check_localization_parity(root, errors)
    gfx_count = check_rol_gfx_references(root, errors)
    dds_count = check_dds_assets(root, errors)
    if errors:
        print(f"[FAIL] RoL static audit failed: {len(errors)} issue(s)")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(f"[OK] RoL static audit passed: {len(CHAINS)} activities, {english_count} English keys, {chinese_count} Chinese keys, {gfx_count} RoL gfx references, {dds_count} canonical DDS assets")
    return 0


if __name__ == "__main__":
    raise SystemExit(audit(Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2]))
