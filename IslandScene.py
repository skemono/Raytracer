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
from figures import OrientedBox, Ellipsoid, Cylinder, EllipticCylinder, deg

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

    # Ayudante para componer posición de mundo con Y de mundo personalizada
    def world_pos(x_rel: float, y_world: float, z_rel: float):
        px, _, pz = to_world([x_rel, 0, z_rel])
        return [px, y_world, pz]

    base_y = rim_top_y  # los pies tocan la superficie del borde

    # Pies (bloques delgados)
    foot_h = size_scaled(0.3)
    foot_half = [size_scaled(0.35)/2.0, foot_h/2.0, size_scaled(0.7)/2.0]
    foot_y = base_y + foot_half[1]
    foot_x_offset = size_scaled(0.6)
    # Pie izquierdo y derecho (rotados para alinear con la dirección)
    rend.scene.append(OrientedBox(position=world_pos(-foot_x_offset, foot_y, 4.0), half_sizes=foot_half, rotation=deg(0, yaw_nw, 0), material=statue_mat))
    rend.scene.append(OrientedBox(position=world_pos(+foot_x_offset, foot_y, 4.0), half_sizes=foot_half, rotation=deg(0, yaw_nw, 0), material=statue_mat))

    # Piernas (cilindros verticales)
    leg_h = size_scaled(3.4)
    leg_r = size_scaled(0.35)
    leg_y = base_y + foot_h + leg_h/2.0
    rend.scene.append(Cylinder(position=world_pos(-foot_x_offset, leg_y, 4.0), radius=leg_r, height=leg_h, material=statue_mat, rotation=deg(0, yaw_nw, 0)))
    rend.scene.append(Cylinder(position=world_pos(+foot_x_offset, leg_y, 4.0), radius=leg_r, height=leg_h, material=statue_mat, rotation=deg(0, yaw_nw, 0)))

    # Torso (elipsoide)
    torso_rx, torso_ry, torso_rz = size_scaled(1.1), size_scaled(1.7), size_scaled(0.8)
    torso_y = base_y + foot_h + leg_h + torso_ry
    rend.scene.append(Ellipsoid(position=world_pos(0.0, torso_y, 4.0), radii=[torso_rx, torso_ry, torso_rz], material=statue_mat, rotation=deg(0, yaw_nw, 0)))

    # Cabeza (elipsoide)
    head_rx, head_ry, head_rz = size_scaled(0.55), size_scaled(0.75), size_scaled(0.55)
    neck_gap = size_scaled(0.2)
    head_y = torso_y + torso_ry + neck_gap + head_ry
    rend.scene.append(Ellipsoid(position=world_pos(0.0, head_y, 4.0), radii=[head_rx, head_ry, head_rz], material=statue_mat, rotation=deg(0, yaw_nw, 0)))

    # Brazos (cilindros) colgando con ligera inclinación
    arm_r = size_scaled(0.25)
    arm_h = size_scaled(2.6)
    shoulder_y = torso_y + torso_ry*0.6
    arm_y = shoulder_y - arm_h/2.0
    shoulder_x = size_scaled(1.2)
    # Pequeño roll hacia afuera (rx) y yaw hacia la dirección de mirada
    rend.scene.append(Cylinder(position=world_pos(-shoulder_x, arm_y, 4.0), radius=arm_r, height=arm_h, material=statue_mat, rotation=deg(6, yaw_nw, 0)))
    rend.scene.append(Cylinder(position=world_pos(+shoulder_x, arm_y, 4.0), radius=arm_r, height=arm_h, material=statue_mat, rotation=deg(-6, yaw_nw, 0)))

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
