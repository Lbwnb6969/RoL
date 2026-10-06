# -*- coding: utf-8 -*-
"""Convert a PNG event background to a cropped BC1/DXT1 DDS.

The encoder intentionally targets opaque event backgrounds only.  It keeps the
conversion local and reproducible when DirectXTex is unavailable, and writes a
standard DDS header that CK3 can load.
"""

from __future__ import annotations

import argparse
import struct
from pathlib import Path

from PIL import Image


def _rgb565(rgb: tuple[int, int, int]) -> int:
    r, g, b = rgb
    return ((r * 31 + 127) // 255 << 11) | ((g * 63 + 127) // 255 << 5) | ((b * 31 + 127) // 255)


def _unpack565(value: int) -> tuple[int, int, int]:
    return (
        ((value >> 11) & 31) * 255 // 31,
        ((value >> 5) & 63) * 255 // 63,
        (value & 31) * 255 // 31,
    )


def _palette(c0: int, c1: int) -> list[tuple[int, int, int]]:
    a, b = _unpack565(c0), _unpack565(c1)
    return [
        a,
        b,
        tuple((2 * a[i] + b[i]) // 3 for i in range(3)),
        tuple((a[i] + 2 * b[i]) // 3 for i in range(3)),
    ]


def _block(block: list[tuple[int, int, int]]) -> bytes:
    # Use the darkest and lightest colors as endpoints. Keeping c0 > c1
    # selects opaque four-color BC1 mode, which is appropriate for backgrounds.
    lo = min(block, key=lambda c: (sum(c), c))
    hi = max(block, key=lambda c: (sum(c), c))
    c0, c1 = _rgb565(hi), _rgb565(lo)
    if c0 < c1:
        c0, c1 = c1, c0
    colors = _palette(c0, c1)
    indices = 0
    for i, color in enumerate(block):
        choice = min(range(4), key=lambda j: sum((color[k] - colors[j][k]) ** 2 for k in range(3)))
        indices |= choice << (2 * i)
    return struct.pack("<HHI", c0, c1, indices)


def _crop_resize(source: Path, width: int, height: int) -> Image.Image:
    image = Image.open(source).convert("RGB")
    source_ratio = image.width / image.height
    target_ratio = width / height
    if source_ratio > target_ratio:
        crop_width = round(image.height * target_ratio)
        left = (image.width - crop_width) // 2
        image = image.crop((left, 0, left + crop_width, image.height))
    else:
        crop_height = round(image.width / target_ratio)
        top = (image.height - crop_height) // 2
        image = image.crop((0, top, image.width, top + crop_height))
    return image.resize((width, height), Image.Resampling.LANCZOS)


def encode(source: Path, destination: Path, width: int = 1592, height: int = 848) -> None:
    if width % 4 or height % 4:
        raise ValueError("BC1 dimensions must be divisible by four")
    image = _crop_resize(source, width, height)
    pixels = image.load()
    blocks = bytearray()
    for y in range(0, height, 4):
        for x in range(0, width, 4):
            block = [pixels[x + dx, y + dy] for dy in range(4) for dx in range(4)]
            blocks.extend(_block(block))

    pixel_format = struct.pack("<I I 4s I I I I I", 32, 0x4, b"DXT1", 0, 0, 0, 0, 0)
    header = struct.pack(
        "<I I I I I I I 11I",
        124,
        0x1 | 0x2 | 0x4 | 0x1000,
        height,
        width,
        ((width + 3) // 4) * 8,
        0,
        1,
        *([0] * 11),
    )
    caps = struct.pack("<I I I I I", 0x1000, 0, 0, 0, 0)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(b"DDS " + header + pixel_format + caps + blocks)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--width", type=int, default=1592)
    parser.add_argument("--height", type=int, default=848)
    args = parser.parse_args()
    encode(args.source, args.destination, args.width, args.height)
    print(f"[OK] wrote {args.destination} ({args.width}x{args.height}, BC1/DXT1)")


if __name__ == "__main__":
    main()
