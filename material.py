"""Materiales y sombreado (modelo de Phong simplificado)."""

import numpy as np

class Material(object):
    """Material con componentes difusa, especular y ambiente."""
    def __init__(self, diffuse=[1,1,1], specular=[1,1,1], shininess=32, ambient=None):
        self.diffuse = diffuse  # Color difuso (RGB entre 0-1)
        self.specular = specular  # Color especular
        self.shininess = shininess  # Brillo especular
        self.ambient = ambient if ambient else diffuse  # Color ambiente
    
    def GetSurfaceColor(self, intercept, renderer):
        # Modelo de reflexión Phong:
        # FinalColor = Ambient + Diffuse + Specular
        
        finalColor = [0, 0, 0]
        
        # Componente ambiente
        for light in renderer.lights:
            if light.type == "Ambient":
                ambientColor = [self.ambient[i] * light.GetLightColor()[i] for i in range(3)]
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
                    diffuseColor = [self.diffuse[i] * lightColor[i] for i in range(3)]
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
        
    # Limitar cada canal a [0,1]
        finalColor = [min(1, max(0, finalColor[i])) for i in range(3)]
        
        return finalColor