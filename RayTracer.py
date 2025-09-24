"""Script principal: render de un cuarto minimalista (5 planos) con
dos cubos, un triángulo y un disco. Iluminación ambiente + direccional.

Requerimientos de la tarea:
 - Dibujar planos, discos, triángulos y cubos con el RayTracer.
 - Escena: habitación (piso, techo, pared izquierda, derecha, fondo) y dentro
     dos cubos, un triángulo y un disco.
 - Materiales simples (Phong) reutilizando `Material`.
"""

import pygame
from gl import *
from BMP_Writer import GenerateBMP
from figures import *
from lights import *
from material import Material
from bmp_texture import BMPTexture

width = 512
height = 512

# Inicializar pygame en modo headless (sin ventana visible)
pygame.init()
screen = pygame.display.set_mode((width, height), pygame.HIDDEN)

rend = Renderer(screen)

# No usamos environment map en esta tarea (cuarto cerrado neutro)
rend.environmentMap = None

# Materiales
opaque_red = Material(diffuse=[0.9, 0.2, 0.2], specular=[1, 1, 1], shininess=32)
opaque_green = Material(diffuse=[0.2, 0.8, 0.2], specular=[1, 1, 1], shininess=16)

mirror = Material(diffuse=[0.0, 0.0, 0.0], reflectivity=1.0, specular=[1, 1, 1], shininess=128)
polished_metal = Material(diffuse=[0.8, 0.6, 0.2], reflectivity=0.6, specular=[1, 1, 1], shininess=96)

glass = Material(diffuse=[0.9, 0.9, 1.0], transparency=0.9, ior=1.52, specular=[1, 1, 1], shininess=64)
water = Material(diffuse=[0.9, 0.9, 1.0], transparency=0.7, ior=1.33, specular=[1, 1, 1], shininess=32)

# ------------------------------
# Construcción de la habitación
# Coordenadas: cámara en (0,0,0) mirando -Z. Ponemos la sala delante.
# Plano del piso: y = -2
room_size = 8  # ancho/largo aproximado
half = room_size / 2

floor_mat = Material(diffuse=[0.6, 0.6, 0.6], specular=[0.2,0.2,0.2], shininess=8)
wall_mat = Material(diffuse=[0.85, 0.85, 0.85], specular=[0.05,0.05,0.05], shininess=4)
ceiling_mat = Material(diffuse=[0.9, 0.9, 0.9], specular=[0.1,0.1,0.1], shininess=8)

# Planos (piso, techo, izquierda, derecha, fondo). No añadimos pared frontal para ver interior.
rend.scene.append(Plane(position=[0, -2, -room_size/2], normal=[0, 1, 0], material=floor_mat))
rend.scene.append(Plane(position=[0,  4, -room_size/2], normal=[0,-1, 0], material=ceiling_mat))
rend.scene.append(Plane(position=[-half, 0, -room_size/2], normal=[1, 0, 0], material=wall_mat))
rend.scene.append(Plane(position=[ half, 0, -room_size/2], normal=[-1,0, 0], material=wall_mat))
rend.scene.append(Plane(position=[0, 0, -room_size-4], normal=[0,0,1], material=wall_mat))

# ------------------------------
# Figuras internas (centradas encima de un disco grande reflectante)
cube_mat1 = Material(diffuse=[0.25, 0.45, 0.95], specular=[1,1,1], shininess=96, reflectivity=0.25)
cube_mat2 = Material(diffuse=[0.95, 0.45, 0.2], specular=[1,1,1], shininess=64, reflectivity=0.15)
triangle_mat = Material(diffuse=[0.35, 0.85, 0.55], specular=[1,1,1], shininess=64)
# Disco espejo casi perfecto
disk_mat = Material(diffuse=[0.05, 0.05, 0.05], specular=[1,1,1], shininess=256, reflectivity=0.97)

# Nuevo radio del disco y posición central
disk_center = [0.0, -1.999, -8.0]
disk_radius = 3.2

# Altura común de las figuras sobre el disco
fig_y = -1.2  # un poco por encima del disco

# Cubos más pequeños
rend.scene.append(Cube(position=[-0.9, fig_y, -7.6], edge=0.9, material=cube_mat1))
rend.scene.append(Cube(position=[ 0.9, fig_y, -7.9], edge=0.9, material=cube_mat2))

# Triángulo pequeño suspendido al centro
v0 = [-0.3, fig_y + 0.2, -8.2]
v1 = [ 0.3, fig_y + 0.25, -8.0]
v2 = [ 0.0, fig_y + 0.85, -7.8]
rend.scene.append(Triangle(v0, v1, v2, triangle_mat))

# Disco grande reflectante
rend.scene.append(Disk(position=disk_center, normal=[0,1,0], radius=disk_radius, material=disk_mat))

# Iluminación: ambiente suave y luz direccional simulando panel
rend.lights.append(AmbientLight(intensity=0.58))
# Panel principal (direccional)
rend.lights.append(DirectionalLight(direction=[-0.45, -1, -0.25], intensity=0.85, color=[1,1,1]))
# Panel secundario
rend.lights.append(DirectionalLight(direction=[0.4, -1, -0.6], intensity=0.45, color=[0.95,0.97,1.0]))
# Punto interno sobre el centro para asegurar luz en caras hacia arriba
rend.lights.append(PointLight(position=[0, 1.2, -8.0], intensity=2.2, color=[1.0, 0.95, 0.9], attenuation=0.15))

# Render de la escena
rend.glRender()

# Guardar la imagen a disco en formato BMP
output = "habitacion_figuras.bmp"
GenerateBMP(output, width, height, 3, rend.frameBuffer)
print(f"Imagen guardada como '{output}'")

if __name__ == "__main__":
    pygame.quit()