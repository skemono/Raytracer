"""Figuras geométricas del raytracer (actualmente: esfera)."""

import numpy as np
from intercept import Intercept

class Shape(object):
    """Base para figuras; define la interfaz de intersección."""
    def __init__(self, position, material):
        self.position = position
        self.material = material
        self.type = "None"

    def ray_intersect(self, orig, dir):
        return None

class Sphere(Shape):
    """Esfera definida por centro (position) y radio."""
    def __init__(self, position, radius, material):
        super().__init__(position, material)
        self.radius = radius
        self.type = "Sphere"
    
    def ray_intersect(self, orig, dir):
        # Asegurarse de trabajar con numpy arrays
        orig = np.array(orig, dtype=float)
        dir = np.array(dir, dtype=float)

    # Normalizar la dirección del rayo
        dir_length = np.linalg.norm(dir)
        if dir_length == 0:
            return None  # Cambié de (False, None) a None
        dir = dir / dir_length  # Normalizar la dirección del rayo

    # Vector del origen del rayo al centro de la esfera
        origin_to_center = np.array(self.position, dtype=float) - orig

    # Proyección de qué tan lejos está el punto más cercano del rayo al centro
        projection_distance = np.dot(origin_to_center, dir)

    # Distancia perpendicular al cuadrado (usando Pitágoras)
        perpendicular_distance_squared = np.dot(origin_to_center, origin_to_center) - projection_distance ** 2
        radius_squared = self.radius * self.radius

    # Si el rayo pasa más lejos que el radio, no hay intersección
        if perpendicular_distance_squared > radius_squared:
            return None  # Cambié de (False, None) a None
        
    # Distancia desde el punto de proyección hasta las intersecciones
        half_chord_distance = np.sqrt(radius_squared - perpendicular_distance_squared)

    # Las 2 distancias de intersección
        near_distance = projection_distance - half_chord_distance
        far_distance = projection_distance + half_chord_distance

        # Elegir la intersección más cercana que esté adelante del origen
        epsilon = 1e-6
        if near_distance > epsilon:
            # Calcular punto de impacto y normal
            hit_point = orig + dir * near_distance
            normal = (hit_point - np.array(self.position)) / self.radius
            # Devolver Intercept con toda la info
            return Intercept(hit_point, normal, near_distance, dir, self)
    
        if far_distance > epsilon:
            # Lo mismo para la intersección lejana
            hit_point = orig + dir * far_distance
            normal = (hit_point - np.array(self.position)) / self.radius
            return Intercept(hit_point, normal, far_distance, dir, self)
        
        # Ambas están detrás del origen
        return None  # Cambié de (False, None) a None