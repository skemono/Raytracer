# Raytracer en Python (Tracing + Materiales + Geometría Extendida)

Un raytracer educativo en Python que renderiza escenas 3D con materiales opacos, reflectantes, transparentes y refractivos. Ahora incluye nuevas figuras no simétricas (elipsoide, caja orientada) y una escena de demostración que combina reflexión, refracción y distintas normales.



## 🚀 Características

- Motor de raytracing con cámara y proyección.
- Geometrías soportadas:
  - Sphere (esfera)
  - Plane (plano infinito)
  - Disk (disco finito)
  - Triangle (Möller–Trumbore)
  - Cube (AABB axis-aligned)
  - Ellipsoid (radii independientes – escalado no uniforme, ahora con rotación Euler)
  - Cylinder (con rotación Euler y tapas)
  - OrientedBox (OBB con rotación Euler)
  - Figura compuesta opcional: ChickenLeg (elipsoide + cápsula) para ejemplo de objetos compuestos
- Materiales (Phong) con:
  - Difuso, especular, ambiente
  - Reflexión (recursiva)
  - Transparencia + refracción básica (IOR + Fresnel)
- Sombreado con sombras por ray casting secundario.
- Escena configurable: fondo con environment map o cuarto cerrado con planos.
- Exportación a BMP.

## 🛠️ Requisitos

- Python 3.10+ (probado con 3.13)
- numpy
- pygame

## 📦 Instalación rápida

```powershell
python -m venv .venv; .venv\Scripts\Activate.ps1; pip install -U pip; pip install numpy pygame
```

## ▶️ Uso

Renderizar la escena de demostración (features):

```powershell
.venv\Scripts\python.exe .\RayTracer.py
```

Genera `features_demo.bmp`.

### Escena de laboratorio (Lab8)

Ellipsoids (3) y Cylinders (3) en variantes opaca / reflectiva / transparente, con rotaciones y tamaños distintos.

![Lab8 Scene](lab8_2.bmp)

Render:
```powershell
.venv\Scripts\python.exe .\Lab8Scene.py
```
Salida: `lab8_2.bmp`.

### Helper de rotación en grados

Puedes usar la función `deg()` definida en `figures.py` para crear rotaciones Euler sin convertir manualmente:

```python
from figures import Ellipsoid, Cylinder, deg

# Elipsoide rotado 30° en X, 45° en Y, 0° en Z
Ellipsoid(position=[0,1,-8], radii=[1,0.6,1.2], material=mat, rotation=deg(30,45,0))

# Cilindro recostado 90° sobre X
Cylinder(position=[2,-1,-9], radius=0.5, height=2.0, material=mat2, rotation=deg(90,0,0))
```

`deg(a,b,c)` retorna una tupla `(rad(a), rad(b), rad(c))`. Si pasas un solo valor `deg(45)` devuelve `(rad(45),0,0)`.

