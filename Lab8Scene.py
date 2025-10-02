"""Lab8: 3 Ellipsoids + 3 Cylinders en variantes opaco / reflectivo / transparente."""

import pygame
import numpy as np
from gl import Renderer
from BMP_Writer import GenerateBMP
from figures import Ellipsoid, Cylinder
from material import Material
from bmp_texture import BMPTexture
from lights import AmbientLight, DirectionalLight

WIDTH = 512
HEIGHT = 512

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.HIDDEN)
rend = Renderer(screen)

# Environment map
try:
    rend.environmentMap = BMPTexture("semuc_enviroment.bmp")
    print("Environment map cargado: semuc_enviroment.bmp")
except Exception:
    rend.environmentMap = None
    print("No se encontró semuc_enviroment.bmp, usando fondo por defecto")

mat_opaco   = Material(diffuse=[0.85, 0.3, 0.25], specular=[1,1,1], shininess=48)
mat_reflect = Material(diffuse=[0.1, 0.1, 0.1], specular=[1,1,1], shininess=256, reflectivity=0.95)
mat_transp  = Material(diffuse=[0.95, 0.97, 1.0], specular=[1,1,1], shininess=96, transparency=0.9, ior=1.5)

cy_opaco   = Material(diffuse=[0.25, 0.6, 0.85], specular=[1,1,1], shininess=64)
cy_reflect = Material(diffuse=[0.15,0.15,0.18], specular=[1,1,1], shininess=196, reflectivity=0.7)
cy_transp  = Material(diffuse=[0.9,0.95,1.0], specular=[1,1,1], shininess=80, transparency=0.75, ior=1.33, reflectivity=0.05)

# Ellipsoids
rend.scene.append(Ellipsoid(position=[-3.2, 1.0, -9.2], radii=[1.4,0.8,1.6], material=mat_opaco, rotation=(0.4, 0.2, -0.1)))
rend.scene.append(Ellipsoid(position=[0.0, 0.9, -8.0], radii=[0.85,1.0,0.9], material=mat_reflect, rotation=(0.0, 0.6, 0.3)))
rend.scene.append(Ellipsoid(position=[3.1, 0.95, -9.6], radii=[0.6,0.45,0.9], material=mat_transp, rotation=(-0.3, -0.5, 0.0)))

# Cylinders
rend.scene.append(Cylinder(position=[-3.0, -1.25, -8.4], radius=0.8, height=1.4, material=cy_opaco, rotation=(0.0, 0.35, 0.15)))
rend.scene.append(Cylinder(position=[0.2, -1.3, -9.4], radius=0.45, height=3.0, material=cy_reflect, rotation=(0.6, 0.0, 0.9)))
rend.scene.append(Cylinder(position=[3.0, -1.2, -8.2], radius=0.55, height=2.2, material=cy_transp, rotation=(0.25, -0.4, 0.0)))

rend.lights.append(AmbientLight(intensity=0.22))
rend.lights.append(DirectionalLight(direction=[-0.4,-1,-0.3], intensity=0.85))
rend.lights.append(DirectionalLight(direction=[0.5,-0.8,-0.4], intensity=0.55, color=[0.95,0.98,1]))

rend.glRender()

OUTPUT = "lab8_2.bmp"
GenerateBMP(OUTPUT, WIDTH, HEIGHT, 3, rend.frameBuffer)
print(f"Imagen guardada como {OUTPUT}")

if __name__ == "__main__":
    pygame.quit()
