"""Estructura con la información de un punto de intersección (ray hit)."""
class Intercept(object):
    def __init__(self, point, normal, distance, rayDirection, obj, uv=None, tangent=None, bitangent=None):
        """
        point: posición 3D del impacto
        normal: normal de la superficie en el punto (mundo)
        distance: distancia desde el origen del rayo
        rayDirection: dirección del rayo (normalizada)
        obj: objeto interceptado
        uv: coordenadas de textura (u,v) en [0,1] o None
        tangent/bitangent: vectores T/B en espacio mundo para normal mapping (opcional)
        """
        self.point = point
        self.normal = normal
        self.distance = distance
        self.rayDirection = rayDirection
        self.obj = obj
        self.uv = uv
        self.tangent = tangent
        self.bitangent = bitangent
        

