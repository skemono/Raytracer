"""Script principal que construye una escena y la renderiza a BMP."""

import pygame
from gl import *
# Nota: existe una versión PEP8 en bmp_writer.py, pero para compatibilidad
# con el proyecto actual usamos el nombre original:
from BMP_Writer import GenerateBMP
from figures import *
from lights import *
from material import Material
import math

width = 512
height = 512

# Inicializar pygame en modo headless (sin ventana visible)
pygame.init()
screen = pygame.display.set_mode((width, height), pygame.HIDDEN)

rend = Renderer(screen)

# Definir materiales en tonos necesarios (difusos)
pig_pink = Material(diffuse=[0.96, 0.73, 0.73])
pig_dark_pink = Material(diffuse=[0.90, 0.45, 0.55])
black = Material(diffuse=[0.05, 0.05, 0.05])
white = Material(diffuse=[0.95, 0.95, 0.95])
dark_shadow = Material(diffuse=[0.3, 0.3, 0.3])

# cuerpo
rend.scene.append(Sphere(position=[0.0, -0.8, -9.0], radius=1.3, material=pig_pink))

# cabeza
rend.scene.append(Sphere(position=[0.0, 0.6, -7.8], radius=1.1, material=pig_pink))

# hociquin
rend.scene.append(Sphere(position=[0.0, 0.7, -6.9], radius=0.4, material=pig_dark_pink))

# fosas nasales
rend.scene.append(Sphere(position=[-0.12, 0.75, -6.6], radius=0.08, material=black))
rend.scene.append(Sphere(position=[0.12, 0.75, -6.6], radius=0.08, material=black))

# ojos 
rend.scene.append(Sphere(position=[-0.4, 1.1, -7], radius=0.18, material=black))
rend.scene.append(Sphere(position=[0.4, 1.1, -7], radius=0.18, material=black))

# ojos (brillos)
rend.scene.append(Sphere(position=[-0.35, 1.15, -6.9], radius=0.08, material=white))
rend.scene.append(Sphere(position=[0.45, 1.15, -6.9], radius=0.08, material=white))

# orejas
rend.scene.append(Sphere(position=[-0.7, 1.5, -7.9], radius=0.35, material=pig_pink))
rend.scene.append(Sphere(position=[0.7, 1.5, -7.9], radius=0.35, material=pig_pink))

# patas frontales
rend.scene.append(Sphere(position=[-0.7, -2.0, -8.3], radius=0.28, material=pig_pink))  # Front left
rend.scene.append(Sphere(position=[0.7, -2.0, -8.3], radius=0.28, material=pig_pink))   # Front right

# patas
rend.scene.append(Sphere(position=[-0.7, -2.0, -9.7], radius=0.28, material=pig_pink))  # Back left
rend.scene.append(Sphere(position=[0.7, -2.0, -9.7], radius=0.28, material=pig_pink))   # Back right

# manitas
rend.scene.append(Sphere(position=[-1.3, -0.1, -9.7], radius=0.12, material=pig_pink))
rend.scene.append(Sphere(position=[1.3, -0.1, -9.7], radius=0.12, material=pig_pink))

# Iluminación
rend.lights.append(AmbientLight(intensity=0.2))
rend.lights.append(DirectionalLight(direction=[-1, -1, -1], intensity=0.8))

# Render de la escena
rend.glRender()

# Guardar la imagen a disco en formato BMP
GenerateBMP("pig_raytracer.bmp", width, height, 3, rend.frameBuffer)

print("Imagen guardada como 'pig_raytracer.bmp'")

if __name__ == "__main__":
    # Cerrar pygame al terminar (no se muestra ventana)
    pygame.quit()