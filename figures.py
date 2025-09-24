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


class Plane(Shape):
    """Plano infinito definido por un punto (position) y una normal (normal)."""
    def __init__(self, position, normal, material):
        super().__init__(position, material)
        n = np.array(normal, dtype=float)
        ln = np.linalg.norm(n)
        self.normal = n / ln if ln != 0 else n
        self.type = "Plane"

    def ray_intersect(self, orig, dir):
        orig = np.array(orig, dtype=float)
        dir = np.array(dir, dtype=float)
        denom = np.dot(self.normal, dir)
        if abs(denom) < 1e-6:
            return None
        t = np.dot(self.normal, np.array(self.position) - orig) / denom
        if t < 1e-4:
            return None
        hit_point = orig + dir * t
        return Intercept(hit_point, self.normal, t, dir, self)


class Disk(Shape):
    """Disco finito: plano con radio."""
    def __init__(self, position, normal, radius, material):
        super().__init__(position, material)
        n = np.array(normal, dtype=float)
        ln = np.linalg.norm(n)
        self.normal = n / ln if ln != 0 else n
        self.radius = radius
        self.type = "Disk"

    def ray_intersect(self, orig, dir):
        orig = np.array(orig, dtype=float)
        dir = np.array(dir, dtype=float)
        denom = np.dot(self.normal, dir)
        if abs(denom) < 1e-6:
            return None
        t = np.dot(self.normal, np.array(self.position) - orig) / denom
        if t < 1e-4:
            return None
        hit_point = orig + dir * t
        # Comprobar dentro del radio
        if np.linalg.norm(hit_point - np.array(self.position)) > self.radius:
            return None
        return Intercept(hit_point, self.normal, t, dir, self)


class Triangle(Shape):
    """Triángulo definido por 3 vértices (v0,v1,v2). Intersección Möller-Trumbore."""
    def __init__(self, v0, v1, v2, material):
        # position = centro (promedio) solo informativo
        centroid = [(v0[i] + v1[i] + v2[i]) / 3.0 for i in range(3)]
        super().__init__(centroid, material)
        self.v0 = np.array(v0, dtype=float)
        self.v1 = np.array(v1, dtype=float)
        self.v2 = np.array(v2, dtype=float)
        # Normal (no normalizada -> luego normalizo)
        n = np.cross(self.v1 - self.v0, self.v2 - self.v0)
        ln = np.linalg.norm(n)
        self.normal = n / ln if ln != 0 else n
        self.type = "Triangle"

    def ray_intersect(self, orig, dir):
        orig = np.array(orig, dtype=float)
        dir = np.array(dir, dtype=float)
        # Möller-Trumbore
        EPS = 1e-6
        edge1 = self.v1 - self.v0
        edge2 = self.v2 - self.v0
        h = np.cross(dir, edge2)
        a = np.dot(edge1, h)
        if -EPS < a < EPS:
            return None
        f = 1.0 / a
        s = orig - self.v0
        u = f * np.dot(s, h)
        if u < 0.0 or u > 1.0:
            return None
        q = np.cross(s, edge1)
        v = f * np.dot(dir, q)
        if v < 0.0 or u + v > 1.0:
            return None
        t = f * np.dot(edge2, q)
        if t > EPS:
            hit_point = orig + dir * t
            return Intercept(hit_point, self.normal, t, dir, self)
        return None


class Cube(Shape):
    """Cubo axis-aligned (AABB) definido por centro (position) y tamaño (edge)."""
    def __init__(self, position, edge, material):
        super().__init__(position, material)
        self.edge = edge
        self.type = "Cube"
        e = edge / 2.0
        self.min = np.array([position[0]-e, position[1]-e, position[2]-e], dtype=float)
        self.max = np.array([position[0]+e, position[1]+e, position[2]+e], dtype=float)

    def ray_intersect(self, orig, dir):
        orig = np.array(orig, dtype=float)
        dir = np.array(dir, dtype=float)
        # Evitar división por cero usando números grandes
        inv_dir = 1.0 / np.where(np.abs(dir) < 1e-8, 1e-8, dir)
        t1 = (self.min - orig) * inv_dir
        t2 = (self.max - orig) * inv_dir
        tmin = np.maximum.reduce(np.minimum(t1, t2))
        tmax = np.minimum.reduce(np.maximum(t1, t2))
        if tmax < 0 or tmin > tmax:
            return None
        t = tmin if tmin > 1e-4 else tmax
        if t < 1e-4:
            return None
        hit_point = orig + dir * t
        # Calcular normal de la cara golpeada
        normal = np.zeros(3)
        # Comparar hit_point cercano a límites
        EPS = 1e-4
        for axis in range(3):
            if abs(hit_point[axis] - self.min[axis]) < EPS:
                normal[axis] = -1
                break
            if abs(hit_point[axis] - self.max[axis]) < EPS:
                normal[axis] = 1
                break
        ln = np.linalg.norm(normal)
        if ln == 0:
            # fallback: usar gradiente (distancias a centros)
            extents = (self.max - self.min) / 2.0
            center = (self.max + self.min) / 2.0
            local = (hit_point - center) / (extents + 1e-8)
            axis = np.argmax(np.abs(local))
            normal = np.zeros(3)
            normal[axis] = np.sign(local[axis])
        return Intercept(hit_point, normal, t, dir, self)