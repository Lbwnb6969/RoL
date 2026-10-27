# -*- coding: utf-8 -*-
"""Audit RoL DDS headers, dimensions, and compression without external tools.

Malformed DDS files fail the audit. Existing pre-canonical dimensions are
reported as warnings so the static gate remains useful while assets are
replaced in batches.
"""

from __future__ import annotations

import struct
import sys
from collections import Counter
from pathlib import Path


KNOWN_FOURCC = {b"DXT1", b"DXT3", b"DXT5", b"ATI1", b"ATI2"}


def _owned(path: Path) -> bool:
    return path.name.lower().startswith("rol_") or path.name.lower().startswith("activity_rol_")


def _expected(path: Path) -> tuple[set[tuple[int, int]], str] | None:
    parts = {part.lower() for part in path.parts}
    if "event_scenes" in parts:
        return {(1592, 848)}, "event scene"
    if "activities" in parts and "illustrations" in parts:
        return {(1592, 848)}, "activity illustration"
    if "activity_header_backgrounds" in parts:
        return {(1100, 440)}, "activity header background"
    if "illustrations" in parts and "decisions" in parts:
        return {(1100, 440)}, "decision illustration"
    if "icons" in parts and "activities" in parts:
        return {(80, 80), (164, 164)}, "activity icon"
    if "icons" in parts and "artifact" in parts:
        return {(240, 240), (60, 60)}, "artifact icon"
    return None


def audit(root: Path) -> int:
    errors: list[str] = []
    warnings: list[str] = []
    dimensions: Counter[tuple[int, int, bytes]] = Counter()
    files = sorted(path for path in (root / "gfx").rglob("*.dds") if path.is_file() and _owned(path))
    for path in files:
        relative = path.relative_to(root).as_posix()
        data = path.read_bytes()
        if len(data) < 128 or data[:4] != b"DDS ":
            errors.append(f"{relative}: missing DDS magic/header")
            continue
        header_size = struct.unpack_from("<I", data, 4)[0]
        height, width = struct.unpack_from("<II", data, 12)
        pixel_format_size, pixel_format_flags = struct.unpack_from("<II", data, 76)
        fourcc = data[84:88]
        if fourcc == b"\x00\x00\x00\x00":
            fourcc = b""
        rgb_bits = struct.unpack_from("<I", data, 88)[0]
        if header_size != 124 or pixel_format_size != 32:
            errors.append(f"{relative}: invalid header sizes ({header_size}/{pixel_format_size})")
            continue
        if width <= 0 or height <= 0:
            errors.append(f"{relative}: invalid dimensions {width}x{height}")
            continue
        if fourcc and fourcc not in KNOWN_FOURCC:
            errors.append(f"{relative}: unsupported fourCC {fourcc!r}")
            continue
        if not fourcc and not (pixel_format_flags & 0x40) or (not fourcc and rgb_bits not in {24, 32}):
            errors.append(f"{relative}: uncompressed pixel format is incomplete")
            continue
        dimensions[(width, height, fourcc)] += 1
        expected = _expected(path)
        if expected and (width, height) not in expected[0]:
            warnings.append(f"{relative}: {expected[1]} is {width}x{height}; canonical target is {sorted(expected[0])}")

    if errors:
        print(f"[FAIL] RoL DDS audit failed: {len(errors)} issue(s)")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(f"[OK] RoL DDS audit passed: {len(files)} owned DDS assets, {len(dimensions)} header variants")
    for warning in warnings:
        print(f"[WARN] {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(audit(Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2]))
