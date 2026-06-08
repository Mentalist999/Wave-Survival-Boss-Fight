import pygame
import constants
import assets
import utils
import save_data

resume_rect = None
settings_rect = None
exit_rect = None
selected = 0


def shop_menu(score):
    global selected
    selected = 0
    message = utils.tr("buy_or_select_weapon")
    pygame.mouse.set_visible(True)

    def option_label(option):
        if option == "back":
            return utils.tr("back")
        weapon = assets.WEAPONS[option]
        state = utils.tr("selected") if option == constants.current_weapon else (
            utils.tr("owned") if option in constants.unlocked_weapons else f"{weapon['cost']} {utils.tr('points')}"
        )
        return f"{utils.weapon_display_name(option)} - {state}"

    def activate_choice(choice):
        nonlocal message
        if choice == "back":
            return True
        weapon = assets.WEAPONS[choice]
        if choice in constants.unlocked_weapons:
            constants.current_weapon = choice
            message = f"{utils.tr('selected')}: {utils.weapon_display_name(choice)}"
        elif score >= weapon["cost"]:
            constants.unlocked_weapons.add(choice)
            constants.current_weapon = choice
            message = f"{utils.tr('bought_and_selected')}: {utils.weapon_display_name(choice)}"
        else:
            message = f"{utils.tr('need')} {weapon['cost']} {utils.tr('points')} to buy {utils.weapon_display_name(choice)}"
        return False

    options = constants.weapon_order + ["back"]
    while True:
        constants.screen.blit(assets.menu_img, (0, 0))
        button_x = 100
        button_y = constants.HEIGHT // 2 - 80
        labels = [option_label(option) for option in options]
        option_rects = []

        for idx, label in enumerate(labels):
            text_width, text_height = utils.ui_font.size(label)
            option_rects.append(pygame.Rect(button_x - 10, button_y + idx * 50 - 4, text_width + 20, text_height + 8))

        mouse_pos = pygame.mouse.get_pos()
        for idx, rect in enumerate(option_rects):
            if rect.collidepoint(mouse_pos):
                selected = idx

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                if event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                if event.key == pygame.K_RETURN:
                    if activate_choice(options[selected]):
                        return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for idx, rect in enumerate(option_rects):
                    if rect.collidepoint(event.pos):
                        selected = idx
                        if activate_choice(options[selected]):
                            return

        utils.draw_text_center(utils.tr("weapon_shop").upper(), constants.HEIGHT // 4, (255, 230, 200), font=utils.title_font, glow_color=(220, 140, 60), glow_radius=2)
        utils.draw_text_center(f"{utils.tr('your_points')}: {score}", constants.HEIGHT // 4 + 80, (240, 210, 180), font=utils.stats_font)
        utils.draw_text_center(message, constants.HEIGHT // 4 + 120, (255, 235, 170), font=utils.stats_font)

        for idx, label in enumerate(labels):
            if idx == selected:
                utils.draw_text(
                    label,
                    (button_x, button_y + idx * 50),
                    (255, 245, 220),
                    font=utils.ui_font,
                    glow_color=(210, 120, 40),
                    glow_radius=1
                )
            else:
                utils.draw_text(label, (button_x, button_y + idx * 50), (220, 195, 170), font=utils.ui_font)

        pygame.display.flip()
        constants.clock.tick(60)


def house_interior(coins, current_mag_ammo, spare_mags, player_hp):
    global selected
    current_coins = coins
    options = constants.weapon_order + [
        "buy_ammo",
        "upgrade_damage",
        "upgrade_magazine",
        "upgrade_reload",
        "rest_heal",
        "upgrade_medkit_capacity",
        "exit_house",
    ]
    selected = 0
    message = utils.tr("welcome_safe_house")
    pygame.mouse.set_visible(True)

    def selected_weapon():
        return assets.WEAPONS[constants.current_weapon]

    def ammo_is_full():
        return current_mag_ammo >= utils.weapon_magazine_size(constants.current_weapon) and spare_mags >= constants.MAX_SPARE_MAGAZINES

    def upgrade_label(option, upgrade_key, title):
        level = utils.weapon_upgrade_level(constants.current_weapon, upgrade_key)
        cost = utils.weapon_upgrade_cost(constants.current_weapon, upgrade_key)
        if cost is None:
            return f"{title} - Max ({level}/{constants.MAX_WEAPON_UPGRADE_LEVEL})"
        return f"{title} - {cost} coins ({level}/{constants.MAX_WEAPON_UPGRADE_LEVEL})"

    def option_label(option):
        if option == "exit_house":
            return utils.tr("exit_house")
        if option == "buy_ammo":
            weapon = selected_weapon()
            if ammo_is_full():
                state = utils.tr("full")
            else:
                state = f"{weapon['ammo_cost']} {utils.tr('coins')} ({utils.tr('plus_mag')})"
            return f"{utils.tr('buy_ammo')} - {state}"
        if option == "upgrade_damage":
            return upgrade_label(option, "damage", utils.tr("upgrade_damage"))
        if option == "upgrade_magazine":
            return upgrade_label(option, "magazine", utils.tr("upgrade_magazine"))
        if option == "upgrade_reload":
            return upgrade_label(option, "reload", utils.tr("upgrade_reload"))
        if option == "rest_heal":
            if player_hp >= constants.PLAYER_MAX_HP:
                state = utils.tr("full")
            else:
                state = f"50 {utils.tr('coins')} (restore 50 HP)"
            return f"{utils.tr('rest_heal')} - {state}"
        if option == "upgrade_medkit_capacity":
            if constants.MAX_MEDKITS >= constants.MAX_MEDKIT_CAPACITY:
                state = utils.tr("full")
            else:
                state = f"100 {utils.tr('coins')} (+1 slot)"
            return f"{utils.tr('upgrade_medkit_capacity')} - {state}"
        weapon = assets.WEAPONS[option]
        state = utils.tr("selected") if option == constants.current_weapon else (
            utils.tr("owned") if option in constants.unlocked_weapons else f"{weapon['cost']} {utils.tr('coins')}"
        )
        return f"{utils.weapon_display_name(option)} - {state}"

    def activate_choice(choice):
        nonlocal message, current_coins, current_mag_ammo, spare_mags, player_hp
        if choice == "exit_house":
            return True
        if choice == "buy_ammo":
            weapon = selected_weapon()
            if ammo_is_full():
                message = utils.tr("full")
                return False
            if current_coins < weapon["ammo_cost"]:
                message = f"{utils.tr('need')} {weapon['ammo_cost']} {utils.tr('coins')} to buy ammo"
                return False
            current_coins -= weapon["ammo_cost"]
            if current_mag_ammo < utils.weapon_magazine_size(constants.current_weapon):
                current_mag_ammo = utils.weapon_magazine_size(constants.current_weapon)
                message = f"{utils.weapon_display_name(constants.current_weapon)} loaded"
            else:
                spare_mags += 1
                message = f"{utils.tr('bought_and_selected')} ({spare_mags}/{constants.MAX_SPARE_MAGAZINES})"
            return False
        if choice in ("upgrade_damage", "upgrade_magazine", "upgrade_reload"):
            upgrade_key = {
                "upgrade_damage": "damage",
                "upgrade_magazine": "magazine",
                "upgrade_reload": "reload",
            }[choice]
            cost = utils.weapon_upgrade_cost(constants.current_weapon, upgrade_key)
            if cost is None:
                message = utils.tr("full")
                return False
            if current_coins < cost:
                message = f"Need {cost} coins for upgrade"
                return False
            current_coins -= cost
            constants.weapon_upgrades[constants.current_weapon][upgrade_key] += 1
            if upgrade_key == "magazine":
                current_mag_ammo = utils.weapon_magazine_size(constants.current_weapon)
            message = f"{utils.weapon_display_name(constants.current_weapon)} {upgrade_key} upgraded"
            return False
        if choice == "rest_heal":
            if player_hp >= constants.PLAYER_MAX_HP:
                message = utils.tr("full")
                return False
            if current_coins >= 50:
                current_coins -= 50
                player_hp = min(constants.PLAYER_MAX_HP, player_hp + 50)
                message = utils.tr("rest_heal")
                return False
            else:
                message = f"{utils.tr('need')} 50 {utils.tr('coins')} to rest"
                return False
        if choice == "upgrade_medkit_capacity":
            if constants.MAX_MEDKITS >= constants.MAX_MEDKIT_CAPACITY:
                message = utils.tr("full")
                return False
            if current_coins >= 100:
                current_coins -= 100
                constants.MAX_MEDKITS += 1
                message = f"Medkit capacity upgraded! Now: {constants.MAX_MEDKITS}"
                return False
            else:
                message = f"{utils.tr('need')} 100 {utils.tr('coins')} to upgrade"
                return False
        weapon = assets.WEAPONS[choice]
        if choice in constants.unlocked_weapons:
            constants.current_weapon = choice
            current_mag_ammo = utils.weapon_magazine_size(constants.current_weapon)
            spare_mags = constants.BASE_SPARE_MAGAZINES
            message = f"{utils.tr('selected')}: {utils.weapon_display_name(choice)}"
        elif current_coins >= weapon["cost"]:
            current_coins -= weapon["cost"]
            constants.unlocked_weapons.add(choice)
            constants.current_weapon = choice
            current_mag_ammo = utils.weapon_magazine_size(constants.current_weapon)
            spare_mags = constants.BASE_SPARE_MAGAZINES
            message = f"{utils.tr('bought_and_selected')}: {utils.weapon_display_name(choice)}"
        else:
            message = f"{utils.tr('need')} {weapon['cost']} {utils.tr('coins')} to buy {utils.weapon_display_name(choice)}"
        return False

    while True:
        constants.screen.fill((40, 30, 20))
        outer_frame = constants.screen.get_rect().inflate(-110, -110)
        inner_frame = constants.screen.get_rect().inflate(-135, -135)
        pygame.draw.rect(constants.screen, (80, 60, 40), outer_frame, 8)
        pygame.draw.rect(constants.screen, (100, 80, 60), inner_frame, 2)
        pygame.draw.line(constants.screen, (120, 100, 80), (inner_frame.left + 20, inner_frame.bottom - 110), (inner_frame.right - 20, inner_frame.bottom - 110), 2)

        button_x = 80
        button_y = 80
        option_step = 42
        option_font = utils.stats_font
        labels = [option_label(option) for option in options]
        option_rects = []

        for idx, label in enumerate(labels):
            text_width, text_height = option_font.size(label)
            option_rects.append(pygame.Rect(button_x - 10, button_y + idx * option_step - 4, text_width + 20, text_height + 8))

        mouse_pos = pygame.mouse.get_pos()
        for idx, rect in enumerate(option_rects):
            if rect.collidepoint(mouse_pos):
                selected = idx

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return current_coins, current_mag_ammo, spare_mags, player_hp
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                if event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                if event.key == pygame.K_RETURN:
                    choice = options[selected]
                    if activate_choice(choice):
                        return current_coins, current_mag_ammo, spare_mags, player_hp
                if event.key == pygame.K_ESCAPE:
                    return current_coins, current_mag_ammo, spare_mags, player_hp
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for idx, rect in enumerate(option_rects):
                    if rect.collidepoint(event.pos):
                        selected = idx
                        if activate_choice(options[selected]):
                            return current_coins, current_mag_ammo, spare_mags, player_hp

        utils.draw_text_center("SAFE HOUSE", 80, (200, 180, 160), font=utils.title_font, glow_color=(150, 120, 80), glow_radius=2)
        utils.draw_text_center(f"Available Coins: {current_coins}", 165, (180, 160, 140), font=utils.stats_font)
        utils.draw_text_center(message, inner_frame.bottom - 70, (200, 220, 180), font=utils.stats_font)

        for idx, label in enumerate(labels):
            if idx == selected:
                utils.draw_text(
                    label,
                    (button_x, button_y + idx * option_step),
                    (255, 245, 220),
                    font=option_font,
                    glow_color=(200, 160, 100),
                    glow_radius=1
                )
            else:
                color = (220, 200, 180) if idx < len(constants.weapon_order) else (180, 200, 200)
                utils.draw_text(label, (button_x, button_y + idx * option_step), color, font=option_font)

        pygame.display.flip()
        constants.clock.tick(60)

    return current_coins, current_mag_ammo, spare_mags, player_hp


def settings_menu():
    global selected
    options = ["music", "sfx", "fullscreen", "language", "back"]
    selected = 0
    pygame.mouse.set_visible(True)

    def option_label(option):
        if option == "music":
            return f"{utils.tr('music_volume')}: {int(constants.SETTINGS['music_volume'] * 100)}%"
        if option == "sfx":
            return f"{utils.tr('sfx_volume')}: {int(constants.SETTINGS['sfx_volume'] * 100)}%"
        if option == "fullscreen":
            state = utils.tr("on") if constants.SETTINGS["fullscreen"] else utils.tr("off")
            return f"{utils.tr('fullscreen')}: {state}"
        if option == "language":
            return f"{utils.tr('language')}: {constants.LANGUAGES.get(constants.SETTINGS['language'], 'English')}"
        return utils.tr("back")

    def change_value(option, amount):
        changed = False
        if option == "music":
            constants.SETTINGS["music_volume"] = max(0, min(1, constants.SETTINGS["music_volume"] + amount))
            if pygame.mixer.get_init():
                pygame.mixer.music.set_volume(constants.SETTINGS["music_volume"])
            changed = True
        elif option == "sfx":
            constants.SETTINGS["sfx_volume"] = max(0, min(1, constants.SETTINGS["sfx_volume"] + amount))
            changed = True
        elif option == "fullscreen" and amount != 0:
            constants.SETTINGS["fullscreen"] = not constants.SETTINGS["fullscreen"]
            flags = pygame.FULLSCREEN if constants.SETTINGS["fullscreen"] else 0
            constants.screen = pygame.display.set_mode((constants.WIDTH, constants.HEIGHT), flags)
            changed = True
        elif option == "language" and amount != 0:
            utils.cycle_language(1 if amount > 0 else -1)
            changed = True
        if changed:
            save_data.save_settings_only()

    while True:
        constants.screen.blit(assets.menu_img, (0, 0))
        labels = [option_label(option) for option in options]
        button_x = 80
        button_y = constants.HEIGHT // 2 - 80
        option_rects = []

        for idx, label in enumerate(labels):
            text_width, text_height = utils.ui_font.size(label)
            option_rects.append(pygame.Rect(button_x - 10, button_y + idx * 70 - 4, text_width + 20, text_height + 8))

        mouse_pos = pygame.mouse.get_pos()
        for idx, rect in enumerate(option_rects):
            if rect.collidepoint(mouse_pos):
                selected = idx

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_LEFT:
                    change_value(options[selected], -0.1)
                elif event.key == pygame.K_RIGHT:
                    change_value(options[selected], 0.1)
                elif event.key == pygame.K_RETURN:
                    if options[selected] == "back":
                        return
                    change_value(options[selected], 1)
                elif event.key == pygame.K_ESCAPE:
                    return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for idx, rect in enumerate(option_rects):
                    if rect.collidepoint(event.pos):
                        selected = idx
                        if options[selected] == "back":
                            return
                        change_value(options[selected], 1)

        utils.draw_text_center(utils.tr("settings").upper(), constants.HEIGHT // 3 - 70, (255, 230, 200), font=utils.title_font, glow_color=(220, 140, 60), glow_radius=2)
        utils.draw_text_center(utils.tr("settings_hint"), constants.HEIGHT // 3, (230, 215, 190), font=utils.stats_font)

        for idx, label in enumerate(labels):
            color = (255, 245, 220) if idx == selected else (220, 195, 170)
            glow = (210, 120, 40) if idx == selected else None
            utils.draw_text(label, (button_x, button_y + idx * 70), color, font=utils.ui_font, glow_color=glow, glow_radius=1 if glow else 0)

        pygame.display.flip()
        constants.clock.tick(60)


def menu(best_score, last_score):
    options = ["start", "shop", "settings", "quit"]
    selected = 0
    pygame.mouse.set_visible(True)

    def activate_choice(choice):
        if choice == "start":
            return True
        if choice == "shop":
            shop_menu(best_score)
            return None
        if choice == "settings":
            settings_menu()
            return None
        return False

    def option_label(option):
        if option == "start":
            return utils.tr("start_game")
        if option == "shop":
            return utils.tr("weapon_shop")
        if option == "settings":
            return utils.tr("settings")
        return utils.tr("quit")

    while True:
        constants.screen.blit(assets.menu_img, (0, 0))
        button_x = 80
        button_y = constants.HEIGHT // 2 + 40
        option_rects = []
        labels = [option_label(option) for option in options]
        for idx, label in enumerate(labels):
            text_width, text_height = utils.ui_font.size(label)
            option_rects.append(pygame.Rect(button_x - 10, button_y + idx * 80 - 4, text_width + 20, text_height + 8))

        mouse_pos = pygame.mouse.get_pos()
        for idx, rect in enumerate(option_rects):
            if rect.collidepoint(mouse_pos):
                selected = idx

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                if event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                if event.key == pygame.K_RETURN:
                    result = activate_choice(options[selected])
                    if result is not None:
                        return result
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for idx, rect in enumerate(option_rects):
                    if rect.collidepoint(event.pos):
                        selected = idx
                        result = activate_choice(options[selected])
                        if result is not None:
                            return result

        utils.draw_text_center(
            "Wave Survival Boss Fight",
            constants.HEIGHT // 3 - 40,
            (255, 230, 200),
            font=utils.title_font,
            glow_color=(220, 140, 60),
            glow_radius=2
        )
        utils.draw_text_center(f"{utils.tr('last_score')}: {last_score}", constants.HEIGHT // 3 + 60, (240, 210, 180), font=utils.stats_font)
        utils.draw_text_center(f"{utils.tr('record')}: {best_score}", constants.HEIGHT // 3 + 110, (240, 210, 180), font=utils.stats_font)

        for idx, label in enumerate(labels):
            if idx == selected:
                utils.draw_text(
                    label,
                    (button_x, button_y + idx * 80),
                    (255, 245, 220),
                    font=utils.ui_font,
                    glow_color=(210, 120, 40),
                    glow_radius=1
                )
            else:
                utils.draw_text(label, (button_x, button_y + idx * 80), (220, 195, 170), font=utils.ui_font)

        pygame.display.flip()
        constants.clock.tick(60)


def game_over_screen(score):
    pygame.mouse.set_visible(True)
    while True:
        constants.screen.fill((10, 10, 20))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return
        utils.draw_text("GAME OVER", (constants.WIDTH//2 - 180, constants.HEIGHT//3 - 40), (255, 80, 80), 64)
        utils.draw_text(f"Final Score: {score}", (constants.WIDTH//2 - 150, constants.HEIGHT//3 + 40), (255, 255, 255), 40)
        pygame.display.flip()
        constants.clock.tick(60)


def victory_screen(score):
    pygame.mouse.set_visible(True)
    while True:
        constants.screen.fill((12, 24, 18))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return
        utils.draw_text_center("VICTORY", constants.HEIGHT // 3 - 40, (180, 255, 190), 64, font=utils.title_font, glow_color=(60, 160, 90), glow_radius=2)
        utils.draw_text_center(f"Final Score: {score}", constants.HEIGHT // 3 + 55, (245, 245, 220), font=utils.stats_font)
        utils.draw_text_center("Press Enter", constants.HEIGHT // 3 + 110, (210, 230, 210), font=utils.stats_font)
        pygame.display.flip()
        constants.clock.tick(60)


def draw_pause_menu():
    global resume_rect, settings_rect, exit_rect, selected
    overlay = pygame.Surface((constants.WIDTH, constants.HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))
    constants.screen.blit(overlay, (0, 0))
    pygame.mouse.set_visible(True)
    options = [utils.tr("resume_game"), utils.tr("settings"), utils.tr("exit_to_menu")]
    button_x = 80
    button_y = constants.HEIGHT // 2 + 40
    option_rects = []
    for idx, option in enumerate(options):
        text_width, text_height = utils.ui_font.size(option)
        option_rects.append(pygame.Rect(button_x - 10, button_y + idx * 80 - 4, text_width + 20, text_height + 8))
    mouse_pos = pygame.mouse.get_pos()
    selected = -1
    for idx, rect in enumerate(option_rects):
        if rect.collidepoint(mouse_pos):
            selected = idx
    for idx, option in enumerate(options):
        color = (255, 255, 0) if idx == selected else (255, 255, 255)
        utils.draw_text(option, (button_x, button_y + idx * 80), color, font=utils.ui_font)
    resume_rect = option_rects[0]
    settings_rect = option_rects[1]
    exit_rect = option_rects[2]
