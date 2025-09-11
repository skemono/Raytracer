"""Script principal: escena de 6 esferas (opacas, reflectantes y transparentes)
con un environment map de fondo.
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

# Cargar environment map si existe en el proyecto
try:
    rend.environmentMap = BMPTexture("semuc_enviroment.bmp")
    print("Environment map cargado: semuc_enviroment.bmp")
except Exception as e:
    print("No se pudo cargar el environment map, se usará color de fondo.")

# Materiales
opaque_red = Material(diffuse=[0.9, 0.2, 0.2], specular=[1, 1, 1], shininess=32)
opaque_green = Material(diffuse=[0.2, 0.8, 0.2], specular=[1, 1, 1], shininess=16)

mirror = Material(diffuse=[0.0, 0.0, 0.0], reflectivity=1.0, specular=[1, 1, 1], shininess=128)
polished_metal = Material(diffuse=[0.8, 0.6, 0.2], reflectivity=0.6, specular=[1, 1, 1], shininess=96)

glass = Material(diffuse=[0.9, 0.9, 1.0], transparency=0.9, ior=1.52, specular=[1, 1, 1], shininess=64)
water = Material(diffuse=[0.9, 0.9, 1.0], transparency=0.7, ior=1.33, specular=[1, 1, 1], shininess=32)

# Esferas: 6 visibles, 3 arriba y 3 abajo
z_front = -8.0
z_back = -10.0
row_y_top = 0.6
row_y_bottom = -1.0
radius = 0.8

# Arriba (izq->der): opaca roja, espejo, transparente (vidrio)
rend.scene.append(Sphere(position=[-2.0, row_y_top, z_front], radius=radius, material=opaque_red))
rend.scene.append(Sphere(position=[0.0, row_y_top, z_front], radius=radius, material=mirror))
rend.scene.append(Sphere(position=[2.0, row_y_top, z_front], radius=radius, material=glass))

# Abajo (izq->der): opaca verde, metal pulido, transparente (agua)
rend.scene.append(Sphere(position=[-2.0, row_y_bottom, z_back], radius=radius, material=opaque_green))
rend.scene.append(Sphere(position=[0.0, row_y_bottom, z_back], radius=radius, material=polished_metal))
rend.scene.append(Sphere(position=[2.0, row_y_bottom, z_back], radius=radius, material=water))

# Iluminación
rend.lights.append(AmbientLight(intensity=0.2))
rend.lights.append(DirectionalLight(direction=[-1, -1, -1], intensity=0.9))

# Render de la escena
rend.glRender()

# Guardar la imagen a disco en formato BMP
output = "semucSpheresEnv.bmp"
GenerateBMP(output, width, height, 3, rend.frameBuffer)
print(f"Imagen guardada como '{output}'")

if __name__ == "__main__":
    pygame.quit()