"""Figuras geométricas del raytracer (actualmente: esfera)."""

import numpy as np

# Grados a radianes (uno o tres valores)
def deg(ax, ay=None, az=None):
        if ay is None and az is None:
                return (np.radians(ax), 0.0, 0.0)
        return (np.radians(ax), np.radians(ay or 0.0), np.radians(az or 0.0))
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
            # UV esféricas: u = atan2(z,x)/(2pi)+0.5, v = asin(y/r)/pi + 0.5
            local = hit_point - np.array(self.position)
            u = (np.arctan2(local[2], local[0]) / (2*np.pi)) + 0.5
            v = (np.arcsin(np.clip(local[1] / self.radius, -1.0, 1.0)) / np.pi) + 0.5
            return Intercept(hit_point, normal, near_distance, dir, self, uv=(float(u), float(v)))
    
        if far_distance > epsilon:
            # Lo mismo para la intersección lejana
            hit_point = orig + dir * far_distance
            normal = (hit_point - np.array(self.position)) / self.radius
            local = hit_point - np.array(self.position)
            u = (np.arctan2(local[2], local[0]) / (2*np.pi)) + 0.5
            v = (np.arcsin(np.clip(local[1] / self.radius, -1.0, 1.0)) / np.pi) + 0.5
            return Intercept(hit_point, normal, far_distance, dir, self, uv=(float(u), float(v)))
        
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
        # Planar UVs: project to plane axes; build tangent basis from normal
        # Choose major axis for stable parameterization
        n = self.normal
        # Find an arbitrary tangent not parallel to n
        ref = np.array([1,0,0]) if abs(n[0]) < 0.9 else np.array([0,1,0])
        tangent = np.cross(ref, n)
        tangent /= (np.linalg.norm(tangent) + 1e-12)
        bitangent = np.cross(n, tangent)
        # Compute local coords
        local = hit_point - np.array(self.position)
        u = float(np.dot(local, tangent))
        v = float(np.dot(local, bitangent))
        # Tile by fractional part to [0,1]
        u = u - np.floor(u)
        v = v - np.floor(v)
        return Intercept(hit_point, self.normal, t, dir, self, uv=(u, v), tangent=tangent, bitangent=bitangent)


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
        # Polar UV mapping on disk
        local = hit_point - np.array(self.position)
        angle = np.arctan2(local[2], local[0])
        u = (angle / (2*np.pi)) + 0.5
        r = min(1.0, np.linalg.norm([local[0], local[2]]) / max(1e-8, self.radius))
        v = r
        # Tangent basis
        n = self.normal
        ref = np.array([1,0,0]) if abs(n[0]) < 0.9 else np.array([0,1,0])
        tangent = np.cross(ref, n); tangent /= (np.linalg.norm(tangent)+1e-12)
        bitangent = np.cross(n, tangent)
        return Intercept(hit_point, self.normal, t, dir, self, uv=(float(u), float(v)), tangent=tangent, bitangent=bitangent)


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


class OrientedBox(Shape):
    """Caja orientada arbitrariamente (OBB) definida por centro, half_sizes y rotación Euler.
    Se intersecta transformando el rayo al espacio local (donde es un AABB) y luego regresando.
    rot = (rx, ry, rz) en radianes.
    """
    def __init__(self, position, half_sizes, rotation, material):
        super().__init__(position, material)
        self.type = "OrientedBox"
        self.half = np.array(half_sizes, dtype=float)
        self.rotation = rotation  # Euler angles
        # Precompute rotation matrix (R = Rz * Ry * Rx)
        rx, ry, rz = rotation
        cx, sx = np.cos(rx), np.sin(rx)
        cy, sy = np.cos(ry), np.sin(ry)
        cz, sz = np.cos(rz), np.sin(rz)
        Rx = np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]])
        Ry = np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]])
        Rz = np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]])
        self.R = Rz @ Ry @ Rx
        self.RT = self.R.T

    def ray_intersect(self, orig, dir):
        orig = np.array(orig, dtype=float)
        dir = np.array(dir, dtype=float)
        # Transform ray to local space
        local_orig = self.RT @ (orig - np.array(self.position))
        local_dir = self.RT @ dir
        # Intersect with AABB [-half, half]
        inv_dir = 1.0 / np.where(np.abs(local_dir) < 1e-8, 1e-8, local_dir)
        t1 = (-self.half - local_orig) * inv_dir
        t2 = ( self.half - local_orig) * inv_dir
        tmin = np.maximum.reduce(np.minimum(t1, t2))
        tmax = np.minimum.reduce(np.maximum(t1, t2))
        if tmax < 0 or tmin > tmax:
            return None
        t = tmin if tmin > 1e-4 else tmax
        if t < 1e-4:
            return None
        # Hit point in local
        local_hit = local_orig + local_dir * t
        # Determine normal in local
        EPS = 1e-4
        normal_local = np.zeros(3)
        for axis in range(3):
            if abs(local_hit[axis] - self.half[axis]) < EPS:
                normal_local[axis] = 1
                break
            if abs(local_hit[axis] + self.half[axis]) < EPS:
                normal_local[axis] = -1
                break
        if np.linalg.norm(normal_local) == 0:
            # fallback choose dominant axis
            axis = np.argmax(np.abs(local_hit) / (self.half + 1e-8))
            normal_local[axis] = np.sign(local_hit[axis])
        # Transform back
        world_hit = self.R @ local_hit + np.array(self.position)
        world_normal = self.R @ normal_local
        world_normal /= (np.linalg.norm(world_normal) + 1e-12)
        # Simple box UVs: project to dominant axis normal in local space
        # Recompute hit face in local to assign UVs
        # Note: we already have local_hit
        # Build local tangent/bitangent based on face axis
        axis = np.argmax(np.abs(normal_local))
        if axis == 0:
            # +/-X face: use Y,Z
            u = (local_hit[2] / (2*self.half[2])) + 0.5
            v = (local_hit[1] / (2*self.half[1])) + 0.5
            t_local = np.array([0,0,1]); b_local = np.array([0,1,0])
        elif axis == 1:
            # +/-Y face: use X,Z
            u = (local_hit[0] / (2*self.half[0])) + 0.5
            v = (local_hit[2] / (2*self.half[2])) + 0.5
            t_local = np.array([1,0,0]); b_local = np.array([0,0,1])
        else:
            # +/-Z face: use X,Y
            u = (local_hit[0] / (2*self.half[0])) + 0.5
            v = (local_hit[1] / (2*self.half[1])) + 0.5
            t_local = np.array([1,0,0]); b_local = np.array([0,1,0])
        # Transform T/B to world
        tangent = self.R @ t_local
        bitangent = self.R @ b_local
        return Intercept(world_hit, world_normal, t, dir, self, uv=(float(u), float(v)), tangent=tangent, bitangent=bitangent)


class Ellipsoid(Shape):
    """Elipsoide (radii) con rotación Euler opcional."""
    def __init__(self, position, radii, material, rotation=None):
        super().__init__(position, material)
        self.type = "Ellipsoid"
        self.radii = np.array(radii, dtype=float)
        self.inv = 1.0 / np.where(self.radii < 1e-8, 1e-8, self.radii)
        if rotation is None:
            self.rotation = (0.0,0.0,0.0)
            self.R = np.eye(3)
            self.RT = self.R
        else:
            self.rotation = rotation
            rx, ry, rz = rotation
            cx, sx = np.cos(rx), np.sin(rx)
            cy, sy = np.cos(ry), np.sin(ry)
            cz, sz = np.cos(rz), np.sin(rz)
            Rx = np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]])
            Ry = np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]])
            Rz = np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]])
            self.R = Rz @ Ry @ Rx
            self.RT = self.R.T

    def ray_intersect(self, orig, dir):
        orig = np.array(orig, dtype=float)
        dir = np.array(dir, dtype=float)
        # Transformar a espacio local rotado
        local_orig = self.RT @ (orig - np.array(self.position))
        local_dir = self.RT @ dir
        # Escalar a esfera unitaria
        o = local_orig * self.inv
        d = local_dir * self.inv
        a = np.dot(d, d)
        b = 2.0 * np.dot(o, d)
        c = np.dot(o, o) - 1.0
        disc = b*b - 4*a*c
        if disc < 0:
            return None
        sqrt_disc = np.sqrt(disc)
        t0 = (-b - sqrt_disc) / (2*a)
        t1 = (-b + sqrt_disc) / (2*a)
        EPS = 1e-4
        t = t0 if t0 > EPS else (t1 if t1 > EPS else None)
        if t is None:
            return None
        # Punto de impacto en espacio local rotado
        local_hit = local_orig + local_dir * t
        # Normal local (derivada implícita)
        local_normal = (local_hit * (self.inv * self.inv))
        ln = np.linalg.norm(local_normal)
        if ln == 0:
            return None
        local_normal /= ln
        # Volver a espacio mundo
        world_hit = self.R @ local_hit + np.array(self.position)
        world_normal = self.R @ local_normal
        world_normal /= (np.linalg.norm(world_normal) + 1e-12)
        # Spherical-like UVs using local_hit and radii
        local = local_hit
        # Normalize to unit sphere space
        p = local / (self.radii + 1e-12)
        u = (np.arctan2(p[2], p[0]) / (2*np.pi)) + 0.5
        v = (np.arcsin(np.clip(p[1], -1.0, 1.0)) / np.pi) + 0.5
        # Approximate tangent basis from world_normal
        n = world_normal
        ref = np.array([1,0,0]) if abs(n[0]) < 0.9 else np.array([0,1,0])
        tangent = np.cross(ref, n); tangent /= (np.linalg.norm(tangent)+1e-12)
        bitangent = np.cross(n, tangent)
        return Intercept(world_hit, world_normal, t, dir, self, uv=(float(u), float(v)), tangent=tangent, bitangent=bitangent)


class ChickenLeg(Shape):
    """Figura compuesta 'pierna de pollo':
    - 'Carne': elipsoide grande.
    - 'Hueso': dos esferas pequeñas unidas por un cilindro aproximado (usamos cápsula simplificada).
    Intersección: probamos cada sub-parte y devolvemos la más cercana.
    """
    def __init__(self, position, material_meat, material_bone=None,
                 meat_radii=(1.0,0.8,1.2), bone_radius=0.25, bone_length=1.4):
        super().__init__(position, material_meat)
        self.type = "ChickenLeg"
        self.material_meat = material_meat
        self.material_bone = material_bone or material_meat
        self.meat = Ellipsoid(position, meat_radii, material_meat)
        # Model bone as a capsule along +X starting partially embedded
        self.bone_center_a = np.array(position) + np.array([meat_radii[0]*0.4, 0, 0])
        self.bone_center_b = self.bone_center_a + np.array([bone_length, 0, 0])
        self.bone_radius = bone_radius

    def _ray_capsule(self, orig, dir, a, b, radius):
        # Capsule = segment extruded sphere radius
        # Algorithm: project to segment, solve quadratic vs infinite cylinder, clamp.
        pa = a; pb = b
        ba = pb - pa
        oa = orig - pa
        baba = np.dot(ba, ba)
        bard = np.dot(ba, dir)
        baoa = np.dot(ba, oa)
        r2 = radius * radius
        # Components for quadratic (derived from distance to segment)
        a_coef = baba - bard * bard
        b_coef = baba * np.dot(oa, dir) - baoa * bard
        c_coef = baba * np.dot(oa, oa) - baoa * baoa - r2 * baba
        h = b_coef * b_coef - a_coef * c_coef
        if h >= 0.0:
            h = np.sqrt(h)
            t = (-b_coef - h) / (a_coef + 1e-12)
            # Check if within segment
            y = baoa + t * bard
            if 0.0 <= y <= baba and t > 1e-4:
                hit_point = orig + dir * t
                # Normal: compute closest point on segment then vector
                cp = pa + ba * (y / baba)
                normal = hit_point - cp
                normal /= (np.linalg.norm(normal) + 1e-12)
                return t, hit_point, normal
            # Else caps (spheres)
            for center in (pa, pb):
                oc = orig - center
                b_ = np.dot(oc, dir)
                c_ = np.dot(oc, oc) - r2
                disc = b_*b_ - c_
                if disc >= 0:
                    s = -b_ - np.sqrt(disc)
                    if s > 1e-4:
                        hp = orig + dir * s
                        n = (hp - center) / radius
                        return s, hp, n
        return None

    def ray_intersect(self, orig, dir):
        # Try meat (ellipsoid) and bone (capsule). Return closest.
        orig = np.array(orig, dtype=float)
        dir = np.array(dir, dtype=float)
        best = None
        # Meat
        m_hit = self.meat.ray_intersect(orig, dir)
        if m_hit is not None:
            best = (m_hit.distance, m_hit.point, m_hit.normal, self.material_meat)
        # Bone capsule
        cap = self._ray_capsule(orig, dir, self.bone_center_a, self.bone_center_b, self.bone_radius)
        if cap is not None:
            dist, pt, n = cap
            if best is None or dist < best[0]:
                best = (dist, pt, n, self.material_bone)
        if best is None:
            return None
        # Build intercept; we set material according to sub-part
        intercept = Intercept(best[1], best[2], best[0], dir, self)
        # Override object material temporarily for shading
        self.material = best[3]
        return intercept


class Cylinder(Shape):
    """Cilindro con rotación Euler opcional."""
    def __init__(self, position, radius, height, material, rotation=None):
        super().__init__(position, material)
        self.type = "Cylinder"
        self.radius = float(radius)
        self.height = float(height)
        self.half_h = self.height * 0.5
        self.radius2 = self.radius * self.radius
        if rotation is None:
            self.rotation = (0.0, 0.0, 0.0)
            self.R = np.eye(3)
            self.RT = self.R
        else:
            self.rotation = rotation
            rx, ry, rz = rotation
            cx, sx = np.cos(rx), np.sin(rx)
            cy, sy = np.cos(ry), np.sin(ry)
            cz, sz = np.cos(rz), np.sin(rz)
            Rx = np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]])
            Ry = np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]])
            Rz = np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]])
            # Orden consistente con OrientedBox para uniformidad
            self.R = Rz @ Ry @ Rx
            self.RT = self.R.T

    def ray_intersect(self, orig, dir):
        orig = np.array(orig, dtype=float)
        dir = np.array(dir, dtype=float)
    # Transformar a espacio local
        local_orig = self.RT @ (orig - np.array(self.position))
        local_dir = self.RT @ dir
        dx, dy, dz = local_dir
        ox, oy, oz = local_orig
    # Lateral
        a = dx*dx + dz*dz
        t_side = None
        normal_side_local = None
        if a > 1e-12:
            b = 2*ox*dx + 2*oz*dz
            c = ox*ox + oz*oz - self.radius2
            disc = b*b - 4*a*c
            if disc >= 0:
                sqrt_disc = np.sqrt(disc)
                t0 = (-b - sqrt_disc) / (2*a)
                t1 = (-b + sqrt_disc) / (2*a)
                for t_candidate in [t0, t1]:
                    if t_candidate > 1e-4:
                        y_hit = oy + t_candidate*dy
                        if -self.half_h - 1e-5 <= y_hit <= self.half_h + 1e-5:
                            if t_side is None or t_candidate < t_side:
                                t_side = t_candidate
                if t_side is not None:
                    hit_local = local_orig + local_dir * t_side
                    n = np.array([hit_local[0], 0.0, hit_local[2]])
                    ln = np.linalg.norm(n)
                    if ln > 0:
                        normal_side_local = n / ln
        # Tapas
        t_caps = []
        if abs(dy) > 1e-12:
            # Superior (y=+half_h)
            t_top = (self.half_h - oy) / dy
            if t_top > 1e-4:
                xh = ox + t_top*dx
                zh = oz + t_top*dz
                if xh*xh + zh*zh <= self.radius2 + 1e-6:
                    t_caps.append((t_top, np.array([0,1,0], dtype=float)))
            # Inferior (y=-half_h)
            t_bottom = (-self.half_h - oy) / dy
            if t_bottom > 1e-4:
                xh = ox + t_bottom*dx
                zh = oz + t_bottom*dz
                if xh*xh + zh*zh <= self.radius2 + 1e-6:
                    t_caps.append((t_bottom, np.array([0,-1,0], dtype=float)))
        # Seleccionar intersección
        best_t = None
        best_normal_local = None
        if t_side is not None:
            best_t = t_side
            best_normal_local = normal_side_local
        for t_cap, n_cap in t_caps:
            if (best_t is None or t_cap < best_t) and t_cap > 1e-4:
                best_t = t_cap
                best_normal_local = n_cap
        if best_t is None:
            return None
        local_hit = local_orig + local_dir * best_t
        # Transformar a mundo
        world_hit = self.R @ local_hit + np.array(self.position)
        world_normal = self.R @ best_normal_local
        world_normal /= (np.linalg.norm(world_normal) + 1e-12)
        # UVs: cylindrical mapping on lateral; planar on caps
        # Determine if lateral hit by checking normal's y in local space
        # We have local_hit and best_normal_local
        lateral = abs(best_normal_local[1]) < 1e-6
        if lateral:
            angle = np.arctan2(local_hit[2], local_hit[0])
            u = (angle / (2*np.pi)) + 0.5
            v = (local_hit[1] / (2*self.half_h)) + 0.5
        else:
            # cap: map x,z to [0,1]
            u = (local_hit[0] / (2*self.radius)) + 0.5
            v = (local_hit[2] / (2*self.radius)) + 0.5
        # Tangent basis in world from local axes
        t_local = np.array([1,0,0]) if lateral else np.array([1,0,0])
        b_local = np.array([0,1,0]) if lateral else np.array([0,0,1])
        tangent = self.R @ t_local
        bitangent = self.R @ b_local
        return Intercept(world_hit, world_normal, best_t, dir, self, uv=(float(u), float(v)), tangent=tangent, bitangent=bitangent)
    

class EllipticCylinder(Shape):
    """Elliptical cylinder with radii (rx, rz), height, and optional rotation Euler.
    Lateral equation: (x^2/rx^2) + (z^2/rz^2) = 1, with y in [-h/2, h/2].
    """
    def __init__(self, position, radii_xz, height, material, rotation=None):
        super().__init__(position, material)
        self.type = "EllipticCylinder"
        self.rx = float(radii_xz[0])
        self.rz = float(radii_xz[1])
        self.height = float(height)
        self.half_h = self.height * 0.5
        # Precompute inverse squares for robust math
        self.invx2 = 1.0 / max(1e-12, self.rx * self.rx)
        self.invz2 = 1.0 / max(1e-12, self.rz * self.rz)
        if rotation is None:
            self.rotation = (0.0, 0.0, 0.0)
            self.R = np.eye(3)
            self.RT = self.R
        else:
            self.rotation = rotation
            rx, ry, rz = rotation
            cx, sx = np.cos(rx), np.sin(rx)
            cy, sy = np.cos(ry), np.sin(ry)
            cz, sz = np.cos(rz), np.sin(rz)
            Rx = np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]])
            Ry = np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]])
            Rz = np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]])
            self.R = Rz @ Ry @ Rx
            self.RT = self.R.T

    def ray_intersect(self, orig, dir):
        orig = np.array(orig, dtype=float)
        dir = np.array(dir, dtype=float)
        # Transform to local space
        local_orig = self.RT @ (orig - np.array(self.position))
        local_dir = self.RT @ dir
        dx, dy, dz = local_dir
        ox, oy, oz = local_orig

        # Lateral intersection: a t^2 + b t + c = 0 for ellipse in XZ
        a = dx*dx * self.invx2 + dz*dz * self.invz2
        t_side = None
        normal_side_local = None
        if a > 1e-12:
            b = 2.0 * (ox*dx * self.invx2 + oz*dz * self.invz2)
            c = ox*ox * self.invx2 + oz*oz * self.invz2 - 1.0
            disc = b*b - 4*a*c
            if disc >= 0.0:
                sqrt_disc = np.sqrt(disc)
                t0 = (-b - sqrt_disc) / (2*a)
                t1 = (-b + sqrt_disc) / (2*a)
                for t_candidate in [t0, t1]:
                    if t_candidate > 1e-4:
                        y_hit = oy + t_candidate * dy
                        if -self.half_h - 1e-5 <= y_hit <= self.half_h + 1e-5:
                            if t_side is None or t_candidate < t_side:
                                t_side = t_candidate
                if t_side is not None:
                    hit_local = local_orig + local_dir * t_side
                    nx = hit_local[0] * self.invx2
                    nz = hit_local[2] * self.invz2
                    n = np.array([nx, 0.0, nz], dtype=float)
                    ln = np.linalg.norm(n)
                    if ln > 0:
                        normal_side_local = n / ln

        # Caps at y = +/- half_h
        t_caps = []
        if abs(dy) > 1e-12:
            # Top cap
            t_top = (self.half_h - oy) / dy
            if t_top > 1e-4:
                xh = ox + t_top * dx
                zh = oz + t_top * dz
                if xh*xh * self.invx2 + zh*zh * self.invz2 <= 1.0 + 1e-6:
                    t_caps.append((t_top, np.array([0, 1, 0], dtype=float)))
            # Bottom cap
            t_bottom = (-self.half_h - oy) / dy
            if t_bottom > 1e-4:
                xh = ox + t_bottom * dx
                zh = oz + t_bottom * dz
                if xh*xh * self.invx2 + zh*zh * self.invz2 <= 1.0 + 1e-6:
                    t_caps.append((t_bottom, np.array([0, -1, 0], dtype=float)))

        # Select nearest valid hit
        best_t = None
        best_normal_local = None
        if t_side is not None:
            best_t = t_side
            best_normal_local = normal_side_local
        for t_cap, n_cap in t_caps:
            if (best_t is None or t_cap < best_t) and t_cap > 1e-4:
                best_t = t_cap
                best_normal_local = n_cap
        if best_t is None:
            return None

        local_hit = local_orig + local_dir * best_t
        world_hit = self.R @ local_hit + np.array(self.position)
        world_normal = self.R @ best_normal_local
        world_normal /= (np.linalg.norm(world_normal) + 1e-12)
        # UVs similar to cylinder but account for ellipse: use angle from center and y along height
        angle = np.arctan2(local_hit[2]/max(1e-8,self.rz), local_hit[0]/max(1e-8,self.rx))
        u = (angle / (2*np.pi)) + 0.5
        v = (local_hit[1] / (2*self.half_h)) + 0.5
        # Tangent basis from local axes
        t_local = np.array([1,0,0])
        b_local = np.array([0,1,0])
        tangent = self.R @ t_local
        bitangent = self.R @ b_local
        return Intercept(world_hit, world_normal, best_t, dir, self, uv=(float(u), float(v)), tangent=tangent, bitangent=bitangent)


class Capsule(Shape):
    """Cápsula definida por dos puntos (pa,pb) y un radio: unión de un cilindro y dos semiesferas.
    Intersección basada en distancia a segmento. UVs: u=ángulo alrededor del eje, v=a lo largo del segmento.
    """
    def __init__(self, point_a, point_b, radius, material):
        super().__init__(position=[(point_a[0]+point_b[0])/2.0, (point_a[1]+point_b[1])/2.0, (point_a[2]+point_b[2])/2.0], material=material)
        self.type = "Capsule"
        self.pa = np.array(point_a, dtype=float)
        self.pb = np.array(point_b, dtype=float)
        self.radius = float(radius)
        self.ba = self.pb - self.pa
        self.len2 = float(np.dot(self.ba, self.ba))

    def _intersect_capsule(self, orig, dir):
        pa = self.pa; pb = self.pb
        ba = self.ba
        oa = orig - pa
        baba = np.dot(ba, ba)
        bard = np.dot(ba, dir)
        baoa = np.dot(ba, oa)
        r2 = self.radius * self.radius
        a_coef = baba - bard * bard
        b_coef = baba * np.dot(oa, dir) - baoa * bard
        c_coef = baba * np.dot(oa, oa) - baoa * baoa - r2 * baba
        h = b_coef * b_coef - a_coef * c_coef
        if h >= 0.0:
            h = np.sqrt(h)
            t = (-b_coef - h) / (a_coef + 1e-12)
            y = baoa + t * bard
            if 0.0 <= y <= baba and t > 1e-4:
                hit_point = orig + dir * t
                cp = pa + ba * (y / baba)
                normal = hit_point - cp
                normal /= (np.linalg.norm(normal) + 1e-12)
                return t, hit_point, normal, y
            # Tapas esféricas
            for center in (pa, pb):
                oc = orig - center
                b_ = np.dot(oc, dir)
                c_ = np.dot(oc, oc) - r2
                disc = b_*b_ - c_
                if disc >= 0:
                    s = -b_ - np.sqrt(disc)
                    if s > 1e-4:
                        hp = orig + dir * s
                        n = (hp - center) / self.radius
                        # y en extremos
                        y = 0.0 if center is pa else baba
                        return s, hp, n, y
        return None

    def ray_intersect(self, orig, dir):
        orig = np.array(orig, dtype=float)
        dir = np.array(dir, dtype=float)
        res = self._intersect_capsule(orig, dir)
        if res is None:
            return None
        t, hit, normal, y_along = res
        # UV: construir base ortonormal alrededor del eje
        u_axis = self.ba / (np.linalg.norm(self.ba) + 1e-12)
        ref = np.array([1,0,0]) if abs(u_axis[0]) < 0.9 else np.array([0,1,0])
        t1 = np.cross(u_axis, ref); t1 /= (np.linalg.norm(t1) + 1e-12)
        t2 = np.cross(u_axis, t1)
        cp = self.pa + u_axis * (y_along / (np.linalg.norm(self.ba) + 1e-12)) * np.linalg.norm(self.ba)
        radial = hit - cp
        a = float(np.arctan2(np.dot(radial, t2), np.dot(radial, t1)))
        u = (a / (2*np.pi)) + 0.5
        v = float(np.clip(y_along / (self.len2 ** 0.5 + 1e-12), 0.0, 1.0))
        return Intercept(hit, normal, t, dir, self, uv=(u, v), tangent=t1, bitangent=t2)


class Cone(Shape):
    """Cono recto finito alineado al eje local Y, con radio en la base y altura.
    Base en y = -h/2, vértice en y = +h/2. Admite rotación Euler.
    """
    def __init__(self, position, radius, height, material, rotation=None):
        super().__init__(position, material)
        self.type = "Cone"
        self.radius = float(radius)
        self.height = float(height)
        self.half_h = self.height * 0.5
        self.k = (self.radius / self.height) if self.height != 0 else 0.0  # pendiente
        if rotation is None:
            self.rotation = (0.0, 0.0, 0.0)
            self.R = np.eye(3)
            self.RT = self.R
        else:
            self.rotation = rotation
            rx, ry, rz = rotation
            cx, sx = np.cos(rx), np.sin(rx)
            cy, sy = np.cos(ry), np.sin(ry)
            cz, sz = np.cos(rz), np.sin(rz)
            Rx = np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]])
            Ry = np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]])
            Rz = np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]])
            self.R = Rz @ Ry @ Rx
            self.RT = self.R.T

    def ray_intersect(self, orig, dir):
        orig = np.array(orig, dtype=float)
        dir = np.array(dir, dtype=float)
        # Transformar a espacio local del cono
        local_o = self.RT @ (orig - np.array(self.position))
        local_d = self.RT @ dir
        ox, oy, oz = local_o
        dx, dy, dz = local_d
        # Ecuación lateral: x^2 + z^2 = (k*(y - y_apex))^2, y_apex = +half_h
        y_apex = self.half_h
        k2 = self.k * self.k
        A = dx*dx + dz*dz - k2 * dy*dy
        B = 2*(ox*dx + oz*dz - k2 * ( (oy - y_apex) * dy ))
        C = ox*ox + oz*oz - k2 * (oy - y_apex) * (oy - y_apex)
        t_lateral = None
        if abs(A) > 1e-12:
            disc = B*B - 4*A*C
            if disc >= 0:
                sqrt_disc = np.sqrt(disc)
                t0 = (-B - sqrt_disc) / (2*A)
                t1 = (-B + sqrt_disc) / (2*A)
                for tc in [t0, t1]:
                    if tc > 1e-4:
                        y_hit = oy + tc*dy
                        if -self.half_h - 1e-5 <= y_hit <= self.half_h + 1e-5:
                            if t_lateral is None or tc < t_lateral:
                                t_lateral = tc
        # Tapa base (círculo) en y = -half_h
        t_cap = None
        if abs(dy) > 1e-12:
            tc = (-self.half_h - oy) / dy
            if tc > 1e-4:
                xh = ox + tc*dx
                zh = oz + tc*dz
                if xh*xh + zh*zh <= self.radius*self.radius + 1e-6:
                    t_cap = tc
        # Elegir la más cercana
        t = None
        hit_local = None
        normal_local = None
        if t_lateral is not None:
            t = t_lateral
            hit_local = local_o + local_d * t
            q = hit_local[1] - y_apex
            n = np.array([hit_local[0], -k2 * q, hit_local[2]], dtype=float)
            ln = np.linalg.norm(n)
            normal_local = n / (ln + 1e-12)
        if t_cap is not None and (t is None or t_cap < t):
            t = t_cap
            hit_local = local_o + local_d * t
            normal_local = np.array([0.0, 1.0, 0.0])  # normal hacia arriba en la base
        if t is None:
            return None
        # Transformar a mundo
        hit_world = self.R @ hit_local + np.array(self.position)
        normal_world = self.R @ normal_local
        normal_world /= (np.linalg.norm(normal_world) + 1e-12)
        # UV cilíndricas
        u = (np.arctan2(hit_local[2], hit_local[0]) / (2*np.pi)) + 0.5
        v = (hit_local[1] + self.half_h) / (self.height + 1e-12)
        # Base T/B aproximadas
        ref = np.array([1,0,0]) if abs(normal_world[0]) < 0.9 else np.array([0,1,0])
        tangent = np.cross(ref, normal_world); tangent /= (np.linalg.norm(tangent)+1e-12)
        bitangent = np.cross(normal_world, tangent)
        return Intercept(hit_world, normal_world, t, dir, self, uv=(float(u), float(v)), tangent=tangent, bitangent=bitangent)

