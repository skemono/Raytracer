"""Lectura sencilla de texturas BMP (24 bits) para mapear colores."""

import struct
from typing import List


class BMPTexture(object):
    def __init__(self, filename: str):
        # Abrir el archivo en modo binario y leer cabeceras básicas del BMP
        with open(filename, "rb") as image:
            image.seek(10)
            headerSize = struct.unpack("=l", image.read(4))[0]
            image.seek(18)
            self.width = struct.unpack("=l", image.read(4))[0]
            self.height = struct.unpack("=l", image.read(4))[0]
            image.seek(headerSize)

            # Leer los píxeles fila por fila en formato BGR y normalizarlos a [0,1]
            self.pixels: List[List[list[float]]] = []
            for y in range(self.height):
                pixelRow = []
                for x in range(self.width):
                    b = ord(image.read(1)) / 255
                    g = ord(image.read(1)) / 255
                    r = ord(image.read(1)) / 255
                    pixelRow.append([r, g, b])
                self.pixels.append(pixelRow)

    def getColor(self, u: float, v: float) -> list[float]:
        """
        Obtiene el color en coordenadas UV [0,1]. Devuelve [r,g,b] en [0,1].
        """
        # Limitar UV al rango [0,1]
        u = max(0, min(1, u))
        v = max(0, min(1, v))

        # Convertir a coordenadas de píxel (enteras)
        x = int(u * (self.width - 1))
        y = int(v * (self.height - 1))

        # Asegurar límites válidos
        x = max(0, min(self.width - 1, x))
        y = max(0, min(self.height - 1, y))

        return self.pixels[y][x]
