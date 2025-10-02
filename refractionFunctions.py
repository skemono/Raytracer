import numpy as np
from math import acos, asin, pi

def refractVector(normal, incident, n1, n2):
	"""Calcula el vector refractado usando la Ley de Snell con robustez numérica.
	Clamps se aplican para evitar valores negativos bajo la raíz por errores flotantes.
	"""
	# Aseguramos arrays numpy
	normal = np.array(normal, dtype=float)
	incident = np.array(incident, dtype=float)
	incident = incident / (np.linalg.norm(incident) + 1e-12)
	normal = normal / (np.linalg.norm(normal) + 1e-12)

	c1 = float(np.dot(normal, incident))
	if c1 < 0:
		c1 = -c1
	else:
		# Invertir normal y swap de índices si el rayo viene desde dentro
		normal = -normal
		n1, n2 = n2, n1

	n = n1 / n2
	# Termino bajo la raíz: 1 - n^2 (1 - c1^2)
	inside = 1 - n**2 * (1 - c1**2)
	if inside < 0:
		# Total internal reflection fallback (devuelve None para que caller use reflexión)
		return None
	inside = max(0.0, inside)
	root = inside ** 0.5
	T = n * (incident + c1 * normal) - normal * root
	norm = np.linalg.norm(T)
	if norm < 1e-12:
		return None
	return T / norm


def totalInternalReflection(normal, incident, n1, n2):
	c1 = np.dot(normal, incident)
	if c1 < 0:
		c1 = -c1
	else:
		n1, n2 = n2, n1
		
	if n1 < n2:
		return False
	
	theta1 = acos(c1)
	thetaC = asin(n2/n1)
	
	return theta1 >= thetaC


def fresnel(normal, incident, n1, n2):
	"""Calcula coeficientes Fresnel (Kr reflejado, Kt transmitido) con clamps.
	Evita valores NaN cuando la refracción no es física.
	"""
	normal = np.array(normal, dtype=float)
	incident = np.array(incident, dtype=float)
	incident = incident / (np.linalg.norm(incident) + 1e-12)
	normal = normal / (np.linalg.norm(normal) + 1e-12)

	c1 = float(np.dot(normal, incident))
	if c1 < 0:
		c1 = -c1
	else:
		n1, n2 = n2, n1

	# s2 = n1*sin(theta1)/n2 ; sin(theta1) = sqrt(1-c1^2)
	sin_theta1_sq = max(0.0, 1 - c1**2)
	sin_theta1 = sin_theta1_sq ** 0.5
	s2 = (n1 * sin_theta1) / n2
	# Total internal reflection -> 100% reflejo
	if s2 > 1.0:
		return 1.0, 0.0
	c2_sq = max(0.0, 1 - s2**2)
	c2 = c2_sq ** 0.5

	# Fórmulas de Fresnel (polarizaciones)
	den1 = (n2 * c1) + (n1 * c2)
	den2 = (n1 * c2) + (n2 * c1)
	if abs(den1) < 1e-12 or abs(den2) < 1e-12:
		return 1.0, 0.0
	F1 = ((n2 * c1 - n1 * c2) / den1) ** 2
	F2 = ((n1 * c2 - n2 * c1) / den2) ** 2
	Kr = max(0.0, min(1.0, (F1 + F2) / 2))
	Kt = 1 - Kr
	return Kr, Kt