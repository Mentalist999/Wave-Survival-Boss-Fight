import pygame
import os
import random
import math

os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()

# =========================
# SCREEN
# =========================
WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wave Survival Boss Fight")

clock = pygame.time.Clock()

# =========================
# ASSETS
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

def load(name, size=None):
    path = os.path.join(ASSETS_DIR, name)
    img = pygame.image.load(path).convert_alpha()
    if size:
        img = pygame.transform.scale(img, size)
    return img

player_img = load("player.png", (60, 60))
enemy_img = load("enemy.png", (50, 50))
bullet_img = load("bullet.png", (10, 10))
boss_img = load("boss.png", (220, 220))
map_img = load("map.png", (WIDTH, HEIGHT))
menu_img = load("menu.png", (WIDTH, HEIGHT))

WEAPONS = {
    "pistol": {
        "name": "Pistol",
        "cost": 0,
        "sprite": load("player_P.png", (60, 60)),
        "delay": 230,
        "speed": 13,
        "damage": 1,
        "pellets": 1,
        "spread": 0,
        "blast_radius": 0,
    },
    "shotgun": {
        "name": "Shotgun",
        "cost": 200,
        "sprite": load("Player_SH.png", (60, 60)),
        "delay": 520,
        "speed": 12,
        "damage": 1,
        "pellets": 5,
        "spread": 0.22,
        "blast_radius": 0,
    },
    "rifle": {
        "name": "Rifle",
        "cost": 400,
        "sprite": load("Player_AK.png", (60, 60)),
        "delay": 90,
        "speed": 16,
        "damage": 1,
        "pellets": 1,
        "spread": 0,
        "blast_radius": 0,
    },
    "sniper": {
        "name": "Sniper Rifle",
        "cost": 600,
        "sprite": load("Player_SP.png", (60, 60)),
        "delay": 650,
        "speed": 24,
        "damage": 5,
        "pellets": 1,
        "spread": 0,
        "blast_radius": 0,
    },
    "rpg": {
        "name": "RPG",
        "cost": 800,
        "sprite": load("Player_RPG.png", (60, 60)),
        "delay": 900,
        "speed": 9,
        "damage": 8,
        "pellets": 1,
        "spread": 0,
        "blast_radius": 90,
    },
}

weapon_order = ["pistol", "shotgun", "rifle", "sniper", "rpg"]
unlocked_weapons = {"pistol"}
current_weapon = "pistol"

font = pygame.font.Font(None, 40)

# Custom fonts (download from Google Fonts and place in assets/fonts/)
try:
    title_font = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "Orbitron-Bold.ttf"), 72)
    print("Loaded Orbitron font")
except Exception as e:
    print(f"Failed to load Orbitron: {e}")
    try:
        title_font = pygame.font.SysFont("orbitron", 72)  # try system font
        print("Using system Orbitron")
    except:
        title_font = pygame.font.Font(None, 72)  # fallback
        print("Using default font for title")

try:
    ui_font = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "Rajdhani-Bold.ttf"), 48)
    print("Loaded Rajdhani font")
except Exception as e:
    print(f"Failed to load Rajdhani: {e}")
    try:
        ui_font = pygame.font.SysFont("rajdhani", 48)  # try system font
        print("Using system Rajdhani")
    except:
        ui_font = pygame.font.Font(None, 48)  # fallback
        print("Using default font for UI")

try:
    stats_font = pygame.font.Font(os.path.join(ASSETS_DIR, "fonts", "ShareTechMono-Regular.ttf"), 32)
    print("Loaded Share Tech Mono font")
except Exception as e:
    print(f"Failed to load Share Tech Mono: {e}")
    try:
        stats_font = pygame.font.SysFont("share tech mono", 32)  # try system font
        print("Using system Share Tech Mono")
    except:
        try:
            stats_font = pygame.font.SysFont("monospace", 32)  # fallback to monospace
            print("Using system monospace")
        except:
            stats_font = pygame.font.Font(None, 32)  # final fallback
            print("Using default font for stats")

# =========================
# WAVES
# =========================
def wave_size(w):
    return [20, 30, 40, 50][w-1] if w <= 4 else 0

# =========================
# HELPERS
# =========================
def draw_text(text, pos, color=(255, 255, 255), size=40, font=None, glow_color=None, glow_radius=0):
    if font is None:
        font = pygame.font.Font(None, size)
    if glow_color and glow_radius > 0:
        glow_surface = font.render(text, True, glow_color)
        for dx in range(-glow_radius, glow_radius + 1):
            for dy in range(-glow_radius, glow_radius + 1):
                if dx == 0 and dy == 0:
                    continue
                screen.blit(glow_surface, (pos[0] + dx, pos[1] + dy))
    screen.blit(font.render(text, True, color), pos)


def draw_text_center(text, y, color=(255, 255, 255), size=40, font=None, glow_color=None, glow_radius=0):
    if font is None:
        font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    x = WIDTH // 2 - text_surface.get_width() // 2
    if glow_color and glow_radius > 0:
        glow_surface = font.render(text, True, glow_color)
        for dx in range(-glow_radius, glow_radius + 1):
            for dy in range(-glow_radius, glow_radius + 1):
                if dx == 0 and dy == 0:
                    continue
                screen.blit(glow_surface, (x + dx, y + dy))
    screen.blit(text_surface, (x, y))


def shop_menu(score):
    global current_weapon

    options = weapon_order + ["back"]
    selected = 0
    message = "Buy or select a weapon"
    pygame.mouse.set_visible(True)

    while True:
        screen.blit(menu_img, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                if event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                if event.key == pygame.K_RETURN:
                    choice = options[selected]
                    if choice == "back":
                        return

                    weapon = WEAPONS[choice]
                    if choice in unlocked_weapons:
                        current_weapon = choice
                        message = f"Selected: {weapon['name']}"
                    elif score >= weapon["cost"]:
                        unlocked_weapons.add(choice)
                        current_weapon = choice
                        message = f"Bought and selected: {weapon['name']}"
                    else:
                        message = f"Need {weapon['cost']} points to buy {weapon['name']}"

        draw_text_center("WEAPON SHOP", HEIGHT // 4, (255, 230, 200), font=title_font, glow_color=(220, 140, 60), glow_radius=2)
        draw_text_center(f"Your Points: {score}", HEIGHT // 4 + 80, (240, 210, 180), font=stats_font)
        draw_text_center(message, HEIGHT // 4 + 120, (255, 235, 170), font=stats_font)

        button_x = 100
        button_y = HEIGHT // 2 - 80

        for idx, option in enumerate(options):
            if option == "back":
                label = "Back to Menu"
            else:
                weapon = WEAPONS[option]
                state = "Selected" if option == current_weapon else "Owned" if option in unlocked_weapons else f"{weapon['cost']} points"
                label = f"{weapon['name']} - {state}"

            if idx == selected:
                draw_text(
                    label,
                    (button_x, button_y + idx * 50),
                    (255, 245, 220),
                    font=ui_font,
                    glow_color=(210, 120, 40),
                    glow_radius=1
                )
            else:
                draw_text(label, (button_x, button_y + idx * 50), (220, 195, 170), font=ui_font)

        pygame.display.flip()
        clock.tick(60)


def menu(best_score, last_score):
    options = ["Start Game", "Shop", "Quit"]
    selected = 0
    pygame.mouse.set_visible(True)

    while True:
        screen.blit(menu_img, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                if event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                if event.key == pygame.K_RETURN:
                    if selected == 0:  # Start Game
                        return True
                    elif selected == 1:  # Shop
                        shop_menu(best_score)
                    elif selected == 2:  # Quit
                        return False

        draw_text_center(
            "Wave Survival Boss Fight",
            HEIGHT // 3 - 40,
            (255, 230, 200),
            font=title_font,
            glow_color=(220, 140, 60),
            glow_radius=2
        )
        draw_text_center(f"Last Score: {last_score}", HEIGHT // 3 + 60, (240, 210, 180), font=stats_font)
        draw_text_center(f"Record: {best_score}", HEIGHT // 3 + 110, (240, 210, 180), font=stats_font)

        button_x = 80
        button_y = HEIGHT // 2 + 40

        for idx, option in enumerate(options):
            if idx == selected:
                draw_text(
                    option,
                    (button_x, button_y + idx * 80),
                    (255, 245, 220),
                    font=ui_font,
                    glow_color=(210, 120, 40),
                    glow_radius=1
                )
            else:
                draw_text(option, (button_x, button_y + idx * 80), (220, 195, 170), font=ui_font)

        pygame.display.flip()
        clock.tick(60)


def game_over_screen(score):
    pygame.mouse.set_visible(True)
    while True:
        screen.fill((10, 10, 20))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return

        draw_text("GAME OVER", (WIDTH//2 - 180, HEIGHT//3 - 40), (255, 80, 80), 64)
        draw_text(f"Final Score: {score}", (WIDTH//2 - 150, HEIGHT//3 + 40), (255, 255, 255), 40)

        pygame.display.flip()
        clock.tick(60)

# =========================
# GAME
# =========================
def game():

    player = pygame.Rect(WIDTH//2, HEIGHT//2, 60, 60)
    weapon = WEAPONS[current_weapon]
    player_sprite = weapon["sprite"]

    bullets = []
    enemies = []
    boss_bullets = []

    wave = 1
    level = 1

    enemy_count = wave_size(wave)
    spawned = 0

    enemy_speed = 2
    spawn_rate = 2

    boss = None
    boss_hp = 0
    boss_max_hp = 0

    score = 0

    last_shot = 0
    shoot_delay = weapon["delay"]

    boss_last_shot = 0
    boss_shoot_delay = 700

    def spawn_enemy():
        return pygame.Rect(random.randint(0, WIDTH), 0, 50, 50)

    def spawn_boss():
        return pygame.Rect(WIDTH//2 - 110, 100, 220, 220)

    def make_player_bullets(direction):
        vx, vy = direction
        created = []
        pellet_count = weapon["pellets"]
        middle = pellet_count // 2

        for i in range(pellet_count):
            offset = i - middle
            shot_vx = vx
            shot_vy = vy

            if weapon["spread"] and pellet_count > 1:
                if vx == 0:
                    shot_vx += offset * weapon["spread"]
                else:
                    shot_vy += offset * weapon["spread"]

                length = math.hypot(shot_vx, shot_vy)
                shot_vx /= length
                shot_vy /= length

            created.append({
                "rect": pygame.Rect(player.centerx - 5, player.centery - 5, 10, 10),
                "vx": shot_vx * weapon["speed"],
                "vy": shot_vy * weapon["speed"],
                "damage": weapon["damage"],
                "blast_radius": weapon["blast_radius"],
            })

        return created

    def bullet_center(bullet):
        return bullet["rect"].centerx, bullet["rect"].centery

    def in_blast_radius(rect, center, radius):
        if radius <= 0:
            return False
        return math.hypot(rect.centerx - center[0], rect.centery - center[1]) <= radius

    pygame.mouse.set_visible(False)
    running = True

    while running:
        screen.blit(map_img, (0, 0))
        now = pygame.time.get_ticks()

        # =========================
        # EVENTS
        # =========================
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return score

        # =========================
        # MOVE PLAYER
        # =========================
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]: player.y -= 6
        if keys[pygame.K_s]: player.y += 6
        if keys[pygame.K_a]: player.x -= 6
        if keys[pygame.K_d]: player.x += 6

        # =========================
        # SHOOT
        # =========================
        shoot_dir = None
        if keys[pygame.K_UP]:
            shoot_dir = (0, -1)
        elif keys[pygame.K_DOWN]:
            shoot_dir = (0, 1)
        elif keys[pygame.K_LEFT]:
            shoot_dir = (-1, 0)
        elif keys[pygame.K_RIGHT]:
            shoot_dir = (1, 0)

        if shoot_dir and now - last_shot > shoot_delay:
            bullets.extend(make_player_bullets(shoot_dir))
            last_shot = now

        # =========================
        # MOVE BULLETS
        # =========================
        for b in bullets:
            b["rect"].x += b["vx"]
            b["rect"].y += b["vy"]

        bullets = [b for b in bullets if 0 < b["rect"].x < WIDTH and 0 < b["rect"].y < HEIGHT]

        # =========================
        # SPAWN ENEMIES
        # =========================
        if boss is None:
            if spawned < enemy_count:
                if random.randint(1, spawn_rate) == 1:
                    enemies.append(spawn_enemy())
                    spawned += 1

        # =========================
        # MOVE ENEMIES
        # =========================
        for e in enemies:
            dx = player.x - e.x
            dy = player.y - e.y
            dist = math.hypot(dx, dy)

            if dist != 0:
                e.x += int(dx / dist * enemy_speed)
                e.y += int(dy / dist * enemy_speed)

        # =========================
        # BULLET HIT ENEMIES (SAFE REMOVE)
        # =========================
        new_bullets = []

        for b in bullets:
            hit = False
            blast_center = bullet_center(b)
            hit_enemies = [
                e for e in enemies
                if b["rect"].colliderect(e) or in_blast_radius(e, blast_center, b["blast_radius"])
            ]

            for e in hit_enemies:
                enemies.remove(e)
                score += 1
                hit = True

            if not hit:
                new_bullets.append(b)

        bullets = new_bullets

        # =========================
        # BOSS SHOOT
        # =========================
        if boss:
            if now - boss_last_shot > boss_shoot_delay:

                dx = player.centerx - boss.centerx
                dy = player.centery - boss.centery
                dist = math.hypot(dx, dy)

                if dist != 0:
                    vx = dx / dist
                    vy = dy / dist

                    boss_bullets.append({
                        "rect": pygame.Rect(boss.centerx, boss.centery, 10, 10),
                        "vx": vx * 7,
                        "vy": vy * 7
                    })

                boss_last_shot = now

        # =========================
        # MOVE BOSS BULLETS
        # =========================
        for b in boss_bullets:
            b["rect"].x += b["vx"]
            b["rect"].y += b["vy"]

        boss_bullets = [b for b in boss_bullets if 0 < b["rect"].x < WIDTH and 0 < b["rect"].y < HEIGHT]

        # =========================
        # PLAYER HIT
        # =========================
        for b in boss_bullets:
            if player.colliderect(b["rect"]):
                game_over_screen(score)
                return score

        for e in enemies:
            if player.colliderect(e):
                game_over_screen(score)
                return score

        if boss and player.colliderect(boss):
            game_over_screen(score)
            return score

        # =========================
        # BOSS DAMAGE (FIXED)
        # =========================
        if boss:
            new_bullets = []

            for b in bullets:
                if b["rect"].colliderect(boss):
                    boss_hp -= b["damage"]
                elif in_blast_radius(boss, bullet_center(b), b["blast_radius"]):
                    boss_hp -= b["damage"]
                else:
                    new_bullets.append(b)

            bullets = new_bullets

        # =========================
        # WAVE SYSTEM
        # =========================
        if len(enemies) == 0 and boss is None and spawned >= enemy_count:

            wave += 1
            spawned = 0
            enemy_count = wave_size(wave)

            if wave % 5 == 0:
                boss = spawn_boss()
                boss_max_hp = 20 * level
                boss_hp = boss_max_hp
            else:
                enemy_speed += 0.5

        # =========================
        # BOSS DEATH
        # =========================
        if boss and boss_hp <= 0:
            boss = None
            level += 1
            wave = 0
            enemy_speed += 1
            spawn_rate = 2

        # =========================
        # DRAW
        # =========================
        screen.blit(player_sprite, player)

        for e in enemies:
            screen.blit(enemy_img, e)

        if boss:
            screen.blit(boss_img, boss)

            hp_ratio = boss_hp / boss_max_hp
            pygame.draw.rect(screen, (255, 255, 255), (boss.x, boss.y - 20, 220, 10))
            pygame.draw.rect(screen, (255, 0, 0), (boss.x, boss.y - 20, 220 * hp_ratio, 10))

        for b in bullets:
            screen.blit(bullet_img, b["rect"])

        for b in boss_bullets:
            pygame.draw.rect(screen, (255, 60, 60), b["rect"])

        # =========================
        # UI
        # =========================
        screen.blit(font.render(f"Score: {score}", True, (255,255,255)), (20, 20))
        screen.blit(font.render(f"Wave: {wave}", True, (0,255,200)), (20, 60))
        screen.blit(font.render(f"Level: {level}", True, (255,255,0)), (20, 100))
        screen.blit(font.render(f"Weapon: {weapon['name']}", True, (255,220,120)), (20, 140))

        pygame.display.flip()
        clock.tick(60)

# =========================
# START
# =========================
if __name__ == "__main__":
    best_score = 0
    last_score = 0

    while True:
        if not menu(best_score, last_score):
            break

        score = game()
        if score is None:
            score = 0

        last_score = score
        if score > best_score:
            best_score = score

    pygame.quit()
