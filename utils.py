import os
import random
import math
import pygame
import constants


def load_font(path=None, size=32, fallback_names=None):
    fallback_names = fallback_names or ["dejavusans", "arial", "noto sans", "liberation sans", "sans"]
    if path:
        try:
            font = pygame.font.Font(path, size)
            print(f"Loaded font from {path}")
            return font
        except Exception as e:
            print(f"Failed to load font {path}: {e}")
    for name in fallback_names:
        try:
            font_path = pygame.font.match_font(name)
            if font_path:
                font = pygame.font.Font(font_path, size)
                print(f"Using system font '{name}' from {font_path}")
                return font
        except Exception:
            pass
    print("Using default pygame font")
    return pygame.font.Font(None, size)


def draw_text(text, pos, color=(255, 255, 255), size=40, font=None, glow_color=None, glow_radius=0):
    if font is None:
        font = load_font(None, size)
    if glow_color and glow_radius > 0:
        glow_surface = font.render(text, True, glow_color)
        for dx in range(-glow_radius, glow_radius + 1):
            for dy in range(-glow_radius, glow_radius + 1):
                if dx == 0 and dy == 0:
                    continue
                constants.screen.blit(glow_surface, (pos[0] + dx, pos[1] + dy))
    constants.screen.blit(font.render(text, True, color), pos)


def draw_text_center(text, y, color=(255, 255, 255), size=40, font=None, glow_color=None, glow_radius=0):
    if font is None:
        font = load_font(None, size)
    text_surface = font.render(text, True, color)
    x = constants.WIDTH // 2 - text_surface.get_width() // 2
    if glow_color and glow_radius > 0:
        glow_surface = font.render(text, True, glow_color)
        for dx in range(-glow_radius, glow_radius + 1):
            for dy in range(-glow_radius, glow_radius + 1):
                if dx == 0 and dy == 0:
                    continue
                constants.screen.blit(glow_surface, (x + dx, y + dy))
    constants.screen.blit(text_surface, (x, y))


def start_ambient_sound():
    if not pygame.mixer.get_init():
        return
    if pygame.mixer.music.get_busy():
        return
    try:
        pygame.mixer.music.load(os.path.join(constants.ASSETS_DIR, "sound", "map.mp3"))
        pygame.mixer.music.set_volume(constants.SETTINGS["music_volume"])
        pygame.mixer.music.play(loops=-1, fade_ms=1200)
    except pygame.error as e:
        print(f"Ambient sound disabled: {e}")


def stop_ambient_sound():
    if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
        pygame.mixer.music.fadeout(500)


def weapon_upgrade_level(weapon_key, upgrade_key):
    return constants.weapon_upgrades.get(weapon_key, {}).get(upgrade_key, 0)


def weapon_upgrade_cost(weapon_key, upgrade_key):
    from assets import WEAPONS
    level = weapon_upgrade_level(weapon_key, upgrade_key)
    costs = constants.UPGRADE_COSTS[upgrade_key]
    if level >= len(costs):
        return None
    base_cost = costs[level]
    return base_cost + WEAPONS[weapon_key]["cost"] // 5


def weapon_damage(weapon_key):
    from assets import WEAPONS
    return WEAPONS[weapon_key]["damage"] + weapon_upgrade_level(weapon_key, "damage")


def weapon_magazine_size(weapon_key):
    from assets import WEAPONS
    base = WEAPONS[weapon_key]["magazine"]
    return base + int(base * 0.25) * weapon_upgrade_level(weapon_key, "magazine")


def weapon_reload_time(weapon_key):
    from assets import WEAPONS
    base = WEAPONS[weapon_key]["reload_time"]
    return max(300, int(base * (1 - 0.15 * weapon_upgrade_level(weapon_key, "reload"))))


def tr(key):
    language = constants.SETTINGS.get("language", "en")
    return constants.TEXT.get(language, constants.TEXT["en"]).get(key, constants.TEXT["en"].get(key, key))


def weapon_display_name(weapon_key):
    from assets import WEAPONS
    name_key = f"weapon_{weapon_key}"
    language = constants.SETTINGS.get("language", "en")
    return constants.TEXT.get(language, constants.TEXT["en"]).get(name_key, WEAPONS.get(weapon_key, {}).get("name", weapon_key))


def cycle_language(step=1):
    codes = list(constants.LANGUAGES.keys())
    current = constants.SETTINGS.get("language", "en")
    index = codes.index(current) if current in codes else 0
    constants.SETTINGS["language"] = codes[(index + step) % len(codes)]


def tint_surface(surface, color):
    tinted = surface.copy()
    tinted.fill(color, special_flags=pygame.BLEND_MULT)
    return tinted


HUD_FONT_SIZE = 20
font = None

DEFAULT_UNICODE_FALLBACKS = [
    "dejavusans",
    "noto sans",
    "liberation sans",
    "arial",
    "sans",
]

MONO_UNICODE_FALLBACKS = [
    "dejavusansmono",
    "liberation mono",
    "courier new",
    "monospace",
]

ui_font = None
title_font = None
stats_font = None

def init_fonts():
    global font, ui_font, title_font, stats_font
    font = load_font(None, HUD_FONT_SIZE)
    ui_font = load_font(None, 48, fallback_names=DEFAULT_UNICODE_FALLBACKS)
    title_font = load_font(None, 72, fallback_names=DEFAULT_UNICODE_FALLBACKS)
    stats_font = load_font(None, 32, fallback_names=MONO_UNICODE_FALLBACKS)
