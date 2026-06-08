import json
import os
import constants


def load_save_data():
    if not os.path.exists(constants.SAVE_PATH):
        return {}
    try:
        with open(constants.SAVE_PATH, "r", encoding="utf-8") as save_file:
            return json.load(save_file)
    except (OSError, json.JSONDecodeError) as e:
        print(f"Save data ignored: {e}")
        return {}


def save_progress(best_score):
    data = {
        "best_score": best_score,
        "unlocked_weapons": sorted(constants.unlocked_weapons),
        "current_weapon": constants.current_weapon,
        "max_medkits": constants.MAX_MEDKITS,
        "weapon_upgrades": constants.weapon_upgrades,
        "settings": constants.SETTINGS,
    }
    try:
        with open(constants.SAVE_PATH, "w", encoding="utf-8") as save_file:
            json.dump(data, save_file, indent=2)
    except OSError as e:
        print(f"Save failed: {e}")


def save_settings_only():
    data = load_save_data()
    data["settings"] = constants.SETTINGS
    try:
        with open(constants.SAVE_PATH, "w", encoding="utf-8") as save_file:
            json.dump(data, save_file, indent=2)
    except OSError as e:
        print(f"Settings save failed: {e}")
