"""Escena de la isla: isla central con pilares de fondo y bloques, ajustada a escala.

Todas las posiciones y tamaños se interpretan como valores relativos y se
mapean a coordenadas de mundo mediante una escala uniforme y un origen global
para que la isla quepa cómodamente en cuadro.
"""

import pygame
import numpy as np
import random
from gl import Renderer
from BMP_Writer import GenerateBMP
from material import Material
from bmp_texture import BMPTexture
from image_texture import ImageTexture, load_texture_any
from lights import AmbientLight, DirectionalLight
from figures import OrientedBox, Ellipsoid, Cylinder, EllipticCylinder, Plane, Sphere, Disk, Cube, Capsule, Cone, deg

WIDTH = 800
HEIGHT = 800


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.HIDDEN)
    rend = Renderer(screen)

    # Environment map opcional (intenta formatos comunes)
    env = None
    env_paths = ["proyecto2.png"]
    try:
        # Preferir el cargador genérico si está disponible
        tex = load_texture_any(env_paths)
        if tex is not None:
            env = tex
        else:
            env = BMPTexture("proyecto2.bmp")
        rend.environmentMap = env
        print("Environment map loaded")
    except Exception:
        rend.environmentMap = None

    # Materiales (intenta cargar texturas difusas opcionales)
    tex_rock = load_texture_any(["rock.png"]) or None
    tex_pillar = load_texture_any(["pillar.png"]) or None
    tex_statue = load_texture_any(["statue.png"]) or None

    rock = Material(diffuse=[0.55, 0.52, 0.5], specular=[0.2, 0.2, 0.2], shininess=16, diffuseTexture=tex_rock)
    rock_dark = Material(diffuse=[0.40, 0.38, 0.36], specular=[0.2, 0.2, 0.2], shininess=12, diffuseTexture=tex_rock)
    rock_light = Material(diffuse=[0.65, 0.62, 0.58], specular=[0.25, 0.25, 0.25], shininess=24, diffuseTexture=tex_rock)

    pillar = Material(diffuse=[0.7, 0.7, 0.75], specular=[0.2, 0.2, 0.2], shininess=12, diffuseTexture=tex_pillar)
    pillar_dark = Material(diffuse=[0.5, 0.5, 0.55], specular=[0.2, 0.2, 0.2], shininess=8, diffuseTexture=tex_pillar)
    pillar_light = Material(diffuse=[0.85, 0.82, 0.78], specular=[0.3, 0.3, 0.3], shininess=24, diffuseTexture=tex_pillar)
    statue_mat = Material(diffuse=[0.8, 0.8, 0.85], specular=[0.2, 0.2, 0.2], shininess=24, diffuseTexture=tex_statue)

    # Mapeo global para que la escena quepa en cuadro
    # Escala uniforme de unidades relativas -> unidades de mundo
    S = 0.12  # ~1/9 scale; island radiusX 18 -> ~2.16 in world
    ORG = (0.0, -2, -6.0)  # world origin for the island composition
    P = 0.12  # Pillar scale factor (same as S here, but could be different)
    # Capas de la isla (unidades relativas) para ubicar elementos por nivel en Y
    # Corresponden a los EllipticCylinder apilados que se colocan abajo.
    layer_specs = [
        {"y": 13.0, "h": 0.6, "rx": 11.5, "rz": 8.0, "cx": 0.0, "cz": 4.0},
        {"y": 13.2, "h": 0.6, "rx": 11.7, "rz": 8.2, "cx": 0.0, "cz": 4.0},
        {"y":  9.8, "h": 8.0, "rx": 11.3, "rz": 7.8, "cx": 0.0, "cz": 4.0},
        {"y":  5.8, "h": 4.5, "rx": 10.3, "rz": 6.8, "cx": 0.0, "cz": 4.0},
        {"y":  2.8, "h": 3.0, "rx":  9.3, "rz": 5.8, "cx": -1.0, "cz": 4.0},
        {"y":  0.5, "h": 2.5, "rx":  6.3, "rz": 4.8, "cx": -2.0, "cz": 4.0},
    ]

    def get_layer_for_y(py_rel: float):
        # Return the layer whose y-range contains py, else the nearest by center
        best = None
        best_d = 1e9
        for L in layer_specs:
            y0 = L["y"] - L["h"] * 0.5
            y1 = L["y"] + L["h"] * 0.5
            if y0 <= py_rel <= y1:
                return L
            d = abs(py_rel - L["y"])
            if d < best_d:
                best = L
                best_d = d
        return best
    def to_world(p):
        x, y, z = p
        return [ORG[0] + S * x, ORG[1] + S * y, ORG[2] + S * z]

    def size_scaled(v):
        return S * v
    
    def size_scaled_pillar(v):
        return P * v  

    # Aros del borde (tres cilindros elípticos delgados con pequeños offsets) en y=13
    rend.scene.append(EllipticCylinder(position=to_world([0, 13, 4]), radii_xz=[size_scaled(11.5), size_scaled(8.0)], height=size_scaled(0.6), material=rock_light))
    rend.scene.append(EllipticCylinder(position=to_world([0, 13.2, 4]), radii_xz=[size_scaled(11.7), size_scaled(8.2)], height=size_scaled(0.6), material=rock))
    rend.scene.append(EllipticCylinder(position=to_world([0, 9.8, 4]), radii_xz=[size_scaled(11.3), size_scaled(7.8)], height=size_scaled(8), material=rock))
    rend.scene.append(EllipticCylinder(position=to_world([0, 5.8, 4]), radii_xz=[size_scaled(10.3), size_scaled(6.8)], height=size_scaled(4.5), material=rock))
    rend.scene.append(EllipticCylinder(position=to_world([-1, 2.8, 4]), radii_xz=[size_scaled(9.3), size_scaled(5.8)], height=size_scaled(3), material=rock))
    rend.scene.append(EllipticCylinder(position=to_world([-2, 0.5, 4]), radii_xz=[size_scaled(6.3), size_scaled(4.8)], height=size_scaled(2.5), material=rock))
    rend.scene.append(EllipticCylinder(position=to_world([-3, -1.8, 4]), radii_xz=[size_scaled(3.3), size_scaled(2.8)], height=size_scaled(1.5), material=rock))
    rend.scene.append(EllipticCylinder(position=to_world([-5, -2.5, 4]), radii_xz=[size_scaled(1.3), size_scaled(0.8)], height=size_scaled(0.8), material=rock))
    rend.scene.append(EllipticCylinder(position=to_world([-6, -2.5, 4]), radii_xz=[size_scaled(0.8), size_scaled(0.3)], height=size_scaled(3), material=rock))
    rend.scene.append(EllipticCylinder(position=to_world([-7, -2.5, 4]), radii_xz=[size_scaled(0.4), size_scaled(0.2)], height=size_scaled(5), material=rock))
    


    # # Ayudantes para ubicar elementos en la ladera de la isla (elipse en XZ)
    # def ellipse_boundary_from_dir(px, py, pz):
    #     # Seleccionar la capa adecuada para esta altura y sus radios/centro
    #     L = get_layer_for_y(float(py))
    #     CX, CZ, A, B = L["cx"], L["cz"], L["rx"], L["rz"]
    #     # Vector desde el centro de la capa al punto en espacio relativo
    #     vx = float(px) - CX
    #     vz = float(pz) - CZ
    #     if abs(vx) < 1e-9 and abs(vz) < 1e-9:
    #         vx = 1.0
    #         vz = 0.0
    #     denom = (vx*vx)/(A*A) + (vz*vz)/(B*B)
    #     t = 1.0 / (denom ** 0.5)
    #     bx = CX + vx * t
    #     bz = CZ + vz * t
    #     return bx, bz

    # def ellipse_normal_at(xb, py, zb):
    #     # Gradiente de x^2/A^2 + z^2/B^2 = 1 (espacio relativo)
    #     L = get_layer_for_y(float(py))
    #     CX, CZ, A, B = L["cx"], L["cz"], L["rx"], L["rz"]
    #     nx = (xb - CX) / (A*A)
    #     nz = (zb - CZ) / (B*B)
    #     n = np.array([nx, 0.0, nz], dtype=float)
    #     n /= (np.linalg.norm(n) + 1e-12)
    #     return n

    # # Placas del acantilado (OBB) – se pegan a la ladera usando un offset sobre la normal
    # def add_prism_side(px, py, pz, w, d, h, rx, ry, rz, mat=rock_dark, bury=0.35):
    #     bx, bz = ellipse_boundary_from_dir(px, py, pz)
    #     n = ellipse_normal_at(bx, py, bz)
    #     # Colocar el centro ligeramente fuera de la superficie, enterrando 'bury'
    #     off = max(0.05, (d * 0.5) - bury)
    #     cx = bx + n[0] * off
    #     cz = bz + n[2] * off
    #     pos = to_world([cx, py, cz])
    #     half_sizes = [size_scaled(w)/2.0, size_scaled(h)/2.0, size_scaled(d)/2.0]
    #     rend.scene.append(OrientedBox(position=pos, half_sizes=half_sizes, rotation=deg(rx, ry, rz), material=mat))

    # # Colocar algunas placas destacadas y luego esparcir más por capa
    # add_prism_side(12, 5, 2, 3, 1, 9, 0, 18, 6, bury=0.5)
    # add_prism_side(-9, 3, -5, 4, 1.2, 8, 0, -22, -4, bury=0.5)
    # add_prism_side(6, 6, -10, 2.5, 0.8, 7, 0, -5, 12, bury=0.45)
    # add_prism_side(-14, 4.5, 3, 2.8, 0.9, 8.5, 0, 12, -8, bury=0.45)

    # # Cornisas de roca (prismas delgados)
    # add_prism_side(8, 8.5, 7, 6, 2.5, 0.8, -6, 30, 3, mat=rock, bury=0.4)
    # add_prism_side(-7, 9, -6, 5, 2, 0.7, 5, -24, -2, mat=rock, bury=0.35)
    # add_prism_side(3, 7.8, -11, 4.5, 2, 0.7, -4, -12, 5, mat=rock, bury=0.35)

    # # Protuberancias de erosión (elipsoides) – pegadas a la ladera de la isla
    # def add_bump_side(px, py, pz, rx, ry, rz, rx_deg=0, ry_deg=0, rz_deg=0, mat=rock_light, bury_factor=0.35):
    #     bx, bz = ellipse_boundary_from_dir(px, py, pz)
    #     n = ellipse_normal_at(bx, py, bz)
    #     r_off = max(0.1, min(rx, rz) * max(0.15, 0.5 - bury_factor))
    #     cx = bx + n[0] * r_off
    #     cz = bz + n[2] * r_off
    #     pos = to_world([cx, py, cz])
    #     radii = [size_scaled(rx), size_scaled(ry), size_scaled(rz)]
    #     rend.scene.append(Ellipsoid(position=pos, radii=radii, material=mat, rotation=deg(rx_deg, ry_deg, rz_deg)))

    # # Esparcir prismas y protuberancias por capas para cubrir la isla
    # random.seed(42)

    # def sample_skewed(a, b, skew=1.6):
    #     # Sesgo hacia 'a' cuando skew>1 (tamaños pequeños más probables)
    #     t = random.random() ** skew
    #     return a + (b - a) * t

    # def scatter_prisms_for_layer(L, count=12, y_jitter=0.5, w_range=(1.6, 3.2), d_range=(0.5, 1.1), h_range=(3.5, 8.5), bury=0.45, skew=1.6):
    #     rx, rz = L["rx"], L["rz"]
    #     cx, cz = L["cx"], L["cz"]
    #     y_center, h = L["y"], L["h"]
    #     for i in range(count):
    #         ang = (2 * np.pi) * (i / count) + random.uniform(-0.08, 0.08)
    #         px = cx + rx * np.cos(ang)
    #         pz = cz + rz * np.sin(ang)
    #         py = y_center + random.uniform(-min(y_jitter, h*0.35), min(y_jitter, h*0.35))
    #         w = sample_skewed(w_range[0], w_range[1], skew)
    #         d = sample_skewed(d_range[0], d_range[1], skew)
    #         ht = sample_skewed(h_range[0], h_range[1], skew)
    #         # Orientar aproximadamente tangente (yaw ~ ang) con ligera inclinación
    #         ry = np.degrees(ang) + random.uniform(-12, 12)
    #         rx_tilt = random.uniform(-6, 6)
    #         rz_tilt = random.uniform(-6, 6)
    #         add_prism_side(px, py, pz, w, d, ht, rx_tilt, ry, rz_tilt, mat=rock_dark, bury=bury)

    # def scatter_bumps_for_layer(L, count=10, y_jitter=0.5, r_ranges=((0.8,1.5),(0.6,1.2),(0.7,1.4)), bury_factor=0.4, skew=1.7):
    #     rx, rz = L["rx"], L["rz"]
    #     cx, cz = L["cx"], L["cz"]
    #     y_center, h = L["y"], L["h"]
    #     for i in range(count):
    #         ang = (2 * np.pi) * (i / count) + random.uniform(-0.06, 0.06)
    #         px = cx + rx * np.cos(ang)
    #         pz = cz + rz * np.sin(ang)
    #         py = y_center + random.uniform(-min(y_jitter, h*0.35), min(y_jitter, h*0.35))
    #         rX = sample_skewed(r_ranges[0][0], r_ranges[0][1], skew)
    #         rY = sample_skewed(r_ranges[1][0], r_ranges[1][1], skew)
    #         rZ = sample_skewed(r_ranges[2][0], r_ranges[2][1], skew)
    #         rz_deg = random.uniform(-12, 12)
    #         add_bump_side(px, py, pz, rX, rY, rZ, rz_deg=rz_deg, mat=rock_light, bury_factor=bury_factor)

    # add_bump_side(5, 4, 11, 1.2, 1.0, 1.0, bury_factor=0.5)
    # add_bump_side(-13, 2.5, 1, 1.5, 1.1, 1.2, bury_factor=0.5)
    # add_bump_side(10, 6, -8, 1.0, 0.9, 1.0, rz_deg=10, bury_factor=0.45)
    # add_bump_side(-6, 5.2, 9, 1.2, 1.0, 1.1, rz_deg=-8, bury_factor=0.45)

    # # Scatter coverage across layers with per-layer tuning (keep top cleaner)
    # for idx, L in enumerate(layer_specs):
    #     if idx == 0:  # top rim
    #         scatter_prisms_for_layer(L, count=3, y_jitter=0.2, w_range=(1.2, 2.2), d_range=(0.4, 0.9), h_range=(2.5, 5.0), bury=0.55, skew=2.0)
    #         scatter_bumps_for_layer(L, count=2, y_jitter=0.2, r_ranges=((0.6,1.1),(0.5,0.9),(0.6,1.0)), bury_factor=0.55, skew=2.0)
    #     elif idx == 1:  # second rim
    #         # Slightly reduced counts to clean up
    #         scatter_prisms_for_layer(L, count=3, y_jitter=0.25, w_range=(1.3, 2.4), d_range=(0.5, 1.0), h_range=(3.0, 5.5), bury=0.55, skew=1.9)
    #         scatter_bumps_for_layer(L, count=2, y_jitter=0.25, r_ranges=((0.7,1.2),(0.5,1.0),(0.7,1.1)), bury_factor=0.5, skew=1.9)
    #     elif idx == 2:  # thick mid ring
    #         scatter_prisms_for_layer(L, count=7, y_jitter=0.5, w_range=(1.6, 3.0), d_range=(0.5, 1.2), h_range=(4.0, 8.0), bury=0.5, skew=1.7)
    #         scatter_bumps_for_layer(L, count=8, y_jitter=0.6, r_ranges=((0.8,1.5),(0.6,1.2),(0.7,1.4)), bury_factor=0.45, skew=1.8)
    #     elif idx == 3:  # mid-lower
    #         scatter_prisms_for_layer(L, count=9, y_jitter=0.6, w_range=(1.8, 3.2), d_range=(0.6, 1.2), h_range=(4.5, 8.5), bury=0.5, skew=1.6)
    #         scatter_bumps_for_layer(L, count=9, y_jitter=0.6, r_ranges=((0.9,1.6),(0.7,1.3),(0.8,1.5)), bury_factor=0.45, skew=1.7)
    #     else:  # lower layers
    #         scatter_prisms_for_layer(L, count=9, y_jitter=0.6, w_range=(1.8, 3.0), d_range=(0.6, 1.1), h_range=(4.0, 8.0), bury=0.5, skew=1.6)
    #         scatter_bumps_for_layer(L, count=9, y_jitter=0.7, r_ranges=((0.9,1.6),(0.7,1.3),(0.8,1.5)), bury_factor=0.45, skew=1.7)

    # # Montículos superiores – pequeños para mantener legibilidad del borde
    rim_center_y = to_world([0, 13, 0])[1]
    rim_top_y = rim_center_y + size_scaled(0.6) * 0.5
    # mound_h = size_scaled(0.5)
    # rend.scene.append(EllipticCylinder(position=[to_world([2, 0, -1])[0], rim_top_y + mound_h * 0.5, to_world([2, 0, -1])[2]], radii_xz=[size_scaled(1.2), size_scaled(0.9)], height=mound_h, material=rock))
    # rend.scene.append(Ellipsoid(position=[to_world([-3.5, 0, 2.2])[0], rim_top_y + size_scaled(0.5), to_world([-3.5, 0, 2.2])[2]], radii=[size_scaled(0.7), size_scaled(0.5), size_scaled(0.6)], material=rock_light))

    # Estatua humanoide con primitivas, colocada sobre el borde superior y mirando al Noroeste (yaw = +45°)
    yaw_nw = 45.0
    statue_scale = 4.0 * (2.0/3.0)
    statue_offset_x_rel = -1.5  

    # Ayudante para componer posición de mundo con Y de mundo personalizada
    def world_pos(x_rel: float, y_world: float, z_rel: float):
        # Aplicar offset lateral relativo para mover la estatua a la izquierda
        px, _, pz = to_world([x_rel + statue_offset_x_rel, 0, z_rel])
        return [px, y_world, pz]

    base_y = rim_top_y  # los pies tocan la superficie del borde

    # Pies (bloques delgados)
    foot_h = size_scaled(0.3) * statue_scale
    foot_half = [size_scaled(0.35) * statue_scale / 2.0, foot_h/2.0, size_scaled(0.7) * statue_scale / 2.0]
    foot_y = base_y + foot_half[1]
    foot_x_rel = 0.6 * statue_scale
    # Pie izquierdo y derecho (rotados para alinear con la dirección)
    rend.scene.append(OrientedBox(position=world_pos(-foot_x_rel, foot_y, 4.0), half_sizes=foot_half, rotation=deg(0, yaw_nw, 0), material=statue_mat))
    rend.scene.append(OrientedBox(position=world_pos(+foot_x_rel, foot_y, 4.0), half_sizes=foot_half, rotation=deg(0, yaw_nw, 0), material=statue_mat))

    # Piernas (cilindros verticales)
    leg_h = size_scaled(3.4) * statue_scale
    leg_r = size_scaled(0.35) * statue_scale
    leg_y = base_y + foot_h + leg_h/2.0
    rend.scene.append(Cylinder(position=world_pos(-foot_x_rel, leg_y, 4.0), radius=leg_r, height=leg_h, material=statue_mat, rotation=deg(0, yaw_nw, 0)))
    rend.scene.append(Cylinder(position=world_pos(+foot_x_rel, leg_y, 4.0), radius=leg_r, height=leg_h, material=statue_mat, rotation=deg(0, yaw_nw, 0)))

    # Torso (elipsoide)
    torso_rx, torso_ry, torso_rz = size_scaled(1.1) * statue_scale, size_scaled(1.7) * statue_scale, size_scaled(0.8) * statue_scale
    torso_y = base_y + foot_h + leg_h + torso_ry
    rend.scene.append(Ellipsoid(position=world_pos(0.0, torso_y, 4.0), radii=[torso_rx, torso_ry, torso_rz], material=statue_mat, rotation=deg(0, yaw_nw, 0)))

    # Cabeza (elipsoide)
    head_rx, head_ry, head_rz = size_scaled(0.55) * statue_scale, size_scaled(0.75) * statue_scale, size_scaled(0.55) * statue_scale
    neck_gap = size_scaled(0.2) * statue_scale
    head_y = torso_y + torso_ry + neck_gap + head_ry
    rend.scene.append(Ellipsoid(position=world_pos(0.0, head_y, 4.0), radii=[head_rx, head_ry, head_rz], material=statue_mat, rotation=deg(0, yaw_nw, 0)))

    # Brazos (cilindros) colgando con ligera inclinación
    arm_r = size_scaled(0.25) * statue_scale
    arm_h = size_scaled(2.6) * statue_scale
    shoulder_y = torso_y + torso_ry*0.6
    arm_y = shoulder_y - arm_h/2.0
    shoulder_x = size_scaled(1.2) * statue_scale
    # Pequeño roll hacia afuera (rx) y yaw hacia la dirección de mirada
    rend.scene.append(Cylinder(position=world_pos(-shoulder_x, arm_y, 4.0), radius=arm_r, height=arm_h, material=statue_mat, rotation=deg(6, yaw_nw, 0)))
    rend.scene.append(Cylinder(position=world_pos(+shoulder_x, arm_y, 4.0), radius=arm_r, height=arm_h, material=statue_mat, rotation=deg(-6, yaw_nw, 0)))

    # Detalles de capa (estatua encapuchada)
    # Cuerpo de la capa: elipsoide más grande que envuelve el torso
    cloak_rx, cloak_ry, cloak_rz = torso_rx * 1.6, torso_ry * 1.6, max(torso_rz * 1.8, torso_rx * 1.2)
    cloak_y = torso_y - torso_ry * 0.2
    rend.scene.append(Ellipsoid(position=world_pos(0.0, cloak_y, 4.0), radii=[cloak_rx, cloak_ry, cloak_rz], material=statue_mat, rotation=deg(0, yaw_nw, 0)))

    # Falda de la capa: cilindro elíptico corto alrededor de las piernas
    skirt_h = size_scaled(1.6) * statue_scale
    skirt_rx, skirt_rz = max(leg_r * 5.0, size_scaled(1.6) * statue_scale), max(leg_r * 4.0, size_scaled(1.4) * statue_scale)
    skirt_center_y = base_y + foot_h + (skirt_h * 0.5)
    rend.scene.append(EllipticCylinder(position=world_pos(0.0, skirt_center_y, 4.0), radii_xz=[skirt_rx, skirt_rz], height=skirt_h, material=statue_mat, rotation=deg(0, yaw_nw, 0)))

    # Capucha: elipsoide que envuelve la cabeza, ligeramente adelantada en la dirección de mirada
    import math as _math
    yaw_r = _math.radians(yaw_nw)
    fwd_x = _math.sin(yaw_r)
    fwd_z = _math.cos(yaw_r)
    hood_rx, hood_ry, hood_rz = head_rx * 1.3, head_ry * 1.25, head_rz * 1.3
    hood_off_rel = 0.25 * statue_scale
    rend.scene.append(Ellipsoid(position=world_pos(fwd_x * hood_off_rel, head_y + head_ry * 0.15, 4.0 - fwd_z * hood_off_rel), radii=[hood_rx, hood_ry, hood_rz], material=statue_mat, rotation=deg(0, yaw_nw, 0)))

    # Pliegues de la capa en hombros: OBBs delgados
    fold_w, fold_d, fold_h = size_scaled(0.6) * statue_scale, size_scaled(0.3) * statue_scale, size_scaled(1.2) * statue_scale
    fold_y = shoulder_y
    shoulder_x_rel = 1.2 * statue_scale
    rend.scene.append(OrientedBox(position=world_pos(-shoulder_x_rel*0.9, fold_y, 4.0), half_sizes=[fold_w/2.0, fold_h/2.0, fold_d/2.0], rotation=deg(-10, yaw_nw, 8), material=statue_mat))
    rend.scene.append(OrientedBox(position=world_pos(+shoulder_x_rel*0.9, fold_y, 4.0), half_sizes=[fold_w/2.0, fold_h/2.0, fold_d/2.0], rotation=deg(10, yaw_nw, -8), material=statue_mat))

    # Brazos detallados con articulaciones (cápsulas) y manos
    upper_len_rel = 1.6 * statue_scale
    fore_len_rel = 1.4 * statue_scale
    elbow_drop = size_scaled(0.6) * statue_scale
    wrist_drop = size_scaled(0.5) * statue_scale
    right_vec = np.array([_math.cos(yaw_r), 0.0, -_math.sin(yaw_r)])

    def arm_chain(side=1):
        sx = side  # +1 derecha, -1 izquierda en coords relativas
        sh_x_rel = shoulder_x_rel * sx
        # Hombro, codo, muñeca en coordenadas relativas (x,z), y en world
        elbow_x_rel = sh_x_rel + fwd_x * (upper_len_rel*0.5)
        elbow_z_rel = 4.0 - fwd_z * (upper_len_rel*0.5)
        wrist_x_rel = sh_x_rel + fwd_x * (upper_len_rel + fore_len_rel*0.4)
        wrist_z_rel = 4.0 - fwd_z * (upper_len_rel + fore_len_rel*0.4)
        shoulder_world = world_pos(sh_x_rel, shoulder_y, 4.0)
        elbow_world = world_pos(elbow_x_rel, shoulder_y - elbow_drop, elbow_z_rel)
        wrist_world = world_pos(wrist_x_rel, (shoulder_y - elbow_drop) - wrist_drop, wrist_z_rel)
        rad = size_scaled(0.22) * statue_scale
        rend.scene.append(Capsule(point_a=shoulder_world, point_b=elbow_world, radius=rad, material=statue_mat))
        rend.scene.append(Capsule(point_a=elbow_world, point_b=wrist_world, radius=rad*0.95, material=statue_mat))
        # Mano
        hand_r = size_scaled(0.3) * statue_scale
        rend.scene.append(Sphere(position=wrist_world, radius=hand_r, material=statue_mat))

    arm_chain(side=+1)
    arm_chain(side=-1)

    # Rodilleras y botas
    knee_y = base_y + foot_h + leg_h*0.45
    knee_r = size_scaled(0.35) * statue_scale
    rend.scene.append(Ellipsoid(position=world_pos(-foot_x_rel, knee_y, 4.0), radii=[knee_r, knee_r*0.7, knee_r], material=statue_mat))
    rend.scene.append(Ellipsoid(position=world_pos(+foot_x_rel, knee_y, 4.0), radii=[knee_r, knee_r*0.7, knee_r], material=statue_mat))
    boot_h = size_scaled(0.6) * statue_scale
    boot_half = [size_scaled(0.5) * statue_scale / 2.0, boot_h/2.0, size_scaled(0.9) * statue_scale / 2.0]
    boot_y = base_y + boot_half[1]
    rend.scene.append(OrientedBox(position=world_pos(-foot_x_rel, boot_y, 4.0), half_sizes=boot_half, rotation=deg(0, yaw_nw, 0), material=statue_mat))
    rend.scene.append(OrientedBox(position=world_pos(+foot_x_rel, boot_y, 4.0), half_sizes=boot_half, rotation=deg(0, yaw_nw, 0), material=statue_mat))
    # Punta del pie
    toe_r = size_scaled(0.3) * statue_scale
    rend.scene.append(Sphere(position=world_pos(-foot_x_rel + fwd_x*0.5*statue_scale, base_y + toe_r*0.6, 4.0 - fwd_z*0.5*statue_scale), radius=toe_r, material=statue_mat))
    rend.scene.append(Sphere(position=world_pos(+foot_x_rel + fwd_x*0.5*statue_scale, base_y + toe_r*0.6, 4.0 - fwd_z*0.5*statue_scale), radius=toe_r, material=statue_mat))

    # Cinturón y medallón
    belt_h = size_scaled(0.25) * statue_scale
    belt_rx, belt_rz = size_scaled(1.3) * statue_scale, size_scaled(1.0) * statue_scale
    belt_y = base_y + foot_h + leg_h + belt_h
    rend.scene.append(EllipticCylinder(position=world_pos(0.0, belt_y, 4.0), radii_xz=[belt_rx, belt_rz], height=belt_h, material=statue_mat, rotation=deg(0, yaw_nw, 0)))
    med_r = size_scaled(0.35) * statue_scale
    rend.scene.append(Disk(position=world_pos(fwd_x*0.2*statue_scale, torso_y, 4.0 - fwd_z*0.2*statue_scale), normal=[0,1,0], radius=med_r, material=statue_mat))

    # Protector de hombros (hombreras) – elipsoides ensanchados
    pauld_r = size_scaled(0.6) * statue_scale
    rend.scene.append(Ellipsoid(position=world_pos(-shoulder_x_rel, shoulder_y + pauld_r*0.4, 4.0), radii=[pauld_r*1.3, pauld_r*0.7, pauld_r], material=statue_mat, rotation=deg(0, yaw_nw, -15)))
    rend.scene.append(Ellipsoid(position=world_pos(+shoulder_x_rel, shoulder_y + pauld_r*0.4, 4.0), radii=[pauld_r*1.3, pauld_r*0.7, pauld_r], material=statue_mat, rotation=deg(0, yaw_nw, 15)))

    # Brazaletes cerca de las muñecas
    br_h = size_scaled(0.35) * statue_scale
    br_r = size_scaled(0.35) * statue_scale
    # usar las muñecas calculadas en arm_chain: replicar aproximación rápida
    for sx in (-1, 1):
        wx_rel = (shoulder_x_rel * sx) + fwd_x * (upper_len_rel + fore_len_rel*0.4)
        wz_rel = 4.0 - fwd_z * (upper_len_rel + fore_len_rel*0.4)
        wy = (shoulder_y - elbow_drop) - wrist_drop
        rend.scene.append(Cylinder(position=world_pos(wx_rel, wy, wz_rel), radius=br_r, height=br_h, material=statue_mat, rotation=deg(0, yaw_nw, 0)))

    # Dedos estilizados (pequeños conos) apuntando hacia la dirección de mirada
    finger_h = size_scaled(0.35) * statue_scale
    finger_r = size_scaled(0.12) * statue_scale
    for sx in (-1, 1):
        base_x = (shoulder_x_rel * sx) + fwd_x * (upper_len_rel + fore_len_rel*0.4)
        base_z = 4.0 - fwd_z * (upper_len_rel + fore_len_rel*0.4)
        base_y = (shoulder_y - elbow_drop) - wrist_drop
        for i in range(3):
            offx = (i - 1) * size_scaled(0.12) * statue_scale
            rend.scene.append(Cone(position=world_pos(base_x + offx, base_y + finger_h*0.4, base_z), radius=finger_r, height=finger_h, material=statue_mat))

    # Borde rígido de la capucha
    rim_rx = head_rx * 1.45
    rim_ry = head_ry * 0.25
    rim_rz = head_rz * 1.45
    rim_off = hood_off_rel + 0.1 * statue_scale
    rend.scene.append(Ellipsoid(position=world_pos(fwd_x * rim_off, head_y + head_ry * 0.25, 4.0 - fwd_z * rim_off), radii=[rim_rx, rim_ry, rim_rz], material=statue_mat, rotation=deg(0, yaw_nw, 0)))

    # Pliegues adicionales al frente de la capa
    for s in (-1, 1):
        rend.scene.append(OrientedBox(position=world_pos(s*0.5*statue_scale, skirt_center_y + skirt_h*0.2, 4.0 - fwd_z*0.2*statue_scale), half_sizes=[size_scaled(0.25)*statue_scale, size_scaled(0.9)*statue_scale/2.0, size_scaled(0.25)*statue_scale], rotation=deg(6*s, yaw_nw, 0), material=statue_mat))

    # Drapeado trasero de la capa
    back_rx, back_ry, back_rz = skirt_rx*0.9, skirt_h*0.6, skirt_rz*0.95
    rend.scene.append(Ellipsoid(position=world_pos(-0.2*statue_scale, base_y + foot_h + skirt_h*0.9, 4.0 + 0.4*statue_scale), radii=[back_rx, back_ry, back_rz], material=statue_mat, rotation=deg(0, yaw_nw, 0)))

    # Suelo: plano infinito por debajo de la isla, usando la misma textura que los pilares
    ground_y = to_world([0, -15, 0])[1]  # un poco más abajo que las bases de los pilares
    rend.scene.append(Plane(position=[0.0, ground_y, 0.0], normal=[0, 1, 0], material=pillar))

    # Rocas y protuberancias sobre el suelo (plano infinito)
    # Usar SIEMPRE la textura del plano (pilares) para estas rocas
    def add_ground_rock_sphere(x_rel, z_rel, r_rel, bury=0.3, mat=pillar):
        r = size_scaled(r_rel)
        y = ground_y + r * (1.0 - bury)
        rend.scene.append(Sphere(position=world_pos(x_rel, y, z_rel), radius=r, material=mat))

    def add_ground_rock_ellipsoid(x_rel, z_rel, rx_rel, ry_rel, rz_rel, bury=0.4, mat=pillar_light):
        rx, ry, rz = size_scaled(rx_rel), size_scaled(ry_rel), size_scaled(rz_rel)
        y = ground_y + ry * (1.0 - bury)
        rend.scene.append(Ellipsoid(position=world_pos(x_rel, y, z_rel), radii=[rx, ry, rz], material=mat))

    def add_ground_flat_disk(x_rel, z_rel, rad_rel, mat=pillar_dark):
        # Disco plano pegado al suelo (tipo losa)
        rad = size_scaled(rad_rel)
        rend.scene.append(Disk(position=world_pos(x_rel, ground_y + 1e-3, z_rel), normal=[0,1,0], radius=rad, material=mat))

    # Colocación base (usando materiales de pilar) y luego dispersión aleatoria
    add_ground_rock_sphere(-10, -6, 1.2, bury=0.45, mat=pillar_dark)
    add_ground_rock_sphere(9, -7, 0.9, bury=0.35, mat=pillar)
    add_ground_rock_ellipsoid(-6, -9, 1.6, 0.9, 1.2, bury=0.5, mat=pillar_light)
    add_ground_rock_ellipsoid(12, -5, 1.2, 0.8, 1.0, bury=0.4, mat=pillar)
    add_ground_flat_disk(6, -8, 1.8, mat=pillar_dark)
    add_ground_flat_disk(-12, -4, 1.4, mat=pillar)

    # Dispersión amplia de rocas por el plano (todas con texturas de pilar)
    random.seed(7)
    def scatter_ground_rocks(count=28, x_range=(-16, 16), z_range=(-16, -2)):
        for _ in range(count):
            x = random.uniform(x_range[0], x_range[1])
            z = random.uniform(z_range[0], z_range[1])
            t = random.random()
            mat = random.choice([pillar, pillar_dark, pillar_light])
            if t < 0.35:
                add_ground_rock_sphere(x, z, random.uniform(0.5, 1.6), bury=random.uniform(0.3, 0.6), mat=mat)
            elif t < 0.7:
                add_ground_rock_ellipsoid(x, z, random.uniform(0.6, 1.8), random.uniform(0.4, 1.0), random.uniform(0.6, 1.6), bury=random.uniform(0.3, 0.6), mat=mat)
            elif t < 0.85:
                add_ground_flat_disk(x, z, random.uniform(0.8, 2.2), mat=mat)
            elif t < 0.93:
                # Conos tumbados simulando rocas puntiagudas
                cone_h = size_scaled(random.uniform(1.2, 2.2))
                cone_r = size_scaled(random.uniform(0.4, 1.0))
                rend.scene.append(Cone(position=world_pos(x, ground_y + cone_h*0.5, z), radius=cone_r, height=cone_h, material=mat))
            else:
                # Cápsulas cortas como cantos rodados
                r = size_scaled(random.uniform(0.3, 0.8))
                a = world_pos(x, ground_y + r, z)
                b = world_pos(x + random.uniform(-0.6, 0.6), ground_y + r + size_scaled(random.uniform(0.4, 1.2)), z + random.uniform(-0.6, 0.6))
                rend.scene.append(Capsule(point_a=a, point_b=b, radius=r, material=mat))
    scatter_ground_rocks()

    # Algunos bloques cúbicos semienterrados
    cube_edge = size_scaled(1.8)
    rend.scene.append(Cube(position=world_pos(-8, ground_y + cube_edge*0.25, -7), edge=cube_edge, material=rock_dark))

    # Nuevas formas: Cápsula y Cono, visibles en el plano del suelo
    cap_r = size_scaled(0.7)
    cap_a = world_pos(4.5, ground_y + cap_r, -10)
    cap_b = world_pos(4.5, ground_y + cap_r + size_scaled(2.5), -10)
    rend.scene.append(Capsule(point_a=cap_a, point_b=cap_b, radius=cap_r, material=pillar_light))

    cone_h = size_scaled(3.2)
    cone_r = size_scaled(1.2)
    rend.scene.append(Cone(position=world_pos(-3.5, ground_y + cone_h*0.5, -11), radius=cone_r, height=cone_h, material=pillar))

    # Pilares de fondo (cilindros) – la y de la especificación es la base; convertir a centro sumando h/2
    def add_pillar(px, base_y, pz, radius, height):
        h = size_scaled_pillar(height)
        center_y = base_y + height/2.0
        pos = to_world([px, center_y, pz])
        rend.scene.append(Cylinder(position=pos, radius=size_scaled_pillar(radius), height=h, material=random.choice([pillar, pillar_dark, pillar_light])))

    add_pillar(-40, -10, -36, 3, 60)   # Near-left
    add_pillar(-42, -11, -36, 5, 40)    # Near-right
    add_pillar(-40, -14, -36, 4, 64)  # Mid-left
    add_pillar(-40, -14, -36, 4, 59)  # Mid-left

    add_pillar(-32, -14, -36, 6, 28)  # Mid-left
    add_pillar(-32, -14, -36, 4, 42)  # Mid-left

    add_pillar(45, -10, -36, 3, 40)   # Mid-right
    add_pillar(42, -12, -36, 2, 33) # Rear-left
    add_pillar(40, -13, -36, 4, 25)  # Rear-right


    # Elementos en primer plano
    #add_bump_side(-7, 1.2, 4, 1.6, 0.8, 1.2, rz_deg=12, mat=rock_light)
    rend.scene.append(Cylinder(position=to_world([6, 0.8, 3]), radius=size_scaled(0.9), height=size_scaled(0.6), material=rock_dark))

    # Iluminación
    rend.lights.append(AmbientLight(intensity=0.22))
    rend.lights.append(DirectionalLight(direction=[-0.4, -1, -0.3], intensity=0.85))
    rend.lights.append(DirectionalLight(direction=[0.5, -0.8, -0.4], intensity=0.55, color=[0.95, 0.98, 1]))

    # Renderizado
    rend.glRender()
    out = "island_scene.bmp"
    GenerateBMP(out, WIDTH, HEIGHT, 3, rend.frameBuffer)
    print(f"Saved {out}")
    pygame.quit()


if __name__ == "__main__":
    main()
