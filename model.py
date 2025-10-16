"""Wavefront OBJ model loading and Mesh primitive for the raytracer.

This module provides:
- OBJMesh: a Shape subclass that performs ray-triangle intersections
- load_obj: a simple Wavefront OBJ parser that returns an OBJMesh

Supported OBJ features:
- v (positions), vt (texcoords), vn (normals)
- f faces with formats: v, v/vt, v//vn, v/vt/vn
- Triangulation by fan for n-gons and quads
- optional smoothing using per-vertex normals when available

Materials (mtl) and textures are not parsed here; assign a Material when
creating or loading the mesh.
"""

from __future__ import annotations

from typing import List, Tuple, Optional
import math
import os

import numpy as np

# Import base Shape and Intercept from project
from figures import Shape  # type: ignore
from intercept import Intercept  # type: ignore


class OBJMesh(Shape):
	"""Triangle mesh Shape with optional per-vertex normals/uvs.

	vertices: np.ndarray of shape (N, 3)
	faces: list of triangles; each triangle is a tuple of 3 elements, where each
		   element is a tuple (vi, vti, vni) of indices (or None for missing).
		   Indices are 0-based into vertices/texcoords/normals arrays.
	texcoords: np.ndarray of shape (M, 2) or None
	normals: np.ndarray of shape (K, 3) or None
	position: world-space translation applied after loading (for convenience)
	rotation: Euler XYZ in radians (applied to vertices if provided)
	scale: uniform or 3-float scale (applied to vertices if provided)
	smooth_shading: if True and vertex normals available, interpolate normals
	"""

	def __init__(
		self,
		vertices: np.ndarray,
		faces: List[Tuple[Tuple[Optional[int], Optional[int], Optional[int]],
						  Tuple[Optional[int], Optional[int], Optional[int]],
						  Tuple[Optional[int], Optional[int], Optional[int]]]],
		material,
		texcoords: Optional[np.ndarray] = None,
		normals: Optional[np.ndarray] = None,
		position: Tuple[float, float, float] = (0.0, 0.0, 0.0),
		rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0),
		scale: Tuple[float, float, float] | float = 1.0,
		smooth_shading: bool = True,
	):
		super().__init__(position=list(position), material=material)
		self.type = "Mesh"

		verts = np.asarray(vertices, dtype=float).copy()
		if isinstance(scale, (int, float)):
			s = np.array([scale, scale, scale], dtype=float)
		else:
			s = np.array(scale, dtype=float)

		# Apply scale, rotation, translation to vertices
		verts *= s
		rx, ry, rz = rotation
		if abs(rx) > 1e-12 or abs(ry) > 1e-12 or abs(rz) > 1e-12:
			cx, sx = math.cos(rx), math.sin(rx)
			cy, sy = math.cos(ry), math.sin(ry)
			cz, sz = math.cos(rz), math.sin(rz)
			Rx = np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]])
			Ry = np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]])
			Rz = np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]])
			R = Rz @ Ry @ Rx
			verts = (R @ verts.T).T
		verts += np.array(position, dtype=float)

		self.vertices = verts
		self.faces = faces
		self.texcoords = np.asarray(texcoords, dtype=float) if texcoords is not None else None
		if normals is not None:
			# Ensure normalized normals
			n = np.asarray(normals, dtype=float)
			ln = np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
			self.normals = n / ln
		else:
			self.normals = None
		self.smooth = bool(smooth_shading)

		# Optional: precompute face normals for fallback
		self._face_normals = None  # lazy compute

		# Precompute axis-aligned bounding box in world space
		self._bb_min = np.min(self.vertices, axis=0)
		self._bb_max = np.max(self.vertices, axis=0)

	def _get_face_normal(self, tri_idx: int) -> np.ndarray:
		if self._face_normals is None:
			self._face_normals = []
			for tri in self.faces:
				(v0i, _, _), (v1i, _, _), (v2i, _, _) = tri
				v0 = self.vertices[v0i]
				v1 = self.vertices[v1i]
				v2 = self.vertices[v2i]
				n = np.cross(v1 - v0, v2 - v0)
				ln = np.linalg.norm(n) + 1e-12
				self._face_normals.append(n / ln)
		return self._face_normals[tri_idx]

	@staticmethod
	def _mt_intersect(v0, v1, v2, orig, dir) -> Optional[Tuple[float, float, float]]:
		"""Möller–Trumbore: returns (t, u, v) or None."""
		EPS = 1e-6
		edge1 = v1 - v0
		edge2 = v2 - v0
		pvec = np.cross(dir, edge2)
		det = np.dot(edge1, pvec)
		if -EPS < det < EPS:
			return None
		inv_det = 1.0 / det
		tvec = orig - v0
		u = np.dot(tvec, pvec) * inv_det
		if u < 0.0 or u > 1.0:
			return None
		qvec = np.cross(tvec, edge1)
		v = np.dot(dir, qvec) * inv_det
		if v < 0.0 or u + v > 1.0:
			return None
		t = np.dot(edge2, qvec) * inv_det
		if t > EPS:
			return (t, u, v)
		return None

	def ray_intersect(self, orig, dir):
		orig = np.asarray(orig, dtype=float)
		dir = np.asarray(dir, dtype=float)

		# AABB culling
		inv_dir = 1.0 / np.where(np.abs(dir) < 1e-12, 1e-12, dir)
		t1 = (self._bb_min - orig) * inv_dir
		t2 = (self._bb_max - orig) * inv_dir
		tmin = np.maximum.reduce(np.minimum(t1, t2))
		tmax = np.minimum.reduce(np.maximum(t1, t2))
		if tmax < 0 or tmin > tmax:
			return None

		best_t = float('inf')
		best_hit = None
		best_normal = None
		best_uv = None

		for idx, tri in enumerate(self.faces):
			(v0i, vt0i, vn0i), (v1i, vt1i, vn1i), (v2i, vt2i, vn2i) = tri
			v0 = self.vertices[v0i]
			v1 = self.vertices[v1i]
			v2 = self.vertices[v2i]

			res = self._mt_intersect(v0, v1, v2, orig, dir)
			if res is None:
				continue
			t, u, v = res
			if t < best_t:
				best_t = t
				hit_point = orig + dir * t

				# Compute normal: smooth if vertex normals provided and enabled
				if self.smooth and self.normals is not None and (vn0i is not None and vn1i is not None and vn2i is not None):
					w = 1.0 - u - v
					n0 = self.normals[vn0i]
					n1 = self.normals[vn1i]
					n2 = self.normals[vn2i]
					n = n0 * w + n1 * u + n2 * v
					n /= (np.linalg.norm(n) + 1e-12)
					best_normal = n
				else:
					best_normal = self._get_face_normal(idx)

				# Interpolate UV if available
				if self.texcoords is not None and (vt0i is not None and vt1i is not None and vt2i is not None):
					w = 1.0 - u - v
					uv0 = self.texcoords[vt0i]
					uv1 = self.texcoords[vt1i]
					uv2 = self.texcoords[vt2i]
					uv = uv0 * w + uv1 * u + uv2 * v
					best_uv = (float(uv[0]), float(uv[1]))
				else:
					best_uv = None

				best_hit = hit_point

		if best_hit is None:
			return None
		return Intercept(best_hit, best_normal, float(best_t), dir, self, uv=best_uv)


def load_obj(
	filepath: str,
	material,
	position: Tuple[float, float, float] = (0.0, 0.0, 0.0),
	scale: Tuple[float, float, float] | float = 1.0,
	rotation_degrees: Tuple[float, float, float] = (0.0, 0.0, 0.0),
	smooth_shading: bool = True,
) -> OBJMesh:
	"""Load a Wavefront OBJ and return an OBJMesh.

	- filepath: path to .obj
	- material: Material instance to assign
	- position/scale/rotation_degrees: transform applied to vertices
	- smooth_shading: interpolate normals if per-vertex normals exist
	"""
	if not os.path.isfile(filepath):
		raise FileNotFoundError(f"OBJ not found: {filepath}")

	verts: List[Tuple[float, float, float]] = []
	tex: List[Tuple[float, float]] = []
	norms: List[Tuple[float, float, float]] = []
	faces: List[Tuple[Tuple[Optional[int], Optional[int], Optional[int]],
					  Tuple[Optional[int], Optional[int], Optional[int]],
					  Tuple[Optional[int], Optional[int], Optional[int]]]] = []

	with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
		for line in f:
			line = line.strip()
			if not line or line.startswith('#'):
				continue
			parts = line.split()
			if parts[0] == 'v' and len(parts) >= 4:
				x, y, z = map(float, parts[1:4])
				verts.append((x, y, z))
			elif parts[0] == 'vt' and len(parts) >= 3:
				u, v = map(float, parts[1:3])
				tex.append((u, v))
			elif parts[0] == 'vn' and len(parts) >= 4:
				nx, ny, nz = map(float, parts[1:4])
				norms.append((nx, ny, nz))
			elif parts[0] == 'f' and len(parts) >= 4:
				# Parse face vertices
				fv = parts[1:]
				# Convert tokens to index triplets (0-based), handling negatives
				triplets: List[Tuple[Optional[int], Optional[int], Optional[int]]] = []
				for tok in fv:
					vi = vti = vni = None
					if '//' in tok:
						a, c = tok.split('//')
						vi = int(a)
						vni = int(c) if c else None
					elif '/' in tok:
						elems = tok.split('/')
						if len(elems) == 3:
							vi = int(elems[0]) if elems[0] else None
							vti = int(elems[1]) if elems[1] else None
							vni = int(elems[2]) if elems[2] else None
						elif len(elems) == 2:
							vi = int(elems[0]) if elems[0] else None
							vti = int(elems[1]) if elems[1] else None
						else:
							vi = int(elems[0]) if elems[0] else None
					else:
						vi = int(tok)

					def fix_index(idx: Optional[int], n: int) -> Optional[int]:
						if idx is None:
							return None
						# OBJ is 1-based; negative means relative to end
						if idx > 0:
							return idx - 1
						else:
							return n + idx

					vi = fix_index(vi, len(verts))
					vti = fix_index(vti, len(tex))
					vni = fix_index(vni, len(norms))
					if vi is None:
						continue
					triplets.append((vi, vti, vni))

				# Triangulate fan if polygon has more than 3 vertices
				if len(triplets) >= 3:
					for i in range(1, len(triplets) - 1):
						faces.append((triplets[0], triplets[i], triplets[i + 1]))

	if not verts or not faces:
		raise ValueError(f"OBJ has no vertices or faces: {filepath}")

	# Convert to arrays
	v_arr = np.array(verts, dtype=float)
	vt_arr = np.array(tex, dtype=float) if tex else None
	vn_arr = np.array(norms, dtype=float) if norms else None

	# Rotation degrees -> radians
	rx, ry, rz = [math.radians(a) for a in rotation_degrees]

	mesh = OBJMesh(
		vertices=v_arr,
		faces=faces,
		material=material,
		texcoords=vt_arr,
		normals=vn_arr,
		position=position,
		rotation=(rx, ry, rz),
		scale=scale,
		smooth_shading=smooth_shading,
	)
	return mesh

