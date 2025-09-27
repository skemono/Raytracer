"""Script principal: Escena DEMO de características.

Muestra:
 - Environment map (plato.bmp si existe)
 - Geometrías: Sphere, Cube (AABB), OrientedBox, Ellipsoid, Triangle, Disk (espejo), Plane (piso)
 - Materiales con reflexión y transparencia (vidrio/agua)
 - Diferentes normales y orientaciones (OBB rotada, elipsoide escalado)
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

# Intentar cargar nuevo environment map
try:
    rend.environmentMap = BMPTexture("semuc_enviroment.bmp")
    print("Environment map cargado: semuc_enviroment.bmp")
except Exception as e:
    rend.environmentMap = None
    print("No se pudo cargar semuc_enviroment.bmp, se usará color de fondo.")

# Materiales
opaque_red = Material(diffuse=[0.9, 0.2, 0.2], specular=[1, 1, 1], shininess=32)
opaque_green = Material(diffuse=[0.2, 0.8, 0.2], specular=[1, 1, 1], shininess=16)

mirror = Material(diffuse=[0.0, 0.0, 0.0], reflectivity=1.0, specular=[1, 1, 1], shininess=128)
polished_metal = Material(diffuse=[0.8, 0.6, 0.2], reflectivity=0.6, specular=[1, 1, 1], shininess=96)

glass = Material(diffuse=[0.9, 0.9, 1.0], transparency=0.9, ior=1.52, specular=[1, 1, 1], shininess=64)
water = Material(diffuse=[0.9, 0.9, 1.0], transparency=0.7, ior=1.33, specular=[1, 1, 1], shininess=32)

# ------------------------------
# ------------------------------
# Escena de demostración

# Piso (plano) ligeramente gris para recibir reflejos/sombras
floor_mat = Material(diffuse=[0.6,0.6,0.6], specular=[0.2,0.2,0.2], shininess=16)
rend.scene.append(Plane(position=[0,-2, -8], normal=[0,1,0], material=floor_mat))

# Disco espejo en el centro para reflejar objetos
mirror_disk_mat = Material(diffuse=[0.05,0.05,0.05], specular=[1,1,1], shininess=256, reflectivity=0.95)
rend.scene.append(Disk(position=[0,-1.999,-8], normal=[0,1,0], radius=2.8, material=mirror_disk_mat))

# Esfera transparente (vidrio) a la izquierda
glass = Material(diffuse=[0.9,0.95,1.0], transparency=0.9, ior=1.52, specular=[1,1,1], shininess=96, reflectivity=0.05)
rend.scene.append(Sphere(position=[-2.2,-1.0,-8.2], radius=0.9, material=glass))

# Esfera agua para comparar
water = Material(diffuse=[0.95,0.95,1.0], transparency=0.7, ior=1.33, specular=[1,1,1], shininess=64, reflectivity=0.05)
rend.scene.append(Sphere(position=[-0.9,-1.05,-9.5], radius=0.6, material=water))

# Cubo metálico pulido
metal = Material(diffuse=[0.8,0.6,0.25], reflectivity=0.6, specular=[1,1,1], shininess=128)
rend.scene.append(Cube(position=[1.6,-1.3,-7.2], edge=1.2, material=metal))

# Oriented Box (rotada) semirreflectiva
obb_mat = Material(diffuse=[0.25,0.45,0.9], specular=[1,1,1], shininess=64, reflectivity=0.2)
rend.scene.append(OrientedBox(position=[0.9,-0.8,-9.2], half_sizes=[0.5,0.9,0.4], rotation=[0.4,0.8,0.2], material=obb_mat))

# Elipsoide aplastado (mostrando escalado no uniforme)
ellip_mat = Material(diffuse=[0.35,0.85,0.55], specular=[1,1,1], shininess=48)
rend.scene.append(Ellipsoid(position=[-1.0,0.2,-7.0], radii=[0.8,0.5,1.2], material=ellip_mat))

# Triángulo flotando arriba
tri_mat = Material(diffuse=[0.9,0.3,0.4], specular=[1,1,1], shininess=64)
tv0 = [-0.5, 1.0, -8.3]
tv1 = [ 0.7, 1.2, -8.0]
tv2 = [ 0.1, 1.6, -7.5]
rend.scene.append(Triangle(tv0, tv1, tv2, tri_mat))

# Esfera espejo pequeña para mostrar reflejos múltiples
mirror_small = Material(diffuse=[0,0,0], reflectivity=1.0, specular=[1,1,1], shininess=256)
rend.scene.append(Sphere(position=[0.3,-1.15,-8.1], radius=0.35, material=mirror_small))

# Iluminación: ambiente + dos direccionales para highlights cruzados
rend.lights.append(AmbientLight(intensity=0.22))
rend.lights.append(DirectionalLight(direction=[-0.4,-1,-0.3], intensity=0.85, color=[1,1,1]))
rend.lights.append(DirectionalLight(direction=[0.45,-0.9,-0.5], intensity=0.55, color=[0.95,0.98,1]))

# Render de la escena
rend.glRender()

# Guardar la imagen a disco en formato BMP
output = "features_demo.bmp"
GenerateBMP(output, width, height, 3, rend.frameBuffer)
print(f"Imagen guardada como '{output}'")

if __name__ == "__main__":
    pygame.quit()