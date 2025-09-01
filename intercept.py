"""Estructura con la información de un punto de intersección (ray hit)."""
class Intercept(object):
    def __init__(self, point, normal, distance, rayDirection, obj):
        """
        point: posición 3D del impacto
        normal: normal de la superficie en el punto
        distance: distancia desde el origen del rayo
        rayDirection: dirección del rayo (normalizada)
        obj: objeto interceptado
        """
        self.point = point
        self.normal = normal
        self.distance = distance
        self.rayDirection = rayDirection
        self.obj = obj
        

