"""Motor mínimo de raster/ray casting para el raytracer."""

import numpy as np
from math import isclose, floor, pi, tan
from camera import Camera
import pygame
from lights import *
import random

class Renderer(object):
    """Encapsula viewport, buffers y el trazado de rayos básico."""
    def __init__(self, screen):
        self.screen = screen
        _, _, self.width, self.height = screen.get_rect()

        self.camera = Camera()
        self.glViewport(0, 0, self.width, self.height)
        self.glProjection()

        self.glColor(1, 1, 1)
        self.glClearColor(0, 0, 0)

        self.glClear()

        # Escena y luces
        self.scene = []
        self.lights = []

        # Environment map y recursión para reflejos/refracciones
        self.environmentMap = None
        self.maxDepth = 3
        # Controles de orientación/escala del environment map
        self.envYaw = 0.0     # rotación horizontal (radianes)
        self.envPitch = 0.0   # rotación vertical (radianes)
        self.envFovScale = 0.4 

    
    def glViewport(self, x, y, width, height):
        self.vpX = round(x)
        self.vpY = round(y)
        self.vpWidth = width
        self.vpHeight = height

        self.viewportMatrix = np.matrix([[width/2, 0, 0, x + width/2],
                                         [0, height/2, 0, y + height/2],
                                         [0, 0, 0.5, 0.5],
                                         [0, 0, 0, 1]])
    
    def glProjection(self, n = 0.1, f = 1000, fov = 60):
        aspectRatio = self.vpWidth / self.vpHeight
        fov *= pi/180
        self.topEdge = tan(fov/2) * n
        self.rightEdge = self.topEdge * aspectRatio

        self.nearPlane = n

        self.projectionMatrix = np.matrix([[n/self.rightEdge, 0, 0, 0],
                                           [0, n/self.topEdge, 0, 0],
                                           [0, 0, -(f+n)/(f-n), -(2*f*n)/(f-n)],
                                           [0, 0, -1, 0]])
        
    def glClearColor(self, r, g, b):
        #los valores de r, g, b deben estar entre 0 y 1
        r = min(1, max(0, r))
        g = min(1, max(0, g))
        b = min(1, max(0, b))

        self.ClearColor = [r,g,b]
    
    def glColor(self, r, g, b):
        #los valores de r, g, b deben estar entre 0 y 1
        r = min(1, max(0, r))
        g = min(1, max(0, g))
        b = min(1, max(0, b))

        #curr para el color actual
        self.currColor = [r,g,b]
    
    def glClear(self):
        #compresion de listas
        color = [int(i * 255) for i in self.ClearColor]
        self.screen.fill(color)

        self.frameBuffer = [[color for y in range(self.height)]
                            for x in range(self.width)]
        
        self.zBuffer = [[float('inf') for y in range(self.height)]
                            for x in range(self.width)]
    
    def glPoint(self, x, y, color = None):
        
        x = round(x)
        y = round(y)

        if (0 <= x < self.width) and (0 <= y < self.height):
             color = [int(i * 255) for i in (color or self.currColor)]
             self.screen.set_at((x, self.height - y - 1), color)

             self.frameBuffer[x][y] = color

    def glLine(self, p0, p1, color = None):
        # y = mx + b

        #Algoritmo de linea de Bresenham
        x0 = p0[0]
        x1 = p1[0]
        y0 = p0[1]
        y1 = p1[1] 
        
        #Revisar si el punto es igual que el punto 1, solamente dibujar un punto. Para evitar division por cero
        if x0 == x1 and y0 == y1:
            self.glPoint(x0, y0)
            return
        
        #En vez de sacar las pendientes, sacamos los deltas
        dy = abs(y1 - y0)
        dx = abs(x1 - x0)

        #steep corresponde a inclinación
        steep = dy > dx
        #Si la inclinación es mayor a 1, intercambiamos los puntos
        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1

        #Cuando algo va de derecha a izquierda
        if x0 > x1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0
        
        #Volver a calcular los deltas
        dy = abs(y1 - y0)
        dx = abs(x1 - x0)

        #Ahora ya podemos dibujar las lineas
        #Pero antes de dibujar las lineas, tenemos que calcular algunas cosas extra

        #1. el offset, el offset se refiere a cuanto eh subido en la linea
        offset = 0
        #2. el limite, se refiere a partir de que punto se va a dibujar la siguiente linea o siguiente fila de pixeles
        limit = 0
        #3. la pendiente, que es la diferencia entre los deltas
        m = dy / dx
        #4.valor en y actualmente
        y = y0

        #Asegurarse de que los valores de x que se pasan también son enteros
        for x in range(round(x0), round(x1) + 1):
            #Si la inclinación es mayor a 1, entonces tenemos que intercambiar los valores de x e y
            if steep:
                self.glPoint(y, x, color or self.currColor)
            else:
                self.glPoint(x, y, color or self.currColor) 

            #Aumentar el offset
            offset += m

            #Si el offset es mayor al limite, entonces tenemos que aumentar el valor de y
            if offset >= limit:
                if y0 < y1:
                    y += 1
                else:
                    y -= 1

                #Aumentar el limite, para pasar a la siguiente fila de pixeles
                limit += 1
    
    def glRender(self):
        # Render all pixels directly to frameBuffer (no display updates)
        total_pixels = max(1, self.vpWidth * self.vpHeight)
        rendered_pixels = 0

        print(f"Renderizando {total_pixels} pixeles...")

        for i in range(self.vpWidth):
            for j in range(self.vpHeight):
                x = i + self.vpX
                y = j + self.vpY

                if 0 <= x < self.width and 0 <= y < self.height:
                    # Convert screen coordinates to normalized device coordinates
                    pX = ((x + 0.5 - self.vpX) / self.vpWidth) * 2 - 1
                    pY = ((y + 0.5 - self.vpY) / self.vpHeight) * 2 - 1

                    # Apply projection
                    pX *= self.rightEdge
                    pY *= self.topEdge
                    pZ = -self.nearPlane

                    # Crear dirección del rayo desde el plano de proyección
                    dir = np.array([pX, pY, pZ], dtype=float)
                    dir = dir / np.linalg.norm(dir)  # Normalize

                    # Color del rayo con soporte de env map / reflejos / refracciones
                    color = self.glRayColor(self.camera.translation, dir, 0)
                    color_255 = [int(c * 255) for c in color]
                    self.frameBuffer[x][y] = color_255

                rendered_pixels += 1

                # Mostrar progreso cada 10%
                step = max(1, total_pixels // 10)
                if rendered_pixels % step == 0:
                    progress = (rendered_pixels / total_pixels) * 100
                    print(f"Progreso: {progress:.0f}% ({rendered_pixels}/{total_pixels} pixeles)")

        print("\u00a1Renderizado completo!")
    

    
    def glCastRay(self, origin, direction, sceneObj = None):

        depth = float('inf')
        intercept = None
        hit = None

        for obj in self.scene:
            if obj != sceneObj:
                intercept = obj.ray_intersect(origin, direction)
                if intercept != None:
                    if intercept.distance < depth:
                        hit = intercept
                        depth = intercept.distance
        return hit

    def glRayColor(self, origin, direction, depth=0):
        """Devuelve el color [0,1] del rayo con recursión limitada."""
        hit = self.glCastRay(origin, direction)
        if hit and hit.obj.material:
            # Delegar en el material (puede llamar recursivamente)
            return hit.obj.material.GetSurfaceColor(hit, self, depth)

        # Fondo: environment map si existe
        if self.environmentMap is not None:
            # Dirección normalizada en espacio de cámara
            d = direction / (np.linalg.norm(direction) + 1e-12)

            # Yaw/pitch (suponiendo forward -Z):
            # yaw = atan2(x, -z) en [-pi, pi]
            # pitch = asin(y) en [-pi/2, pi/2]
            yaw = np.arctan2(d[0], -d[2])
            pitch = np.arcsin(np.clip(d[1], -1.0, 1.0))

            # Aplicar controles de escala (zoom) y rotación
            f = max(1e-6, float(self.envFovScale))
            yaw = yaw / f + float(self.envYaw)
            pitch = pitch / f + float(self.envPitch)

            # Mapear a UV equirectangular
            u = (yaw + np.pi) / (2.0 * np.pi)
            v = 0.5 - (pitch / np.pi)
            # envolver U para evitar costuras
            u = (u % 1.0 + 1.0) % 1.0
            return self.environmentMap.getColor(u, v)

        # Sin env map, usar color claro de fondo
        return self.ClearColor
    
    
