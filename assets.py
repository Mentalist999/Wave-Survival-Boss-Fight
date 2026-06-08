import os
import random
import math
import xml.etree.ElementTree as ET
import pygame
import constants
from utils import tint_surface


def resolve_tmx_source_path(base_path, source):
    source_path = os.path.join(os.path.dirname(base_path), source)
    return os.path.normpath(source_path)


def load_tmx_map(path, size=None):
    tree = ET.parse(path)
    root = tree.getroot()
    tilewidth = int(root.get('tilewidth', 32))
    tileheight = int(root.get('tileheight', 32))

    gid_tiles = {}
    for tileset in root.findall('tileset'):
        firstgid = int(tileset.get('firstgid', 1))
        ts_root = tileset
        ts_path = path
        source = tileset.get('source')
        if source:
            ts_path = resolve_tmx_source_path(path, source)
            ts_tree = ET.parse(ts_path)
            ts_root = ts_tree.getroot()

        image = ts_root.find('image')
        if image is None:
            continue

        img_source = image.get('source')
        img_path = resolve_tmx_source_path(ts_path, img_source)
        tileset_img = pygame.image.load(img_path).convert_alpha()

        tw = int(ts_root.get('tilewidth', tilewidth))
        th = int(ts_root.get('tileheight', tileheight))
        columns = int(ts_root.get('columns', 0))
        count = int(ts_root.get('tilecount', 0))
        margin = int(ts_root.get('margin', 0))
        spacing = int(ts_root.get('spacing', 0))
        if columns == 0 and tw > 0:
            columns = tileset_img.get_width() // tw
        if columns == 0:
            columns = 1

        for local_id in range(count):
            gid = firstgid + local_id
            tile_x = local_id % columns
            tile_y = local_id // columns
            rect = pygame.Rect(
                margin + tile_x * (tw + spacing),
                margin + tile_y * (th + spacing),
                tw,
                th,
            )
            gid_tiles[gid] = tileset_img.subsurface(rect).copy()

    layer_chunks = []
    min_px = min_py = 0.0
    max_px = max_py = 0.0
    for layer in root.findall('layer'):
        data = layer.find('data')
        if data is None:
            continue

        offset_x = float(layer.get('offsetx', 0))
        offset_y = float(layer.get('offsety', 0))
        chunk_nodes = data.findall('chunk')
        if chunk_nodes:
            for chunk in chunk_nodes:
                x = int(chunk.get('x', 0))
                y = int(chunk.get('y', 0))
                width = int(chunk.get('width', 0))
                height = int(chunk.get('height', 0))
                gids = [int(v) for v in chunk.text.strip().replace('\n', '').split(',') if v.strip()]
                layer_chunks.append((x, y, width, height, gids, offset_x, offset_y))
                min_px = min(min_px, x * tilewidth + offset_x)
                min_py = min(min_py, y * tileheight + offset_y)
                max_px = max(max_px, (x + width) * tilewidth + offset_x)
                max_py = max(max_py, (y + height) * tileheight + offset_y)
        else:
            raw = data.text or ''
            gids = [int(v) for v in raw.strip().replace('\n', '').split(',') if v.strip()]
            width = int(data.get('width', 0))
            height = int(data.get('height', 0))
            if width and height:
                layer_chunks.append((0, 0, width, height, gids, offset_x, offset_y))
                min_px = min(min_px, offset_x)
                min_py = min(min_py, offset_y)
                max_px = max(max_px, width * tilewidth + offset_x)
                max_py = max(max_py, height * tileheight + offset_y)

    if not layer_chunks:
        raise ValueError(f'No visible tile layers found in TMX map: {path}')

    surface_width = int(math.ceil(max_px - min_px))
    surface_height = int(math.ceil(max_py - min_py))
    surface = pygame.Surface((surface_width, surface_height), pygame.SRCALPHA)

    for x, y, width, height, gids, offset_x, offset_y in layer_chunks:
        for index, gid in enumerate(gids):
            if gid == 0:
                continue
            tile = gid_tiles.get(gid)
            if tile is None:
                continue
            local_x = index % width
            local_y = index // width
            px = int(round((x * tilewidth + offset_x) - min_px + local_x * tilewidth))
            py = int(round((y * tileheight + offset_y) - min_py + local_y * tileheight))
            surface.blit(tile, (px, py))

    if size:
        surface = pygame.transform.scale(surface, size)
    return surface


def load(name, size=None):
    path = os.path.join(constants.ASSETS_DIR, name)
    if name.lower().endswith('.tmx'):
        return load_tmx_map(path, size)
    img = pygame.image.load(path).convert_alpha()
    if size:
        img = pygame.transform.scale(img, size)
    return img


def load_optional(name, size=None):
    path = os.path.join(constants.ASSETS_DIR, name)
    if not os.path.exists(path):
        return None
    return load(name, size)


def load_optional_cropped(name, max_size):
    path = os.path.join(constants.ASSETS_DIR, name)
    if not os.path.exists(path):
        return None

    img = pygame.image.load(path).convert_alpha()
    crop_rect = img.get_bounding_rect()
    if crop_rect.width > 0 and crop_rect.height > 0:
        img = img.subsurface(crop_rect).copy()

    scale = min(max_size[0] / img.get_width(), max_size[1] / img.get_height())
    size = (max(1, int(img.get_width() * scale)), max(1, int(img.get_height() * scale)))
    return pygame.transform.scale(img, size)

player_img = None
enemy_img = None
enemy_p_img = None
bullet_img = None
boss_img = None
base_map_img = None
WORLD_WIDTH = 0
WORLD_HEIGHT = 0
menu_img = None

PLAYER_PARTS = {}
PLAYER_PARTS_READY = False

WEAPON_IMAGES = {}
WEAPONS = {}


def create_weapon_image(kind, size):
    surface = pygame.Surface(size, pygame.SRCALPHA)
    width, height = size
    grip_color = (62, 42, 32)
    metal_dark = (38, 45, 48)
    metal = (82, 95, 98)
    accent = (124, 82, 54)

    if kind == "pistol":
        pygame.draw.rect(surface, metal, (3, 4, width - 10, 6))
        pygame.draw.rect(surface, metal_dark, (width - 9, 5, 8, 3))
        pygame.draw.rect(surface, grip_color, (8, 9, 6, height - 10))
        pygame.draw.rect(surface, (18, 18, 18), (5, 9, 8, 3))
    elif kind == "shotgun":
        pygame.draw.rect(surface, accent, (4, 7, width - 8, 5))
        pygame.draw.rect(surface, metal_dark, (12, 3, width - 14, 4))
        pygame.draw.rect(surface, grip_color, (5, 10, 9, height - 11))
    elif kind == "rifle":
        pygame.draw.rect(surface, metal_dark, (5, 6, width - 7, 5))
        pygame.draw.rect(surface, accent, (12, 11, 15, 4))
        pygame.draw.rect(surface, grip_color, (7, 11, 8, height - 10))
        pygame.draw.rect(surface, metal, (width - 8, 4, 6, 3))
    elif kind == "sniper":
        pygame.draw.rect(surface, metal_dark, (4, 7, width - 4, 4))
        pygame.draw.rect(surface, accent, (8, 11, 20, 4))
        pygame.draw.rect(surface, metal, (18, 3, 12, 3))
        pygame.draw.rect(surface, grip_color, (8, 13, 7, height - 14))
    else:
        pygame.draw.rect(surface, (54, 86, 66), (7, 5, width - 14, 9), border_radius=4)
        pygame.draw.rect(surface, metal_dark, (width - 14, 7, 13, 5))
        pygame.draw.rect(surface, grip_color, (8, 13, 8, height - 13))

    return surface


def create_themed_map_surface(base_surface, theme, seed):
    image_name = theme.get("image")
    if image_name:
        image_path = os.path.join(constants.ASSETS_DIR, image_name)
        if os.path.exists(image_path):
            return pygame.image.load(image_path).convert()

    themed = tint_surface(base_surface, theme["tint"])
    overlay_color = theme["overlay"]
    if overlay_color[3] > 0:
        overlay = pygame.Surface(base_surface.get_size(), pygame.SRCALPHA)
        overlay.fill(overlay_color)
        themed.blit(overlay, (0, 0))

    detail_rng = random.Random(seed)
    detail = theme["detail"]
    if detail == "snow":
        for _ in range(260):
            x = detail_rng.randrange(0, base_surface.get_width())
            y = detail_rng.randrange(0, base_surface.get_height())
            radius = detail_rng.choice((1, 1, 2, 3))
            pygame.draw.circle(themed, (235, 248, 255, 78), (x, y), radius)
    elif detail == "lava":
        for _ in range(42):
            x = detail_rng.randrange(0, base_surface.get_width())
            y = detail_rng.randrange(0, base_surface.get_height())
            length = detail_rng.randrange(70, 210)
            end = (min(base_surface.get_width(), x + length), y + detail_rng.randrange(-18, 19))
            pygame.draw.line(themed, (255, 75, 18, 95), (x, y), end, detail_rng.randrange(2, 5))
            pygame.draw.line(themed, (255, 190, 45, 80), (x, y), end, 1)
    elif detail == "swamp":
        for _ in range(55):
            x = detail_rng.randrange(0, base_surface.get_width())
            y = detail_rng.randrange(0, base_surface.get_height())
            width = detail_rng.randrange(45, 120)
            height = detail_rng.randrange(18, 44)
            pygame.draw.ellipse(themed, (45, 95, 55, 68), (x, y, width, height))
    elif detail == "neon":
        neon_colors = [(255, 55, 185, 125), (65, 235, 255, 125), (185, 95, 255, 115)]
        for _ in range(32):
            x = detail_rng.randrange(0, base_surface.get_width())
            y = detail_rng.randrange(0, base_surface.get_height())
            length = detail_rng.randrange(55, 180)
            color = detail_rng.choice(neon_colors)
            pygame.draw.line(themed, color, (x, y), (x + length, y), detail_rng.randrange(2, 5))

    return themed

def init_assets():
    global player_img, enemy_img, enemy_p_img, bullet_img, boss_img, base_map_img
    global WORLD_WIDTH, WORLD_HEIGHT, menu_img, PLAYER_PARTS, PLAYER_PARTS_READY
    global WEAPON_IMAGES, WEAPONS, map_img
    
    player_img = load("player.png", (60, 60))
    enemy_img = load("enemy.png", (50, 50))
    enemy_p_img = load("enemy_p.png", (70, 70))
    bullet_img = load("bullet.png", (15, 15))
    boss_img = load("boss.png", (220, 220))
    base_map_img = load("map.tmx")
    WORLD_WIDTH, WORLD_HEIGHT = base_map_img.get_width(), base_map_img.get_height()
    menu_img = load("menu.png", (constants.WIDTH, constants.HEIGHT))
    
    PLAYER_PARTS = {
        "head": load_optional(os.path.join("player_parts", "head_hood.png"), (42, 36)),
        "body": load_optional(os.path.join("player_parts", "torso.png"), (34, 38)),
        "arm_left": load_optional(os.path.join("player_parts", "left_arm.png"), (14, 36)),
        "arm_right": load_optional(os.path.join("player_parts", "right_arm.png"), (14, 36)),
        "leg_left": load_optional(os.path.join("player_parts", "left_leg.png"), (14, 30)),
        "leg_right": load_optional(os.path.join("player_parts", "right_leg.png"), (14, 30)),
    }
    PLAYER_PARTS_READY = all(part is not None for part in PLAYER_PARTS.values())
    
    WEAPON_IMAGES = {
        "pistol": load_optional_cropped(os.path.join("weapons", "pistol.png"), (24, 18)) or create_weapon_image("pistol", (24, 12)),
        "shotgun": load_optional_cropped(os.path.join("weapons", "shotgun.png"), (48, 18)) or create_weapon_image("shotgun", (42, 16)),
        "rifle": load_optional_cropped(os.path.join("weapons", "ak47.png"), (50, 20)) or create_weapon_image("rifle", (44, 16)),
        "sniper": load_optional_cropped(os.path.join("weapons", "sniper.png"), (54, 18)) or create_weapon_image("sniper", (52, 16)),
        "rpg": load_optional_cropped(os.path.join("weapons", "rpg.png"), (54, 18)) or create_weapon_image("rpg", (52, 20)),
    }
    
    WEAPONS = {
        "pistol": {
            "name": "Pistol",
            "cost": 0,
            "magazine": 30,
            "ammo_cost": 30,
            "sprite": load("player_P.png", (60, 60)),
            "delay": 230,
            "reload_time": 900,
            "speed": 13,
            "damage": 1,
            "pellets": 1,
            "spread": 0,
            "blast_radius": 0,
        },
        "shotgun": {
            "name": "Shotgun",
            "cost": 200,
            "magazine": 8,
            "ammo_cost": 45,
            "sprite": load("Player_SH.png", (60, 60)),
            "delay": 520,
            "reload_time": 1250,
            "speed": 12,
            "damage": 1,
            "pellets": 5,
            "spread": 0.22,
            "blast_radius": 0,
        },
        "rifle": {
            "name": "Rifle",
            "cost": 400,
            "magazine": 45,
            "ammo_cost": 80,
            "sprite": load("Player_AK.png", (60, 60)),
            "delay": 90,
            "reload_time": 1550,
            "speed": 16,
            "damage": 1,
            "pellets": 1,
            "spread": 0,
            "blast_radius": 0,
        },
        "sniper": {
            "name": "Sniper Rifle",
            "cost": 600,
            "magazine": 10,
            "ammo_cost": 70,
            "sprite": load("Player_SP.png", (60, 60)),
            "delay": 650,
            "reload_time": 1800,
            "speed": 24,
            "damage": 8,
            "pellets": 1,
            "spread": 0,
            "blast_radius": 0,
            "piercing": True,
        },
        "rpg": {
            "name": "RPG",
            "cost": 800,
            "magazine": 5,
            "ammo_cost": 120,
            "sprite": load("Player_RPG.png", (60, 60)),
            "delay": 900,
            "reload_time": 2300,
            "speed": 9,
            "damage": 12,
            "pellets": 1,
            "spread": 0,
            "blast_radius": 120,
        },
    }
    
    for theme_index, theme in enumerate(constants.MAP_THEMES):
        theme["surface"] = create_themed_map_surface(base_map_img, theme, theme_index + 7)

map_img = None
