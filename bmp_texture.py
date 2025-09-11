"""Lectura de texturas BMP (24 bits) con padding y orientación correcta.

- Soporta filas con padding a múltiplos de 4 bytes.
- Reordena la imagen a top-to-bottom si el BMP está en bottom-up.
- getColor aplica muestreo bilineal para mejor calidad.
"""

import struct
from typing import List


class BMPTexture(object):
    def __init__(self, filename: str):
        with open(filename, "rb") as image:
            image.seek(10)
            headerSize = struct.unpack("=l", image.read(4))[0]
            image.seek(18)
            self.width = struct.unpack("=l", image.read(4))[0]
            height_raw = struct.unpack("=l", image.read(4))[0]
            top_down = height_raw < 0
            self.height = abs(height_raw)
            image.seek(headerSize)

            row_padding = (4 - (self.width * 3) % 4) % 4
            rows: List[List[list[float]]] = []
            for _ in range(self.height):
                pixelRow: List[list[float]] = []
                for _ in range(self.width):
                    b = image.read(1)[0] / 255
                    g = image.read(1)[0] / 255
                    r = image.read(1)[0] / 255
                    pixelRow.append([r, g, b])
                if row_padding:
                    image.read(row_padding)
                rows.append(pixelRow)

            # BMP bottom-up (height > 0) => primera fila leída es la inferior.
            # Queremos self.pixels[0] = fila superior.
            if not top_down:
                rows.reverse()

            self.pixels = rows

    def getColor(self, u: float, v: float) -> list[float]:
        # Clamp UV
        u = max(0.0, min(1.0, u))
        v = max(0.0, min(1.0, v))

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
