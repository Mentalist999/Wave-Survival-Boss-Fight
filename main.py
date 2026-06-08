#!/usr/bin/env python3
import os
import pygame
import constants
import assets
import utils
import menus
import save_data
import game_loop


os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.mixer.pre_init(22050, -16, 1, 512)
pygame.init()
utils.init_fonts()

constants.screen = pygame.display.set_mode((constants.WIDTH, constants.HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Wave Survival Boss Fight")
constants.clock = pygame.time.Clock()
assets.init_assets()

if __name__ == "__main__":
    save = save_data.load_save_data()
    best_score = int(save.get("best_score", 0))
    last_score = 0
    
    saved_weapons = save.get("unlocked_weapons", [])
    constants.unlocked_weapons.update(weapon for weapon in saved_weapons if weapon in assets.WEAPONS)
    
    saved_weapon = save.get("current_weapon")
    if saved_weapon in constants.unlocked_weapons:
        constants.current_weapon = saved_weapon
    
    constants.MAX_MEDKITS = max(3, min(constants.MAX_MEDKIT_CAPACITY, int(save.get("max_medkits", constants.MAX_MEDKITS))))
    
    saved_upgrades = save.get("weapon_upgrades", {})
    for weapon_key, upgrades in saved_upgrades.items():
        if weapon_key in constants.weapon_upgrades and isinstance(upgrades, dict):
            for upgrade_key in constants.weapon_upgrades[weapon_key]:
                constants.weapon_upgrades[weapon_key][upgrade_key] = max(
                    0,
                    min(constants.MAX_WEAPON_UPGRADE_LEVEL, int(upgrades.get(upgrade_key, 0)))
                )
    
    saved_settings = save.get("settings", {})
    if isinstance(saved_settings, dict):
        constants.SETTINGS["music_volume"] = max(0, min(1, float(saved_settings.get("music_volume", constants.SETTINGS["music_volume"]))))
        constants.SETTINGS["sfx_volume"] = max(0, min(1, float(saved_settings.get("sfx_volume", constants.SETTINGS["sfx_volume"]))))
        constants.SETTINGS["fullscreen"] = bool(saved_settings.get("fullscreen", constants.SETTINGS["fullscreen"]))
        saved_language = saved_settings.get("language", constants.SETTINGS["language"])
        if saved_language in constants.LANGUAGES:
            constants.SETTINGS["language"] = saved_language
        if not constants.SETTINGS["fullscreen"]:
            constants.screen = pygame.display.set_mode((constants.WIDTH, constants.HEIGHT))

    while True:
        utils.stop_ambient_sound()
        if not menus.menu(best_score, last_score):
            save_data.save_progress(best_score)
            break

        score = game_loop.game()
        if score is None:
            score = 0

        last_score = score
        if score > best_score:
            best_score = score
        save_data.save_progress(best_score)

    pygame.quit()
