#!/usr/bin/env python3
"""Generate a 1024x1024 Formint POS app-icon source PNG (stdlib only).

Design: dark slate rounded square with a subtle diagonal gradient, a mint
"F" monogram bar, and anti-aliasing via 4x supersampling + box downsample.

Usage: python3 scripts/make-tauri-icon.py [output.png]
"""
import struct
import sys
import zlib

OUT = sys.argv[1] if len(sys.argv) > 1 else "src-tauri/icons/app-icon.png"

SIZE = 1024
SS = 2  # supersample factor
W = H = SIZE * SS


def rounded_rect_sdf(px, py, cx, cy, w, h, r):
    """Signed-ish distance for rounded rect centered at (cx, cy)."""
    qx = abs(px - cx) - (w / 2 - r)
    qy = abs(py - cy) - (h / 2 - r)
    ax, ay = max(qx, 0.0), max(qy, 0.0)
    outside = (ax * ax + ay * ay) ** 0.5
    inside = min(max(qx, qy), 0.0)
    return outside + inside - r


def lerp(a, b, t):
    return a + (b - a) * t


def draw_bg(px, py):
    """Dark slate rounded square with diagonal gradient."""
    d = rounded_rect_sdf(px, py, W / 2, H / 2, W * 0.94, H * 0.94, W * 0.21)
    if d > 0:
        return (0, 0, 0, 0)  # transparent
    t = ((px / W) + (py / H)) / 2
    r = int(lerp(30, 11, t))
    g = int(lerp(36, 15, t))
    b = int(lerp(50, 23, t))
    return (r, g, b, 255)


def draw_f(px, py):
    """Mint 'F' monogram drawn from three rounded bars."""
    bars = [
        (0.315, 0.245, 0.125, 0.560, 0.062),  # vertical stem
        (0.315, 0.245, 0.370, 0.130, 0.062),  # top bar
        (0.315, 0.470, 0.290, 0.110, 0.062),  # middle bar
    ]
    for cx, cy, w, h, r in bars:
        d = rounded_rect_sdf(px, py, W * cx, H * cy, W * w, H * h, W * r)
        if d <= 0:
            return (56, 240, 192, 255)  # mint
    return None


# Supersampled raster
rows = []
for py in range(H):
    row = bytearray()
    for px in range(W):
        bg = draw_bg(px, py)
        if bg[3] == 0:
            row += b"\x00\x00\x00\x00"
            continue
        f = draw_f(px, py)
        if f is not None:
            row += bytes(f)
        else:
            row += bytes(bg)
    rows.append(bytes(row))

# Box downsample SS -> 1
def downsample(rows, n, size):
    out = []
    for y in range(size):
        row = bytearray()
        for x in range(size):
            rs = gs = bs = as_ = 0
            for dy in range(n):
                src = rows[y * n + dy]
                for dx in range(n):
                    i = (x * n + dx) * 4
                    rs += src[i]
                    gs += src[i + 1]
                    bs += src[i + 2]
                    as_ += src[i + 3]
            total = n * n
            row += bytes((rs // total, gs // total, bs // total, as_ // total))
        out.append(bytes(row))
    return out

final_rows = downsample(rows, SS, SIZE)

# Encode PNG (RGBA, 8-bit)
raw = b"".join(b"\x00" + r for r in final_rows)


def chunk(tag, data):
    c = tag + data
    return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c))


png = b"\x89PNG\r\n\x1a\n"
png += chunk(b"IHDR", struct.pack(">IIBBBBB", SIZE, SIZE, 8, 6, 0, 0, 0))
png += chunk(b"IDAT", zlib.compress(raw, 9))
png += chunk(b"IEND", b"")

with open(OUT, "wb") as fh:
    fh.write(png)
print(f"wrote {OUT} ({SIZE}x{SIZE})")
