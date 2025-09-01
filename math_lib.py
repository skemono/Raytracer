"""Funciones matemáticas para transformaciones y coordenadas (PEP 8)."""

import numpy as np
from math import pi, sin, cos


def TranslationMatrix(x, y, z):
    """Matriz de traslación 4x4."""
    return np.matrix(
        [[1, 0, 0, x], [0, 1, 0, y], [0, 0, 1, z], [0, 0, 0, 1]]
    )


def ScaleMatrix(x, y, z):
    """Matriz de escala 4x4."""
    return np.matrix(
        [[x, 0, 0, 0], [0, y, 0, 0], [0, 0, z, 0], [0, 0, 0, 1]]
    )


def barycentricCoords(A, B, C, P):
    """
    Coordenadas baricéntricas de P con respecto al triángulo ABC.
    Devuelve (u, v, w) o None si P está fuera o el triángulo es degenerado.
    """
    areaPCB = abs((P[0] * C[1] + C[0] * B[1] + B[0] * P[1]) - (P[1] * C[0] + C[1] * B[0] + B[1] * P[0]))
    areaACP = abs((A[0] * C[1] + C[0] * P[1] + P[0] * A[1]) - (A[1] * C[0] + C[1] * P[0] + P[1] * A[0]))
    areaABP = abs((A[0] * B[1] + B[0] * P[1] + P[0] * A[1]) - (A[1] * B[0] + B[1] * P[0] + P[1] * A[0]))
    areaABC = abs((A[0] * B[1] + B[0] * C[1] + C[0] * A[1]) - (A[1] * B[0] + B[1] * C[0] + C[1] * A[0]))

    if areaABC == 0:
        return None

    u = areaPCB / areaABC
    v = areaACP / areaABC
    w = areaABP / areaABC

    if 0 <= u <= 1 and 0 <= v <= 1 and 0 <= w <= 1:
        return (u, v, w)
    else:
        return None


def RotationMatrix(pitch, yaw, roll):
    """
    Matriz de rotación 4x4 (pitch, yaw, roll) en grados.
    Orden: pitch * yaw * roll (convención del código original).
    """
    pitch *= pi / 180
    yaw *= pi / 180
    roll *= pi / 180

    pitchMat = np.matrix(
        [[1, 0, 0, 0], [0, cos(pitch), -sin(pitch), 0], [0, sin(pitch), cos(pitch), 0], [0, 0, 0, 1]]
    )

    yawMat = np.matrix(
        [[cos(yaw), 0, sin(yaw), 0], [0, 1, 0, 0], [-sin(yaw), 0, cos(yaw), 0], [0, 0, 0, 1]]
    )

    rollMat = np.matrix(
        [[cos(roll), -sin(roll), 0, 0], [sin(roll), cos(roll), 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
    )

    return pitchMat * yawMat * rollMat
