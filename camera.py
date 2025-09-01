"""Cámara virtual para el raytracer."""

from math_lib import *
import numpy as np


class Camera(object):
    def __init__(self):
        """Inicializa la cámara en el origen sin rotación."""
        self.translation = [0, 0, 0]
        self.rotation = [0, 0, 0]

    def GetCamMatrix(self):
        """Matriz de cámara (world transform)."""
        translateMat = TranslationMatrix(
            self.translation[0], self.translation[1], self.translation[2]
        )

        rotateMat = RotationMatrix(
            self.rotation[0], self.rotation[1], self.rotation[2]
        )

        return translateMat * rotateMat

    def GetViewMatrix(self):
        """Matriz de vista (inversa de la matriz de cámara)."""
        return np.linalg.inv(self.GetCamMatrix())