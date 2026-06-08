import os
import pygame

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
SAVE_PATH = os.path.join(BASE_DIR, "save.json")

screen = None
clock = None

WIDTH, HEIGHT = 1920, 1080

weapon_order = ["pistol", "shotgun", "rifle", "sniper", "rpg"]
unlocked_weapons = {"pistol"}
current_weapon = "pistol"
weapon_upgrades = {
    weapon_key: {"damage": 0, "magazine": 0, "reload": 0}
    for weapon_key in weapon_order
}
SETTINGS = {
    "music_volume": 0.35,
    "sfx_volume": 0.8,
    "fullscreen": True,
    "language": "en",
}
LANGUAGES = {
    "en": "English",
    "ru": "Русский",
    "uk": "Українська",
}
TEXT = {
    "en": {
        "start_game": "Start Game",
        "weapon_shop": "Weapon Shop",
        "your_points": "Your Points",
        "welcome_safe_house": "Welcome to your safe house",
        "buy_ammo": "Buy Ammo",
        "exit_house": "Exit House",
        "upgrade_damage": "Upgrade Damage",
        "upgrade_magazine": "Upgrade Magazine",
        "upgrade_reload": "Upgrade Reload",
        "rest_heal": "Rest & Heal",
        "upgrade_medkit_capacity": "Upgrade Medkit Capacity",
        "full": "Full",
        "coins": "coins",
        "plus_mag": "+1 magazine",
        "weapon_pistol": "Pistol",
        "weapon_shotgun": "Shotgun",
        "weapon_rifle": "Rifle",
        "weapon_sniper": "Sniper Rifle",
        "weapon_rpg": "RPG",
        "selected": "Selected",
        "bought_and_selected": "Bought and selected",
        "need": "Need",
        "points": "points",
        "back": "Back",
        "buy_or_select_weapon": "Buy or select a weapon",
        "owned": "Owned",
        "settings": "Settings",
        "quit": "Quit",
        "last_score": "Last Score",
        "record": "Record",
        "music_volume": "Music Volume",
        "sfx_volume": "SFX Volume",
        "fullscreen": "Fullscreen",
        "language": "Language",
        "settings_hint": "Use left/right or click to change",
        "resume_game": "Resume Game",
        "exit_to_menu": "Exit to Main Menu",
        "game_over": "GAME OVER",
        "final_score": "Final Score",
        "victory": "VICTORY",
        "press_enter": "Press Enter",
    },
    "ru": {
        "start_game": "Начать игру",
        "weapon_shop": "Магазин оружия",
        "your_points": "Ваши очки",
        "welcome_safe_house": "Добро пожаловать в вашу безопасную хижину",
        "buy_ammo": "Купить патроны",
        "exit_house": "Выйти из дома",
        "upgrade_damage": "Улучшить урон",
        "upgrade_magazine": "Улучшить обойму",
        "upgrade_reload": "Улучшить перезарядку",
        "rest_heal": "Отдохнуть и исцелиться",
        "upgrade_medkit_capacity": "Увеличить ёмкость аптечек",
        "full": "Полный",
        "coins": "монет",
        "plus_mag": "+1 обойма",
        "weapon_pistol": "Пистолет",
        "weapon_shotgun": "Дробовик",
        "weapon_rifle": "Автомат",
        "weapon_sniper": "Снайперская винтовка",
        "weapon_rpg": "РПГ",
        "selected": "Выбрано",
        "bought_and_selected": "Куплено и выбрано",
        "need": "Нужно",
        "points": "очков",
        "back": "Назад",
        "buy_or_select_weapon": "Купить или выбрать оружие",
        "owned": "В принадлежности",
        "settings": "Настройки",
        "quit": "Выйти",
        "last_score": "Последний счёт",
        "record": "Рекорд",
        "music_volume": "Музыка",
        "sfx_volume": "Громкость звуков",
        "fullscreen": "Полный экран",
        "language": "Язык",
        "settings_hint": "Влево/вправо или клик, чтобы изменить",
        "resume_game": "Продолжить",
        "exit_to_menu": "Выйти в меню",
        "game_over": "ИГРА ОКОНЧЕНА",
        "final_score": "Итоговый счёт",
        "victory": "ПОБЕДА",
        "press_enter": "Нажми Enter",
    },
    "uk": {
        "start_game": "Почати гру",
        "weapon_shop": "Магазин зброї",
        "your_points": "Ваші очки",
        "welcome_safe_house": "Ласкаво просимо до вашої безпечної домівки",
        "buy_ammo": "Придбати патрони",
        "exit_house": "Покинути домівку",
        "upgrade_damage": "Покращити урон",
        "upgrade_magazine": "Покращити обійму",
        "upgrade_reload": "Покращити перезарядку",
        "rest_heal": "Відпочити й вилікуватись",
        "upgrade_medkit_capacity": "Збільшити місткість аптечок",
        "full": "Повний",
        "coins": "монет",
        "plus_mag": "+1 обійма",
        "weapon_pistol": "Пістолет",
        "weapon_shotgun": "Дробовик",
        "weapon_rifle": "Автомат",
        "weapon_sniper": "Снайперська гвинтівка",
        "weapon_rpg": "РПГ",
        "selected": "Вибрано",
        "bought_and_selected": "Куплено й вибрано",
        "need": "Потрібно",
        "points": "очок",
        "back": "Назад",
        "buy_or_select_weapon": "Купити або вибрати зброю",
        "owned": "У володінні",
        "settings": "Налаштування",
        "quit": "Вийти",
        "last_score": "Останній рахунок",
        "record": "Рекорд",
        "music_volume": "Музика",
        "sfx_volume": "Гучність звуків",
        "fullscreen": "Повний екран",
        "language": "Мова",
        "settings_hint": "Вліво/вправо або клік, щоб змінити",
        "resume_game": "Продовжити",
        "exit_to_menu": "Вийти в меню",
        "game_over": "ГРУ ЗАВЕРШЕНО",
        "final_score": "Підсумковий рахунок",
        "victory": "ПЕРЕМОГА",
        "press_enter": "Натисни Enter",
    },
}

PLAYER_MAX_HP = 100
ZOMBIE_BASE_HP = 3
ZOMBIE_HP_PER_LEVEL = 1
ZOMBIE_TOUCH_DAMAGE = 15
BOSS_BULLET_DAMAGE = 20
BOSS_TOUCH_DAMAGE = 35
MINI_BOSS_BASE_HP = 14
MINI_BOSS_HP_PER_LEVEL = 4
MINI_BOSS_TOUCH_DAMAGE = 20
MINI_BOSS_BULLET_DAMAGE = 10
MINI_BOSS_SHOOT_DELAY = 900
MINI_BOSS_SIGHT_RANGE = 850
BOSS_SIGHT_RANGE = 1100
PLAYER_HIT_COOLDOWN = 700
ENEMY_SPEED_WAVE_MULTIPLIER = 1.04
ENEMY_SPEED_LEVEL_MULTIPLIER = 1.08
MEDKIT_HEAL_AMOUNT = 30
MAX_MEDKITS = 3
MAX_MEDKIT_CAPACITY = 6
MEDKIT_DROP_CHANCE = 0.4
BASE_SPARE_MAGAZINES = 2
MAX_SPARE_MAGAZINES = 4
MAX_WEAPON_UPGRADE_LEVEL = 3
WAVES_PER_MAP = 10
LEVEL_SKIP_CHEATS = ("SKIPLEVEL", "NEXTLEVEL")
CHEAT_BUFFER_LIMIT = max(len(code) for code in LEVEL_SKIP_CHEATS)
UPGRADE_COSTS = {
    "damage": [120, 240, 420],
    "magazine": [90, 180, 300],
    "reload": [100, 200, 340],
}
ZOMBIE_COIN_REWARD = 10
MINI_BOSS_COIN_REWARD = 45
BOSS_COIN_REWARD = 180
WAVE_CLEAR_BASE_COINS = 60
WAVE_CLEAR_COINS_PER_WAVE = 20
ENEMY_TYPES = {
    "walker": {
        "name": "Walker",
        "wave": 1,
        "weight": 70,
        "size": 50,
        "hp_mult": 1.0,
        "speed_mult": 1.0,
        "damage": ZOMBIE_TOUCH_DAMAGE,
        "reward": ZOMBIE_COIN_REWARD,
        "tint": (255, 255, 255),
        "bar": (80, 220, 80),
    },
    "runner": {
        "name": "Runner",
        "wave": 2,
        "weight": 28,
        "size": 44,
        "hp_mult": 0.7,
        "speed_mult": 1.45,
        "damage": 10,
        "reward": 12,
        "tint": (255, 210, 160),
        "bar": (255, 190, 70),
    },
    "brute": {
        "name": "Brute",
        "wave": 3,
        "weight": 18,
        "size": 64,
        "hp_mult": 2.4,
        "speed_mult": 0.65,
        "damage": 25,
        "reward": 25,
        "tint": (210, 170, 255),
        "bar": (180, 100, 255),
    },
    "toxic": {
        "name": "Toxic",
        "wave": 4,
        "weight": 16,
        "size": 50,
        "hp_mult": 1.25,
        "speed_mult": 0.9,
        "damage": 18,
        "reward": 20,
        "tint": (160, 255, 150),
        "bar": (130, 255, 100),
    },
    "spitter": {
        "name": "Spitter",
        "wave": 5,
        "weight": 14,
        "size": 50,
        "hp_mult": 1.15,
        "speed_mult": 0.75,
        "damage": 12,
        "reward": 22,
        "tint": (150, 220, 255),
        "bar": (90, 200, 255),
        "shoot_delay": 1500,
        "range": 650,
    },
}
AMBIENT_VOLUME = 0.35
HOUSE_RECT = pygame.Rect(1165, 1046, 229, 343)
BREAK_DURATION = 12000
HOUSE_ENTER_KEY = pygame.K_e

MAP_THEMES = [
    {
        "name": "Forest",
        "tint": (255, 255, 255),
        "overlay": (0, 0, 0, 0),
        "detail": "none",
        "enemy_tint": (255, 255, 255),
        "boss_bullet_color": (255, 60, 60),
        "mini_boss_bullet_color": (255, 210, 80),
        "enemy_bullet_color": (90, 210, 255),
        "difficulty": 1.0,
        "speed_bonus": 0.0,
        "spawn_rate": 2,
    },
    {
        "name": "Winter",
        "image": "map_winter.png",
        "house_rect": (1070, 1160, 360, 360),
        "tint": (190, 225, 255),
        "overlay": (210, 235, 255, 42),
        "detail": "snow",
        "enemy_tint": (210, 235, 255),
        "boss_bullet_color": (160, 230, 255),
        "mini_boss_bullet_color": (210, 245, 255),
        "enemy_bullet_color": (180, 240, 255),
        "difficulty": 1.0,
        "speed_bonus": 0.0,
        "spawn_rate": 2,
    },
    {
        "name": "Inferno",
        "image": "map_inferno.png",
        "house_rect": (1020, 1160, 360, 360),
        "tint": (255, 145, 85),
        "overlay": (95, 18, 5, 54),
        "detail": "lava",
        "enemy_tint": (255, 185, 115),
        "boss_bullet_color": (255, 80, 20),
        "mini_boss_bullet_color": (255, 155, 45),
        "enemy_bullet_color": (255, 110, 35),
        "difficulty": 1.25,
        "speed_bonus": 0.18,
        "spawn_rate": 2,
    },
    {
        "name": "Swamp",
        "image": "map_swamp.png",
        "house_rect": (850, 1160, 360, 360),
        "tint": (155, 210, 145),
        "overlay": (20, 60, 35, 48),
        "detail": "swamp",
        "enemy_tint": (185, 230, 125),
        "boss_bullet_color": (150, 255, 90),
        "mini_boss_bullet_color": (210, 235, 80),
        "enemy_bullet_color": (115, 255, 130),
        "difficulty": 1.38,
        "speed_bonus": 0.22,
        "spawn_rate": 2,
    },
    {
        "name": "Night City",
        "image": "map_city.png",
        "house_rect": (860, 1160, 360, 360),
        "tint": (135, 145, 215),
        "overlay": (12, 14, 42, 72),
        "detail": "neon",
        "enemy_tint": (205, 185, 255),
        "boss_bullet_color": (255, 70, 190),
        "mini_boss_bullet_color": (120, 255, 235),
        "enemy_bullet_color": (180, 95, 255),
        "difficulty": 1.55,
        "speed_bonus": 0.32,
        "spawn_rate": 1,
    },
]

FINAL_WAVE = WAVES_PER_MAP * len(MAP_THEMES)


def build_theme_waves(theme):
    waves = {}
    for wave_number, config in {
        1: {"enemies": 20, "spawn_rate": 2, "speed": 2.0},
        2: {"enemies": 28, "spawn_rate": 2, "speed": 2.1},
        3: {"enemies": 36, "spawn_rate": 2, "speed": 2.2},
        4: {"enemies": 44, "spawn_rate": 2, "speed": 2.35},
        5: {"enemies": 0, "spawn_rate": 2, "speed": 2.4, "boss": True},
        6: {"enemies": 46, "spawn_rate": 2, "speed": 2.5},
        7: {"enemies": 54, "spawn_rate": 2, "speed": 2.65},
        8: {"enemies": 62, "spawn_rate": 2, "speed": 2.8},
        9: {"enemies": 70, "spawn_rate": 2, "speed": 3.0},
        10: {"enemies": 0, "spawn_rate": 2, "speed": 3.1, "boss": True, "final": True},
    }.items():
        themed_config = config.copy()
        themed_config["enemies"] = int(config["enemies"] * theme["difficulty"])
        themed_config["speed"] = round(config["speed"] + theme["speed_bonus"], 2)
        themed_config["spawn_rate"] = theme["spawn_rate"]
        if wave_number == WAVES_PER_MAP:
            themed_config["final"] = False
        waves[wave_number] = themed_config
    return waves


for theme in MAP_THEMES:
    theme["waves"] = build_theme_waves(theme)

MAP_THEMES[-1]["waves"][WAVES_PER_MAP]["final"] = True


def map_index_for_wave(w):
    return max(0, min((w - 1) // WAVES_PER_MAP, len(MAP_THEMES) - 1))


def wave_in_map(w):
    return ((w - 1) % WAVES_PER_MAP) + 1


def map_theme_for_wave(w):
    return MAP_THEMES[map_index_for_wave(w)]


def wave_size(w):
    return wave_config(w)["enemies"]


def wave_config(w):
    theme = map_theme_for_wave(w)
    return theme["waves"][wave_in_map(w)]
