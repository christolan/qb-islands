#!/usr/bin/env python3
"""Generate the extension icons (pure stdlib, no PIL)."""
import struct
import zlib

SIZE = 128


def rounded_rect_mask(x, y, size, radius):
    if radius <= 0:
        return True
    cx = min(x, size - 1 - x)
    cy = min(y, size - 1 - y)
    if cx >= radius or cy >= radius:
        return True
    dx, dy = radius - cx, radius - cy
    return dx * dx + dy * dy <= radius * radius


def render(scale):
    size = SIZE * scale
    px = [[(0, 0, 0, 0)] * size for _ in range(size)]
    bg = (22, 26, 35, 255)
    green = (77, 208, 127, 255)
    blue = (85, 168, 255, 255)

    def put(x, y, color):
        if 0 <= x < size and 0 <= y < size:
            px[y][x] = color

    def rect(x0, y0, x1, y1, color):
        for y in range(y0 * scale, (y1 + 1) * scale):
            for x in range(x0 * scale, (x1 + 1) * scale):
                put(x, y, color)

    def tri_down(cx, top, half_w, height, color):
        for row in range(height * scale):
            y = top * scale + row
            spread = half_w * row / (height * scale)
            for x in range(int((cx - spread) * scale), int((cx + spread) * scale) + 1):
                put(x, y, color)

    def tri_up(cx, bottom, half_w, height, color):
        for row in range(height * scale):
            y = bottom * scale - 1 - row
            spread = half_w * row / (height * scale)
            for x in range(int((cx - spread) * scale), int((cx + spread) * scale) + 1):
                put(x, y, color)

    radius = 28
    for y in range(size):
        for x in range(size):
            if rounded_rect_mask(x // scale, y // scale, SIZE, radius):
                put(x, y, bg)

    # Left: green download arrow.
    rect(38, 34, 50, 70, green)
    tri_down(44, 64, 30, 34, green)
    # Right: blue upload arrow.
    rect(78, 58, 90, 94, blue)
    tri_up(84, 64, 30, 34, blue)

    return px


def write_png(path, px):
    height = len(px)
    width = len(px[0])
    raw = b""
    for row in px:
        raw += b"\x00" + b"".join(struct.pack("4B", *p) for p in row)

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")
    with open(path, "wb") as fh:
        fh.write(png)
    print(f"wrote {path} ({width}x{height})")


def downscale(px, factor):
    out = []
    for y in range(0, len(px), factor):
        row = px[y][::factor]
        out.append(row)
    return out


def main():
    import os

    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "icons")
    out_dir = os.path.normpath(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    for target in (16, 32, 48, 128):
        # Render large enough that every target size divides evenly.
        px = render(12)
        px = downscale(px, (SIZE * 12) // target)
        write_png(os.path.join(out_dir, f"icon{target}.png"), px)


if __name__ == "__main__":
    main()
