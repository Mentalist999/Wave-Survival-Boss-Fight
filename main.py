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

font = pygame.font.Font(None, 40)

# =========================
# WAVES
# =========================
def wave_size(w):
    return [20, 30, 40, 50][w-1] if w <= 4 else 0

# =========================
# HELPERS
# =========================
def draw_text(text, pos, color=(255, 255, 255), size=40):
    font_obj = pygame.font.Font(None, size)
    screen.blit(font_obj.render(text, True, color), pos)


def draw_text_center(text, y, color=(255, 255, 255), size=40):
    font_obj = pygame.font.Font(None, size)
    text_surface = font_obj.render(text, True, color)
    x = WIDTH // 2 - text_surface.get_width() // 2
    screen.blit(text_surface, (x, y))


def menu(best_score, last_score):
    options = ["Start Game", "Quit"]
    selected = 0
    pygame.mouse.set_visible(True)

    while True:
        screen.fill((18, 18, 18))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                if event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                if event.key == pygame.K_RETURN:
                    return selected == 0

        draw_text_center("Wave Survival Boss Fight", HEIGHT // 3 - 40, (255, 255, 255), 64)
        draw_text_center(f"Last Score: {last_score}", HEIGHT // 3 + 60, (230, 230, 230), 36)
        draw_text_center(f"Record: {best_score}", HEIGHT // 3 + 110, (230, 230, 230), 36)

        button_x = 80
        button_y = HEIGHT // 2 + 40

        for idx, option in enumerate(options):
            color = (255, 255, 255) if idx == selected else (180, 180, 180)
            draw_text(option, (button_x, button_y + idx * 80), color, 64)

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
        draw_text("Press ENTER to return to menu", (WIDTH//2 - 270, HEIGHT//2 + 60), (200, 200, 200), 32)

        pygame.display.flip()
        clock.tick(60)

# =========================
# GAME
# =========================
def game():

    player = pygame.Rect(WIDTH//2, HEIGHT//2, 60, 60)

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
    shoot_delay = 150

    boss_last_shot = 0
    boss_shoot_delay = 700

    def spawn_enemy():
        return pygame.Rect(random.randint(0, WIDTH), 0, 50, 50)

    def spawn_boss():
        return pygame.Rect(WIDTH//2 - 110, 100, 220, 220)

    pygame.mouse.set_visible(False)
    running = True

    while running:
        screen.fill((10, 10, 20))
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
            vx, vy = shoot_dir
            bullets.append({
                "rect": pygame.Rect(player.centerx - 5, player.centery - 5, 10, 10),
                "vx": vx * 12,
                "vy": vy * 12
            })
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

            for e in enemies:
                if b["rect"].colliderect(e):
                    enemies.remove(e)
                    score += 1
                    hit = True
                    break

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
                    boss_hp -= 1
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
        screen.blit(player_img, player)

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