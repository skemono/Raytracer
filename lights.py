"""Luces para el raytracer (ambiente y direccional)."""

import numpy as np

class Light(object):
    """Luz base con color, intensidad y tipo."""
    def __init__(self, color = [1, 1, 1], intensity = 1.0, lightType = "None"):
        self.color = color
        self.intensity = intensity
        self.type = lightType

    
    def GetLightColor(self, intercept = None):
        """Color de la luz modulado por la intensidad."""
        return [(i * self.intensity) for i in self.color]

class AmbientLight(Light):
    """Luz ambiente uniforme que afecta toda la escena por igual."""
    def __init__(self, color = [1, 1, 1], intensity = 0.1):
        super().__init__(color, intensity, "Ambient")

class DirectionalLight(Light):
    """Luz direccional con una dirección infinita (como el sol)."""
    def __init__(self, color = [1, 1, 1], intensity = 1.0, direction = [0,  -1, 0]):
        super().__init__(color, intensity, "Directional")
        # Asegurar vector numpy normalizado
        d = np.array(direction, dtype=float)
        norm = np.linalg.norm(d)
        self.direction = (d / norm) if norm != 0 else d

    def GetLightColor(self, intercept = None):
        """Color de luz en el punto, considerando la normal (difuso Lambert)."""
        lightColor = super().GetLightColor()

        if intercept is not None:
            # SurfaceIntensity = NORMAL · (-DIRECCION DE LA LUZ)
            dir_vec = -self.direction
            surfaceIntensity = float(np.dot(intercept.normal, dir_vec))
            surfaceIntensity = max(0.0, min(1.0, surfaceIntensity))
            lightColor = [(i * surfaceIntensity) for i in lightColor]

        return lightColor