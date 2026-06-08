import pygame
import math
import random
import constants
import assets
import utils
import menus


def draw_player_character(rect, camera_x, camera_y, moving, direction, weapon_key, fallback_sprite, hurt=False):
    screen_rect = rect.move(-camera_x, -camera_y)
    if not assets.PLAYER_PARTS_READY:
        if hurt:
            fallback_sprite = utils.tint_surface(fallback_sprite, (255, 150, 150))
        constants.screen.blit(fallback_sprite, screen_rect)
        return

    x = screen_rect.x
    y = screen_rect.y
    walk = math.sin(pygame.time.get_ticks() * 0.014) if moving else 0
    head_bob = int(abs(walk) * 2)
    arm_swing = int(walk * 4)
    leg_swing = int(walk * 4)
    flip = direction == (-1, 0)

    def part(name):
        image = assets.PLAYER_PARTS[name]
        if hurt:
            image = utils.tint_surface(image, (255, 150, 150))
        return pygame.transform.flip(image, True, False) if flip else image

    leg_left_pos = (x + 18, y + 43 + leg_swing)
    leg_right_pos = (x + 30, y + 43 - leg_swing)
    body_pos = (x + 15, y + 18 + head_bob)
    head_pos = (x + 13, y - 2 + head_bob)
    arm_back_pos = (x + 13, y + 22 - arm_swing)
    arm_front_pos = (x + 38, y + 22 + arm_swing)

    if flip:
        arm_back_pos, arm_front_pos = arm_front_pos, arm_back_pos

    constants.screen.blit(part("leg_left"), leg_left_pos)
    constants.screen.blit(part("leg_right"), leg_right_pos)
    constants.screen.blit(part("arm_left"), arm_back_pos)
    constants.screen.blit(part("arm_right"), arm_front_pos)
    constants.screen.blit(part("body"), body_pos)
    constants.screen.blit(part("head"), head_pos)

    weapon_img = assets.WEAPON_IMAGES.get(weapon_key)
    if weapon_img:
        weapon = pygame.transform.flip(weapon_img, True, False) if flip else weapon_img
        if direction == (0, -1):
            weapon_pos = (x + 28, y + 12 + head_bob)
            weapon = pygame.transform.rotate(weapon, 90)
        elif direction == (0, 1):
            weapon_pos = (x + 26, y + 34 + head_bob)
            weapon = pygame.transform.rotate(weapon, -90)
        elif flip:
            weapon_pos = (x + 2, y + 27 + head_bob)
        else:
            weapon_pos = (x + 33, y + 27 + head_bob)
        if hurt:
            weapon = utils.tint_surface(weapon, (255, 150, 150))
        constants.screen.blit(weapon, weapon_pos)


def game():
    utils.start_ambient_sound()

    player = pygame.Rect(0, 0, 60, 60)
    player.center = (assets.WORLD_WIDTH // 2, assets.WORLD_HEIGHT // 2)
    weapon = assets.WEAPONS[constants.current_weapon]
    player_sprite = weapon["sprite"]
    player_hp = constants.PLAYER_MAX_HP
    medkits = 0
    last_player_hit = -constants.PLAYER_HIT_COOLDOWN
    player_hurt_timer = 0
    paused = False
    selected = 0
    start_time = pygame.time.get_ticks()
    waiting_for_next_wave = False
    wave_break_end = 0
    pending_boss_level_up = False
    house_entered_this_break = False
    house_message = ""
    in_house = False

    bullets = []
    enemies = []
    mini_bosses = []
    boss_bullets = []
    mini_boss_bullets = []
    enemy_bullets = []
    ammo_pickups = []
    medkit_pickups = []
    particles = []
    floating_texts = []

    wave = 1
    level = 1
    enemy_count = constants.wave_size(wave)
    spawned = 0
    mini_bosses_spawned = 0
    enemy_speed = constants.wave_config(wave)["speed"]
    spawn_rate = constants.wave_config(wave)["spawn_rate"]
    boss = None
    boss_hp = 0
    boss_max_hp = 0
    score = 0
    last_shot = 0
    shoot_delay = weapon["delay"]
    look_dir = (1, 0)
    is_moving = False
    reloading = False
    reload_end = 0
    status_message = f"{constants.map_theme_for_wave(wave)['name']} - Wave {constants.wave_in_map(wave)}/{constants.WAVES_PER_MAP}"
    status_message_until = pygame.time.get_ticks() + 2500
    boss_last_shot = 0
    boss_shoot_delay = 700
    cheat_buffer = ""
    cheat_chat_open = False
    cheat_chat_text = ""

    def magazine_size(weapon_key=None):
        if weapon_key is None:
            weapon_key = constants.current_weapon
        return utils.weapon_magazine_size(weapon_key)

    current_mag_ammo = magazine_size()
    spare_mags = constants.BASE_SPARE_MAGAZINES
    coins = 0

    def prepare_wave_ammo():
        nonlocal current_mag_ammo, spare_mags, reloading
        reloading = False
        current_mag_ammo = magazine_size()
        spare_mags = min(constants.MAX_SPARE_MAGAZINES, max(spare_mags, constants.BASE_SPARE_MAGAZINES))

    def reload_weapon():
        nonlocal reloading, reload_end
        if reloading or current_mag_ammo >= magazine_size() or spare_mags <= 0:
            return
        reloading = True
        reload_end = now + utils.weapon_reload_time(constants.current_weapon)

    def add_floating_text(text, pos, color):
        floating_texts.append({
            "text": text,
            "x": pos[0],
            "y": pos[1],
            "color": color,
            "until": now + 900,
        })

    def add_particles(pos, color, count=8):
        for _ in range(count):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(1.2, 4.0)
            particles.append({
                "x": pos[0],
                "y": pos[1],
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "radius": random.randint(2, 5),
                "color": color,
                "until": now + random.randint(350, 700),
            })

    def drop_enemy_loot(enemy):
        enemy_name = enemy["type"]["name"]
        center = enemy["rect"].center
        if enemy_name == "Spitter" and random.random() < 0.35:
            ammo_pickups.append({"rect": pygame.Rect(center[0] - 12, center[1] - 12, 24, 24)})
            add_floating_text("Ammo", center, (180, 220, 255))
        elif enemy_name in ("Brute", "Toxic") and random.random() < 0.16:
            medkit_pickups.append({"rect": pygame.Rect(center[0] - 12, center[1] - 12, 24, 24)})
            add_floating_text("Medkit", center, (120, 255, 140))
        elif enemy_name == "Walker" and random.random() < 0.04:
            medkit_pickups.append({"rect": pygame.Rect(center[0] - 12, center[1] - 12, 24, 24)})

    def set_status_message(text, duration=2200):
        nonlocal status_message, status_message_until
        status_message = text
        status_message_until = now + duration

    def wave_clear_reward():
        return constants.WAVE_CLEAR_BASE_COINS + wave * constants.WAVE_CLEAR_COINS_PER_WAVE

    def zombie_max_hp():
        return constants.ZOMBIE_BASE_HP + (level - 1) * constants.ZOMBIE_HP_PER_LEVEL

    def choose_enemy_type():
        current_map_wave = constants.wave_in_map(wave)
        available = [
            enemy_type for enemy_type in constants.ENEMY_TYPES.values()
            if current_map_wave >= enemy_type["wave"]
        ]
        total_weight = sum(enemy_type["weight"] for enemy_type in available)
        roll = random.uniform(0, total_weight)
        current = 0
        for enemy_type in available:
            current += enemy_type["weight"]
            if roll <= current:
                return enemy_type
        return available[0]

    def random_world_edge_position(width, height):
        world_width, world_height = current_world_size()
        edge = random.choice(["top", "bottom", "left", "right"])
        if edge == "top":
            return random.randint(0, world_width - width), 0
        if edge == "bottom":
            return random.randint(0, world_width - width), world_height - height
        if edge == "left":
            return 0, random.randint(0, world_height - height)
        return world_width - width, random.randint(0, world_height - height)

    def spawn_enemy():
        enemy_type = choose_enemy_type()
        size = enemy_type["size"]
        max_hp = max(1, int(zombie_max_hp() * enemy_type["hp_mult"]))
        x, y = random_world_edge_position(size, size)
        sprite = utils.tint_surface(assets.enemy_img, constants.map_theme_for_wave(wave)["enemy_tint"])
        if enemy_type["tint"] != (255, 255, 255):
            sprite = utils.tint_surface(sprite, enemy_type["tint"])
        if size != 50:
            sprite = pygame.transform.scale(sprite, (size, size))
        return {
            "rect": pygame.Rect(x, y, size, size),
            "hp": max_hp,
            "max_hp": max_hp,
            "type": enemy_type,
            "sprite": sprite,
            "last_shot": 0,
        }

    def mini_boss_max_hp():
        return constants.MINI_BOSS_BASE_HP + (level - 1) * constants.MINI_BOSS_HP_PER_LEVEL

    def mini_boss_count_for_wave():
        current_map_wave = constants.wave_in_map(wave)
        if current_map_wave < 6:
            return 0
        return min(current_map_wave - 4, 5)

    def spawn_mini_boss():
        max_hp = mini_boss_max_hp()
        x, y = random_world_edge_position(70, 70)
        return {
            "rect": pygame.Rect(x, y, 70, 70),
            "hp": max_hp,
            "max_hp": max_hp,
            "last_shot": 0,
        }

    def spawn_boss():
        world_width, world_height = current_world_size()
        return pygame.Rect(world_width // 2 - 110, world_height // 2 - 300, 220, 220)

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
                "damage": utils.weapon_damage(constants.current_weapon),
                "blast_radius": weapon["blast_radius"],
            })
        return created

    def bullet_center(bullet):
        return bullet["rect"].centerx, bullet["rect"].centery

    def in_blast_radius(rect, center, radius):
        if radius <= 0:
            return False
        return math.hypot(rect.centerx - center[0], rect.centery - center[1]) <= radius

    def current_world_size():
        return constants.map_theme_for_wave(wave)["surface"].get_size()

    def move_player_to_current_map_center():
        world_width, world_height = current_world_size()
        player.center = (world_width // 2, world_height // 2)
        player.clamp_ip(pygame.Rect(0, 0, world_width, world_height))

    def get_camera():
        world_width, world_height = current_world_size()
        camera_x = max(0, min(player.centerx - constants.WIDTH // 2, world_width - constants.WIDTH))
        camera_y = max(0, min(player.centery - constants.HEIGHT // 2, world_height - constants.HEIGHT))
        return camera_x, camera_y

    def camera_rect(rect, camera_x, camera_y):
        return rect.move(-camera_x, -camera_y)

    def current_house_rect():
        return pygame.Rect(constants.map_theme_for_wave(wave).get("house_rect", constants.HOUSE_RECT))

    def hurt_player(damage):
        nonlocal player_hp, last_player_hit, player_hurt_timer
        if now - last_player_hit < constants.PLAYER_HIT_COOLDOWN:
            return False
        player_hp -= damage
        player_hurt_timer = 500
        last_player_hit = now
        return player_hp <= 0

    def use_medkit():
        nonlocal player_hp, medkits
        if medkits <= 0 or player_hp >= constants.PLAYER_MAX_HP:
            return
        medkits -= 1
        player_hp = min(constants.PLAYER_MAX_HP, player_hp + constants.MEDKIT_HEAL_AMOUNT)

    def skip_level_cheat():
        nonlocal wave, level, enemy_count, spawned, mini_bosses_spawned
        nonlocal enemy_speed, spawn_rate, boss, boss_hp, boss_max_hp
        nonlocal waiting_for_next_wave, wave_break_end, pending_boss_level_up
        nonlocal house_entered_this_break, house_message, in_house, reloading, reload_end
        nonlocal boss_last_shot

        current_map_index = constants.map_index_for_wave(wave)
        if current_map_index >= len(constants.MAP_THEMES) - 1:
            set_status_message("Cheat active: no more levels to skip", 2500)
            return
        next_map_index = current_map_index + 1
        wave = next_map_index * constants.WAVES_PER_MAP + 1
        level = max(level, next_map_index + 1)
        move_player_to_current_map_center()
        enemy_count = constants.wave_size(wave)
        spawned = 0
        mini_bosses_spawned = 0
        enemy_speed = constants.wave_config(wave)["speed"]
        spawn_rate = constants.wave_config(wave)["spawn_rate"]
        enemies.clear()
        mini_bosses.clear()
        bullets.clear()
        boss_bullets.clear()
        mini_boss_bullets.clear()
        enemy_bullets.clear()
        ammo_pickups.clear()
        medkit_pickups.clear()
        boss = None
        boss_hp = 0
        boss_max_hp = 0
        boss_last_shot = now
        waiting_for_next_wave = False
        wave_break_end = 0
        pending_boss_level_up = False
        house_entered_this_break = False
        house_message = ""
        in_house = False
        reloading = False
        reload_end = 0
        prepare_wave_ammo()
        next_theme = constants.map_theme_for_wave(wave)
        set_status_message(f"Cheat activated: {next_theme['name']} unlocked", 3200)

    def check_cheat_key(event):
        nonlocal cheat_buffer
        if paused or in_house:
            return
        key_name = pygame.key.name(event.key).upper()
        if len(key_name) == 1 and "A" <= key_name <= "Z":
            key_char = key_name
        elif event.unicode and event.unicode.isascii() and event.unicode.isalpha():
            key_char = event.unicode.upper()
        else:
            return
        cheat_buffer = (cheat_buffer + key_char)[-constants.CHEAT_BUFFER_LIMIT:]
        for code in constants.LEVEL_SKIP_CHEATS:
            if cheat_buffer.endswith(code):
                cheat_buffer = ""
                skip_level_cheat()
                return

    def submit_cheat_chat():
        nonlocal cheat_chat_text
        code = cheat_chat_text.strip().upper()
        cheat_chat_text = ""
        if not code:
            return
        if code in constants.LEVEL_SKIP_CHEATS:
            skip_level_cheat()
        else:
            set_status_message(f"Unknown cheat: {code}", 1800)

    def draw_cheat_chat():
        box_width = min(760, constants.WIDTH - 80)
        box_height = 54
        box_x = constants.WIDTH // 2 - box_width // 2
        box_y = constants.HEIGHT - 190
        box = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        box.fill((10, 12, 18, 225))
        constants.screen.blit(box, (box_x, box_y))
        pygame.draw.rect(constants.screen, (95, 180, 255), (box_x, box_y, box_width, box_height), 2, border_radius=8)
        text = cheat_chat_text if cheat_chat_text else "type cheat code..."
        color = (245, 250, 255) if cheat_chat_text else (145, 155, 170)
        constants.screen.blit(utils.font.render(f"> {text}", True, color), (box_x + 18, box_y + 17))

    def try_drop_medkit():
        nonlocal medkits
        if medkits >= constants.MAX_MEDKITS:
            return
        if random.random() < constants.MEDKIT_DROP_CHANCE:
            medkits += 1

    pygame.mouse.set_visible(False)
    running = True

    while running:
        now = pygame.time.get_ticks()
        dt = constants.clock.tick(60)
        if player_hurt_timer > 0:
            player_hurt_timer -= dt
        if reloading and now >= reload_end:
            reloading = False
            spare_mags -= 1
            current_mag_ammo = magazine_size()
            set_status_message("Reloaded", 900)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                utils.stop_ambient_sound()
                return score
            if event.type == pygame.KEYDOWN:
                if cheat_chat_open:
                    if event.key == pygame.K_RETURN:
                        submit_cheat_chat()
                        cheat_chat_open = False
                    elif event.key == pygame.K_ESCAPE:
                        cheat_chat_text = ""
                        cheat_chat_open = False
                    elif event.key == pygame.K_BACKSPACE:
                        cheat_chat_text = cheat_chat_text[:-1]
                    elif len(cheat_chat_text) < 24:
                        key_name = pygame.key.name(event.key).upper()
                        if len(key_name) == 1 and "A" <= key_name <= "Z":
                            cheat_chat_text += key_name
                        elif event.unicode and event.unicode.isprintable():
                            cheat_chat_text += event.unicode
                    continue
                if event.key == pygame.K_t and not paused:
                    cheat_chat_open = True
                    cheat_chat_text = ""
                    continue
                check_cheat_key(event)
                if event.key == pygame.K_1:
                    use_medkit()
                elif event.key == pygame.K_r:
                    reload_weapon()
                elif event.key == pygame.K_ESCAPE:
                    paused = not paused
                elif event.key == constants.HOUSE_ENTER_KEY and waiting_for_next_wave and player.colliderect(current_house_rect()):
                    if not house_entered_this_break:
                        in_house = True
                        pygame.mouse.set_visible(False)
                if paused:
                    if event.key == pygame.K_UP:
                        if selected == -1:
                            selected = 0
                        else:
                            selected = (selected - 1) % 3
                    if event.key == pygame.K_DOWN:
                        if selected == -1:
                            selected = 0
                        else:
                            selected = (selected + 1) % 3
                    if event.key == pygame.K_RETURN:
                        if selected >= 0:
                            if selected == 0:
                                paused = False
                            elif selected == 1:
                                menus.settings_menu()
                            else:
                                running = False
            if paused and event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if menus.resume_rect and menus.resume_rect.collidepoint(mouse_pos):
                    paused = False
                elif menus.settings_rect and menus.settings_rect.collidepoint(mouse_pos):
                    menus.settings_menu()
                elif menus.exit_rect and menus.exit_rect.collidepoint(mouse_pos):
                    running = False

        if in_house and waiting_for_next_wave:
            previous_weapon = constants.current_weapon
            coins, current_mag_ammo, spare_mags, player_hp = menus.house_interior(coins, current_mag_ammo, spare_mags, player_hp)
            weapon = assets.WEAPONS[constants.current_weapon]
            player_sprite = weapon["sprite"]
            shoot_delay = weapon["delay"]
            if constants.current_weapon != previous_weapon:
                current_mag_ammo = magazine_size()
                spare_mags = constants.BASE_SPARE_MAGAZINES
            reloading = False
            in_house = False
            house_entered_this_break = True
            house_message = "House supplies updated."
            pygame.mouse.set_visible(False)

        if not paused and not cheat_chat_open:
            keys = pygame.key.get_pressed()
            move_dir = None
            if keys[pygame.K_w]:
                player.y -= 6
                move_dir = (0, -1)
            if keys[pygame.K_s]:
                player.y += 6
                move_dir = (0, 1)
            if keys[pygame.K_a]:
                player.x -= 6
                move_dir = (-1, 0)
            if keys[pygame.K_d]:
                player.x += 6
                move_dir = (1, 0)
            is_moving = keys[pygame.K_w] or keys[pygame.K_s] or keys[pygame.K_a] or keys[pygame.K_d]
            world_width, world_height = current_world_size()
            player.clamp_ip(pygame.Rect(0, 0, world_width, world_height))
            shoot_dir = None
            if keys[pygame.K_UP]:
                shoot_dir = (0, -1)
            elif keys[pygame.K_DOWN]:
                shoot_dir = (0, 1)
            elif keys[pygame.K_LEFT]:
                shoot_dir = (-1, 0)
            elif keys[pygame.K_RIGHT]:
                shoot_dir = (1, 0)
            if shoot_dir:
                look_dir = shoot_dir
            elif move_dir:
                look_dir = move_dir
            if shoot_dir and current_mag_ammo > 0 and not reloading and now - last_shot > shoot_delay:
                bullets.extend(make_player_bullets(shoot_dir))
                current_mag_ammo -= 1
                last_shot = now
            elif shoot_dir and current_mag_ammo <= 0 and spare_mags > 0 and not reloading:
                reload_weapon()
            for b in bullets:
                b["rect"].x += b["vx"]
                b["rect"].y += b["vy"]
            bullets = [
                b for b in bullets
                if 0 < b["rect"].x < world_width
                and 0 < b["rect"].y < world_height
            ]
            if boss is None and not waiting_for_next_wave:
                mini_boss_target = mini_boss_count_for_wave()
                while mini_bosses_spawned < mini_boss_target:
                    mini_bosses.append(spawn_mini_boss())
                    mini_bosses_spawned += 1
                if spawned < enemy_count:
                    if random.randint(1, spawn_rate) == 1:
                        enemies.append(spawn_enemy())
                        spawned += 1
            for e in enemies:
                zombie = e["rect"]
                dx = player.x - zombie.x
                dy = player.y - zombie.y
                dist = math.hypot(dx, dy)
                if dist != 0:
                    zombie.x += int(dx / dist * enemy_speed * e["type"]["speed_mult"])
                    zombie.y += int(dy / dist * enemy_speed * e["type"]["speed_mult"])
                if "shoot_delay" in e["type"] and now - e["last_shot"] > e["type"]["shoot_delay"] and 0 < dist <= e["type"]["range"]:
                    vx = dx / dist
                    vy = dy / dist
                    enemy_bullets.append({
                        "rect": pygame.Rect(zombie.centerx - 5, zombie.centery - 5, 10, 10),
                        "vx": vx * 8,
                        "vy": vy * 8,
                        "damage": 8,
                    })
                    e["last_shot"] = now
            for mb in mini_bosses:
                mini_boss = mb["rect"]
                dx = player.x - mini_boss.x
                dy = player.y - mini_boss.y
                dist = math.hypot(dx, dy)
                if dist != 0:
                    mini_boss.x += int(dx / dist * enemy_speed * 0.65)
                    mini_boss.y += int(dy / dist * enemy_speed * 0.65)
                if now - mb["last_shot"] > constants.MINI_BOSS_SHOOT_DELAY and 0 < dist <= constants.MINI_BOSS_SIGHT_RANGE:
                    vx = dx / dist
                    vy = dy / dist
                    mini_boss_bullets.append({
                        "rect": pygame.Rect(mini_boss.centerx - 5, mini_boss.centery - 5, 10, 10),
                        "vx": vx * 10,
                        "vy": vy * 10,
                    })
                    mb["last_shot"] = now
            new_bullets = []
            for b in bullets:
                hit = False
                blast_center = bullet_center(b)
                hit_enemies = [
                    e for e in enemies
                    if b["rect"].colliderect(e["rect"]) or in_blast_radius(e["rect"], blast_center, b["blast_radius"])
                ]
                hit_mini_bosses = [
                    mb for mb in mini_bosses
                    if b["rect"].colliderect(mb["rect"]) or in_blast_radius(mb["rect"], blast_center, b["blast_radius"])
                ]
                for e in hit_enemies:
                    e["hp"] -= b["damage"]
                    add_floating_text(f"-{b['damage']}", e["rect"].center, (255, 235, 160))
                    add_particles(e["rect"].center, e["type"]["bar"], 3)
                    if e["hp"] <= 0 and e in enemies:
                        drop_enemy_loot(e)
                        add_particles(e["rect"].center, (110, 25, 25), 12)
                        enemies.remove(e)
                        score += 1
                        coins += e["type"]["reward"]
                        add_floating_text(f"+{e['type']['reward']}", e["rect"].center, (255, 215, 90))
                    if not b.get("piercing", False):
                        hit = True
                for mb in hit_mini_bosses:
                    mb["hp"] -= b["damage"]
                    add_floating_text(f"-{b['damage']}", mb["rect"].center, (255, 235, 160))
                    add_particles(mb["rect"].center, (230, 170, 60), 4)
                    if mb["hp"] <= 0 and mb in mini_bosses:
                        add_particles(mb["rect"].center, (180, 70, 30), 18)
                        mini_bosses.remove(mb)
                        score += 5
                        coins += constants.MINI_BOSS_COIN_REWARD
                        add_floating_text(f"+{constants.MINI_BOSS_COIN_REWARD}", mb["rect"].center, (255, 215, 90))
                    if not b.get("piercing", False):
                        hit = True
                if not hit:
                    new_bullets.append(b)
            bullets = new_bullets
            if boss:
                if now - boss_last_shot > boss_shoot_delay:
                    dx = player.centerx - boss.centerx
                    dy = player.centery - boss.centery
                    dist = math.hypot(dx, dy)
                    if 0 < dist <= constants.BOSS_SIGHT_RANGE:
                        vx = dx / dist
                        vy = dy / dist
                        boss_bullets.append({
                            "rect": pygame.Rect(boss.centerx, boss.centery, 10, 10),
                            "vx": vx * 7,
                            "vy": vy * 7
                        })
                    boss_last_shot = now
            for b in boss_bullets:
                b["rect"].x += b["vx"]
                b["rect"].y += b["vy"]
            boss_bullets = [
                b for b in boss_bullets
                if 0 < b["rect"].x < world_width
                and 0 < b["rect"].y < world_height
            ]
            for b in mini_boss_bullets:
                b["rect"].x += b["vx"]
                b["rect"].y += b["vy"]
            mini_boss_bullets = [
                b for b in mini_boss_bullets
                if 0 < b["rect"].x < world_width
                and 0 < b["rect"].y < world_height
            ]
            for b in enemy_bullets:
                b["rect"].x += b["vx"]
                b["rect"].y += b["vy"]
            enemy_bullets = [
                b for b in enemy_bullets
                if 0 < b["rect"].x < world_width
                and 0 < b["rect"].y < world_height
            ]
            new_boss_bullets = []
            for b in boss_bullets:
                if player.colliderect(b["rect"]):
                    if hurt_player(constants.BOSS_BULLET_DAMAGE):
                        utils.stop_ambient_sound()
                        menus.game_over_screen(score)
                        return score
                else:
                    new_boss_bullets.append(b)
            boss_bullets = new_boss_bullets
            new_mini_boss_bullets = []
            for b in mini_boss_bullets:
                if player.colliderect(b["rect"]):
                    if hurt_player(constants.MINI_BOSS_BULLET_DAMAGE):
                        utils.stop_ambient_sound()
                        menus.game_over_screen(score)
                        return score
                else:
                    new_mini_boss_bullets.append(b)
            mini_boss_bullets = new_mini_boss_bullets
            new_enemy_bullets = []
            for b in enemy_bullets:
                if player.colliderect(b["rect"]):
                    if hurt_player(b["damage"]):
                        utils.stop_ambient_sound()
                        menus.game_over_screen(score)
                        return score
                else:
                    new_enemy_bullets.append(b)
            enemy_bullets = new_enemy_bullets
            for e in enemies:
                if player.colliderect(e["rect"]):
                    if hurt_player(e["type"]["damage"]):
                        utils.stop_ambient_sound()
                        menus.game_over_screen(score)
                        return score
            for mb in mini_bosses:
                if player.colliderect(mb["rect"]):
                    if hurt_player(constants.MINI_BOSS_TOUCH_DAMAGE):
                        utils.stop_ambient_sound()
                    menus.game_over_screen(score)
                    return score
            remaining_ammo_pickups = []
            for pickup in ammo_pickups:
                if player.colliderect(pickup["rect"]):
                    if current_mag_ammo < magazine_size():
                        current_mag_ammo = magazine_size()
                    else:
                        spare_mags = min(constants.MAX_SPARE_MAGAZINES, spare_mags + 1)
                    add_floating_text("+Ammo", player.center, (180, 220, 255))
                else:
                    remaining_ammo_pickups.append(pickup)
            ammo_pickups = remaining_ammo_pickups
            remaining_medkit_pickups = []
            for pickup in medkit_pickups:
                if player.colliderect(pickup["rect"]):
                    if medkits < constants.MAX_MEDKITS:
                        medkits += 1
                        add_floating_text("+Medkit", player.center, (120, 255, 140))
                    else:
                        remaining_medkit_pickups.append(pickup)
                else:
                    remaining_medkit_pickups.append(pickup)
            medkit_pickups = remaining_medkit_pickups
            if boss and player.colliderect(boss):
                if hurt_player(constants.BOSS_TOUCH_DAMAGE):
                    utils.stop_ambient_sound()
                menus.game_over_screen(score)
                return score
        if boss:
            new_bullets = []
            for b in bullets:
                if b["rect"].colliderect(boss):
                    boss_hp -= b["damage"]
                    add_floating_text(f"-{b['damage']}", boss.center, (255, 235, 160))
                    add_particles(boss.center, (255, 80, 80), 5)
                elif in_blast_radius(boss, bullet_center(b), b["blast_radius"]):
                    boss_hp -= b["damage"]
                    add_floating_text(f"-{b['damage']}", boss.center, (255, 235, 160))
                    add_particles(boss.center, (255, 120, 80), 8)
                else:
                    new_bullets.append(b)
            bullets = new_bullets
        if len(enemies) == 0 and len(mini_bosses) == 0 and boss is None and spawned >= enemy_count:
            if not waiting_for_next_wave:
                try_drop_medkit()
                coins += wave_clear_reward()
                prepare_wave_ammo()
                waiting_for_next_wave = True
                wave_break_end = now + constants.BREAK_DURATION
                house_entered_this_break = False
                house_message = "House open! Enter to rest."
                set_status_message(f"Wave clear! +{wave_clear_reward()} coins", 3000)
            if waiting_for_next_wave and now >= wave_break_end:
                waiting_for_next_wave = False
                previous_map_index = constants.map_index_for_wave(wave)
                wave += 1
                if constants.map_index_for_wave(wave) != previous_map_index:
                    move_player_to_current_map_center()
                    bullets.clear()
                    boss_bullets.clear()
                    mini_boss_bullets.clear()
                    enemy_bullets.clear()
                spawned = 0
                mini_bosses_spawned = 0
                enemy_count = constants.wave_size(wave)
                enemy_speed = constants.wave_config(wave)["speed"]
                spawn_rate = constants.wave_config(wave)["spawn_rate"]
                theme = constants.map_theme_for_wave(wave)
                set_status_message(f"{theme['name']} - Wave {constants.wave_in_map(wave)}/{constants.WAVES_PER_MAP} started", 2500)
                if constants.wave_config(wave).get("boss"):
                    boss = spawn_boss()
                    boss_max_hp = 70 * level if constants.wave_config(wave).get("final") else 20 * level
                    boss_hp = boss_max_hp
                    prepare_wave_ammo()
                elif pending_boss_level_up:
                    pending_boss_level_up = False
                    prepare_wave_ammo()
                else:
                    prepare_wave_ammo()
        if boss and boss_hp <= 0:
            boss_center = boss.center
            boss = None
            level += 1
            score += 25
            coins += constants.BOSS_COIN_REWARD
            add_floating_text(f"+{constants.BOSS_COIN_REWARD}", boss_center, (255, 215, 90))
            if wave >= constants.FINAL_WAVE:
                add_particles(boss_center, (180, 255, 190), 28)
                utils.stop_ambient_sound()
                menus.victory_screen(score)
                return score
            if not waiting_for_next_wave:
                pending_boss_level_up = True
                coins += wave_clear_reward()
                prepare_wave_ammo()
                waiting_for_next_wave = True
                wave_break_end = now + constants.BREAK_DURATION
                house_entered_this_break = False
                if constants.wave_in_map(wave) == constants.WAVES_PER_MAP:
                    next_theme = constants.map_theme_for_wave(wave + 1)
                    house_message = f"Next map unlocked: {next_theme['name']}."
                else:
                    house_message = "House open! Enter to rest."
        for text in floating_texts:
            text["y"] -= dt * 0.045
        floating_texts = [text for text in floating_texts if now < text["until"]]
        for particle in particles:
            particle["x"] += particle["vx"]
            particle["y"] += particle["vy"]
            particle["vy"] += 0.06
        particles = [particle for particle in particles if now < particle["until"]]
        camera_x, camera_y = get_camera()
        current_theme = constants.map_theme_for_wave(wave)
        constants.screen.blit(current_theme["surface"], (-camera_x, -camera_y))
        if waiting_for_next_wave:
            house_screen_rect = camera_rect(current_house_rect(), camera_x, camera_y)
            pygame.draw.rect(constants.screen, (255, 255, 255), house_screen_rect, 3)
        draw_player_character(player, camera_x, camera_y, is_moving, look_dir, constants.current_weapon, player_sprite, hurt=player_hurt_timer > 0)
        for e in enemies:
            zombie = e["rect"]
            zombie_screen = camera_rect(zombie, camera_x, camera_y)
            constants.screen.blit(e["sprite"], zombie_screen)
            hp_ratio = max(e["hp"], 0) / e["max_hp"]
            pygame.draw.rect(constants.screen, (40, 40, 40), (zombie_screen.x, zombie_screen.y - 8, zombie.width, 5))
            pygame.draw.rect(constants.screen, e["type"]["bar"], (zombie_screen.x, zombie_screen.y - 8, zombie.width * hp_ratio, 5))
        for mb in mini_bosses:
            mini_boss = mb["rect"]
            mini_boss_screen = camera_rect(mini_boss, camera_x, camera_y)
            constants.screen.blit(assets.enemy_p_img, mini_boss_screen)
            hp_ratio = max(mb["hp"], 0) / mb["max_hp"]
            pygame.draw.rect(constants.screen, (40, 40, 40), (mini_boss_screen.x, mini_boss_screen.y - 10, 70, 6))
            pygame.draw.rect(constants.screen, (230, 170, 60), (mini_boss_screen.x, mini_boss_screen.y - 10, 70 * hp_ratio, 6))
        if boss:
            boss_screen = camera_rect(boss, camera_x, camera_y)
            constants.screen.blit(assets.boss_img, boss_screen)
            hp_ratio = boss_hp / boss_max_hp
            pygame.draw.rect(constants.screen, (255, 255, 255), (boss_screen.x, boss_screen.y - 20, 220, 10))
            pygame.draw.rect(constants.screen, (255, 0, 0), (boss_screen.x, boss_screen.y - 20, 220 * hp_ratio, 10))
        for b in bullets:
            constants.screen.blit(assets.bullet_img, camera_rect(b["rect"], camera_x, camera_y))
        for b in boss_bullets:
            pygame.draw.rect(constants.screen, current_theme["boss_bullet_color"], camera_rect(b["rect"], camera_x, camera_y))
        for b in mini_boss_bullets:
            pygame.draw.rect(constants.screen, current_theme["mini_boss_bullet_color"], camera_rect(b["rect"], camera_x, camera_y))
        for b in enemy_bullets:
            pygame.draw.rect(constants.screen, current_theme["enemy_bullet_color"], camera_rect(b["rect"], camera_x, camera_y))
        for pickup in ammo_pickups:
            pickup_rect = camera_rect(pickup["rect"], camera_x, camera_y)
            pygame.draw.rect(constants.screen, (60, 110, 170), pickup_rect, border_radius=4)
            pygame.draw.rect(constants.screen, (190, 230, 255), pickup_rect, 2, border_radius=4)
        for pickup in medkit_pickups:
            pickup_rect = camera_rect(pickup["rect"], camera_x, camera_y)
            pygame.draw.rect(constants.screen, (40, 130, 70), pickup_rect, border_radius=4)
            pygame.draw.line(constants.screen, (220, 255, 220), pickup_rect.midleft, pickup_rect.midright, 3)
            pygame.draw.line(constants.screen, (220, 255, 220), pickup_rect.midtop, pickup_rect.midbottom, 3)
        for particle in particles:
            pygame.draw.circle(
                constants.screen,
                particle["color"],
                (int(particle["x"] - camera_x), int(particle["y"] - camera_y)),
                particle["radius"],
            )
        for text in floating_texts:
            text_surface = utils.font.render(text["text"], True, text["color"])
            constants.screen.blit(text_surface, (text["x"] - camera_x, text["y"] - camera_y))
        elapsed_seconds = (now - start_time) // 1000
        elapsed_minutes = elapsed_seconds // 60
        elapsed_seconds = elapsed_seconds % 60
        zombie_count = len(enemies) + len(mini_bosses)
        constants.screen.blit(utils.font.render(f"Map: {current_theme['name']} ({constants.map_index_for_wave(wave) + 1}/{len(constants.MAP_THEMES)})", True, (0,255,200)), (20, 20))
        constants.screen.blit(utils.font.render(f"Wave: {constants.wave_in_map(wave)}/{constants.WAVES_PER_MAP}  Total: {wave}/{constants.FINAL_WAVE}", True, (0,255,200)), (20, 60))
        constants.screen.blit(utils.font.render(f"Zombies left: {zombie_count}", True, (255,200,0)), (20, 100))
        constants.screen.blit(utils.font.render(f"Pos: ({player.x}, {player.y})", True, (220,220,220)), (20, 140))
        screen_rect = constants.screen.get_rect()
        panel_width = min(820, screen_rect.width - 40)
        panel_height = 112
        panel_x = screen_rect.centerx - panel_width // 2
        panel_y = screen_rect.bottom - panel_height
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel.fill((18, 20, 24, 210))
        constants.screen.blit(panel, (panel_x, panel_y))
        pygame.draw.rect(constants.screen, (95, 105, 120), (panel_x, panel_y, panel_width, panel_height), 2, border_radius=8)
        hp_ratio = max(player_hp, 0) / constants.PLAYER_MAX_HP
        hp_bar = pygame.Rect(panel_x + 24, panel_y + 58, 210, 18)
        pygame.draw.rect(constants.screen, (55, 20, 24), hp_bar, border_radius=5)
        pygame.draw.rect(constants.screen, (220, 65, 70), (hp_bar.x, hp_bar.y, int(hp_bar.width * hp_ratio), hp_bar.height), border_radius=5)
        hp_text = utils.font.render(f"{max(player_hp, 0)}/{constants.PLAYER_MAX_HP}", True, (255,245,245))
        constants.screen.blit(hp_text, (hp_bar.centerx - hp_text.get_width() // 2, hp_bar.centery - hp_text.get_height() // 2))
        ammo_label = "Reloading" if reloading else f"Ammo {current_mag_ammo}/{magazine_size()}"
        constants.screen.blit(utils.font.render(ammo_label, True, (180,220,255)), (panel_x + 270, panel_y + 18))
        constants.screen.blit(utils.font.render(f"Mags {spare_mags}/{constants.MAX_SPARE_MAGAZINES}", True, (190,235,205)), (panel_x + 270, panel_y + 58))
        constants.screen.blit(utils.font.render(f"Coins {coins}", True, (255,215,90)), (panel_x + 500, panel_y + 18))
        constants.screen.blit(utils.font.render(f"Medkits {medkits}/{constants.MAX_MEDKITS}", True, (120,255,140)), (panel_x + 500, panel_y + 58))
        constants.screen.blit(utils.font.render(f"{utils.weapon_display_name(constants.current_weapon)}  Lv {level}  {elapsed_minutes:02d}:{elapsed_seconds:02d}", True, (235,235,235)), (panel_x + 24, panel_y + 82))
        if reloading:
            reload_ratio = 1 - max(0, reload_end - now) / utils.weapon_reload_time(constants.current_weapon)
            reload_bar = pygame.Rect(panel_x + 270, panel_y + 50, 190, 8)
            pygame.draw.rect(constants.screen, (35, 45, 55), reload_bar, border_radius=4)
            pygame.draw.rect(constants.screen, (110, 190, 255), (reload_bar.x, reload_bar.y, int(reload_bar.width * reload_ratio), reload_bar.height), border_radius=4)
        elif current_mag_ammo <= 0 and not waiting_for_next_wave:
            reload_hint = "Press [R] to reload" if spare_mags > 0 else "Out of ammo! Buy ammo in the house."
            constants.screen.blit(utils.font.render(reload_hint, True, (255,120,120)), (panel_x + 270, panel_y - 42))
        if now < status_message_until:
            status_surface = utils.font.render(status_message, True, (255, 245, 190))
            constants.screen.blit(status_surface, (screen_rect.centerx - status_surface.get_width() // 2, 170))
        if waiting_for_next_wave:
            remaining = max(0, (wave_break_end - now) // 1000)
            constants.screen.blit(utils.font.render(f"House is open! Enter [E] ({remaining}s)", True, (255,255,180)), (20, 180))
            if player.colliderect(current_house_rect()):
                constants.screen.blit(utils.font.render("Press [E] to enter house", True, (180,255,255)), (20, 220))
            if house_message:
                constants.screen.blit(utils.font.render(house_message, True, (180,255,180)), (20, 260))
        if cheat_chat_open:
            draw_cheat_chat()
        if paused:
            menus.draw_pause_menu()
        else:
            pygame.mouse.set_visible(False)
        pygame.display.flip()
