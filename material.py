"""Materiales y sombreado (Phong) con soporte de reflexión y refracción."""

import numpy as np
from refractionFunctions import refractVector, fresnel, totalInternalReflection

class Material(object):
    """Material con componentes difusa, especular y ambiente; admite textura difusa opcional
    y reflexión/refracción simples.
    """
    def __init__(self, diffuse=[1,1,1], specular=[1,1,1], shininess=32, ambient=None,
                 reflectivity: float = 0.0, transparency: float = 0.0, ior: float = 1.0,
                 diffuseTexture=None):
        self.diffuse = diffuse  # Color difuso (RGB entre 0-1)
        self.specular = specular  # Color especular
        self.shininess = shininess  # Brillo especular
        self.ambient = ambient if ambient else diffuse  # Color ambiente
        self.reflectivity = max(0.0, min(1.0, reflectivity))
        self.transparency = max(0.0, min(1.0, transparency))
        self.ior = ior  # Índice de refracción (1.0 = aire)
        # Textura difusa opcional (por ejemplo, instancia de BMPTexture)
        self.diffuseTexture = diffuseTexture
    
    def GetSurfaceColor(self, intercept, renderer, depth=0):
        # Modelo de reflexión Phong:
        # FinalColor = Ambient + Diffuse + Specular
        
        finalColor = [0.0, 0.0, 0.0]
        
        # Determinar color base de superficie (textura si existe y hay UV)
        baseColor = self.diffuse
        if self.diffuseTexture is not None and getattr(intercept, 'uv', None) is not None:
            try:
                u, v = intercept.uv
                baseColor = self.diffuseTexture.getColor(float(u), float(v))
            except Exception:
                baseColor = self.diffuse

        # Componente ambiente
        for light in renderer.lights:
            if light.type == "Ambient":
                ambientBase = self.ambient if self.diffuseTexture is None else baseColor
                ambientColor = [ambientBase[i] * light.GetLightColor()[i] for i in range(3)]
                finalColor = [finalColor[i] + ambientColor[i] for i in range(3)]
        
    # Componentes difusa y especular
        for light in renderer.lights:
            if light.type == "Directional":
                # Verificar si hay sombras
                lightDir = [-i for i in light.direction]
                # Mover el punto ligeramente hacia la superficie para evitar self-intersection
                offset = 0.001
                shadowRayOrigin = [intercept.point[i] + intercept.normal[i] * offset for i in range(3)]
                shadowIntercept = renderer.glCastRay(shadowRayOrigin, lightDir, intercept.obj)
                
                if shadowIntercept is None:
                    # No hay sombra, calcular iluminación
                    lightColor = light.GetLightColor(intercept)
                    
                    # Componente difusa
                    diffuseColor = [baseColor[i] * lightColor[i] for i in range(3)]
                    finalColor = [finalColor[i] + diffuseColor[i] for i in range(3)]
                    
                    # Componente especular (Phong)
                    if hasattr(renderer.camera, 'translation'):
                        viewDir = np.array(renderer.camera.translation) - np.array(intercept.point)
                        viewDir = viewDir / np.linalg.norm(viewDir)
                        
                        # Vector de reflexión
                        lightDirNorm = np.array(lightDir) / np.linalg.norm(lightDir)
                        reflectDir = 2 * np.dot(intercept.normal, lightDirNorm) * intercept.normal - lightDirNorm
                        
                        # Cálculo especular
                        specularIntensity = max(0, np.dot(viewDir, reflectDir)) ** self.shininess
                        specularColor = [self.specular[i] * lightColor[i] * specularIntensity for i in range(3)]
                        finalColor = [finalColor[i] + specularColor[i] for i in range(3)]

        # Reflexión / Refracción (recursivo)
        if depth < renderer.maxDepth and (self.reflectivity > 0 or self.transparency > 0):
            n = np.array(intercept.normal, dtype=float)
            i = np.array(intercept.rayDirection, dtype=float)
            i = i / (np.linalg.norm(i) + 1e-12)
            n = n / (np.linalg.norm(n) + 1e-12)

            # Reflexión
            reflectedColor = [0.0, 0.0, 0.0]
            if self.reflectivity > 0:
                r = i - 2 * np.dot(i, n) * n
                r = r / (np.linalg.norm(r) + 1e-12)
                offset = 0.001
                originR = intercept.point + n * offset if np.dot(r, n) > 0 else intercept.point - n * offset
                reflectedColor = renderer.glRayColor(originR, r, depth + 1)

            # Refracción
            refractedColor = [0.0, 0.0, 0.0]
            if self.transparency > 0:
                n1 = 1.0
                n2 = self.ior
                try:
                    tir = totalInternalReflection(n, i, n1, n2)
                except Exception:
                    tir = False
                if tir:
                    refractedColor = reflectedColor
                else:
                    try:
                        t = refractVector(n, i, n1, n2)
                        offset = 0.001
                        originT = intercept.point - n * offset if np.dot(t, n) < 0 else intercept.point + n * offset
                        refractedColor = renderer.glRayColor(originT, t, depth + 1)
                    except Exception:
                        refractedColor = reflectedColor

                # Fresnel para mezclar (si es posible)
                try:
                    Kr, Kt = fresnel(n, i, n1, n2)
                except Exception:
                    Kr, Kt = 0.5, 0.5
            else:
                Kr, Kt = 0.0, 1.0

            # Mezcla final (ponderación simple)
            localFactor = max(0.0, 1.0 - self.reflectivity - self.transparency)
            color = [0.0, 0.0, 0.0]
            for c in range(3):
                color[c] = (
                    localFactor * finalColor[c]
                    + self.reflectivity * reflectedColor[c]
                    + self.transparency * (Kr * reflectedColor[c] + Kt * refractedColor[c])
                )
            finalColor = color

        # Limitar cada canal a [0,1]
        finalColor = [min(1, max(0, finalColor[i])) for i in range(3)]
        return finalColor