"""Generic image texture loader with bilinear sampling using Pillow.

Supports common formats: PNG, JPG/JPEG, BMP, WEBP, etc.

API is compatible with Material.diffuseTexture: must implement getColor(u,v)->[r,g,b].
"""

from __future__ import annotations

from typing import List, Optional
import os

try:
    from PIL import Image  # type: ignore
except Exception as _e:
    Image = None  # Lazy failure; we raise when trying to load


class ImageTexture:
    def __init__(self, filename: str):
        if Image is None:
            raise ImportError(
                "Pillow is required for ImageTexture. Install with: pip install pillow"
            )
        if not os.path.isfile(filename):
            raise FileNotFoundError(filename)
        img = Image.open(filename).convert("RGB")
        # Ensure top-left is row 0; PIL already uses top-left origin
        self.width, self.height = img.size
        # Load as list of rows of float rgb [0-1]
        # Using getdata is memory efficient; then reshape
        data = list(img.getdata())  # [(r,g,b), ...] row-major top-to-bottom
        rows: List[List[list[float]]] = []
        it = iter(data)
        for _ in range(self.height):
            row: List[list[float]] = []
            for _ in range(self.width):
                r, g, b = next(it)
                row.append([r/255.0, g/255.0, b/255.0])
            rows.append(row)
        self.pixels = rows

    def getColor(self, u: float, v: float) -> list[float]:
        # Clamp UV
        u = 0.0 if u < 0.0 else (1.0 if u > 1.0 else u)
        v = 0.0 if v < 0.0 else (1.0 if v > 1.0 else v)

        # Bilinear sampling
        x = u * (self.width - 1)
        y = v * (self.height - 1)

        x0 = int(x)
        y0 = int(y)
        x1 = min(x0 + 1, self.width - 1)
        y1 = min(y0 + 1, self.height - 1)

        dx = x - x0
        dy = y - y0

        c00 = self.pixels[y0][x0]
        c10 = self.pixels[y0][x1]
        c01 = self.pixels[y1][x0]
        c11 = self.pixels[y1][x1]

        def lerp(a, b, t):
            return a + (b - a) * t

        c0 = [lerp(c00[i], c10[i], dx) for i in range(3)]
        c1 = [lerp(c01[i], c11[i], dx) for i in range(3)]
        c = [lerp(c0[i], c1[i], dy) for i in range(3)]
        return c


def load_texture_any(paths: list[str] | tuple[str, ...]) -> Optional[ImageTexture]:
    """Try to load the first existing path with Pillow. Returns None if none found.

    Example:
      load_texture_any(["rock.png", "rock.jpg", "rock.bmp"]) -> ImageTexture or None
    """
    if Image is None:
        # Pillow not installed; cannot load PNG/JPG
        print("Pillow is required for image textures.")
        return None
    for p in paths:
        print(f"Checking texture: {p}")
        if os.path.isfile(p):
            print(f"Loading texture: {p}")
            try:
                return ImageTexture(p)
            except Exception:
                pass
    return None
