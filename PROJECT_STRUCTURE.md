# Структура проекта Wave Survival Boss Fight

## Модули

### `main.py` (главный файл)
Точка входа приложения. Инициализирует Pygame, загружает сохранённые данные и запускает главный цикл меню/игры.

### `constants.py` (константы и конфигурация)
- Все константы игры (размеры, урон, награды)
- Словари текстов (LANGUAGES, TEXT)
- Конфигурация оружия (WEAPONS, weapon_order)
- Конфигурация врагов (ENEMY_TYPES)
- Конфигурация карт (MAP_THEMES, BASE_WAVE_CONFIGS)
- Функции для работы с волнами и картами
- Глобальные переменные (screen, clock, current_weapon, unlocked_weapons, etc.)

### `utils.py` (утилиты и помощники)
- Функции для загрузки и отрисовки шрифтов
- Функции отрисовки текста (`draw_text`, `draw_text_center`)
- Управление музыкой (`start_ambient_sound`, `stop_ambient_sound`)
- Функции для оружия (`weapon_upgrade_level`, `weapon_damage`, `weapon_magazine_size`, `weapon_reload_time`)
- Функции локализации (`tr` для перевода, `weapon_display_name`, `cycle_language`)
- Утилита `tint_surface` для тинирования спрайтов
- Объекты шрифтов (font, ui_font, title_font, stats_font)

### `assets.py` (загрузка ресурсов)
- TMX парсер для загрузки карт из Tiled (`load_tmx_map`)
- Функции загрузки изображений (`load`, `load_optional`, `load_optional_cropped`)
- Функция генерации изображений оружия (`create_weapon_image`)
- Загрузка всех спрайтов (игроки, враги, пули, босс, оружие)
- Загрузка и обработка изображений разных частей персонажа (PLAYER_PARTS)
- Применение эффектов к картам (`create_themed_map_surface`)

### `save_data.py` (сохранения)
- `load_save_data()` - загрузить сохранённые данные из JSON
- `save_progress()` - сохранить прогресс (очки, оружие, улучшения)
- `save_settings_only()` - сохранить только настройки

### `menus.py` (меню и интерфейс)
- `shop_menu()` - меню покупки оружия
- `house_interior()` - интерьер безопасного дома (покупка, улучшения, исцеление)
- `settings_menu()` - меню настроек (музыка, громкость, разрешение, язык)
- `menu()` - главное меню
- `game_over_screen()` - экран проигрыша
- `victory_screen()` - экран победы
- `draw_pause_menu()` - меню паузы

### `game_loop.py` (основной игровой цикл)
- `draw_player_character()` - отрисовка игрока с анимацией
- `game()` - главный игровой цикл с логикой:
  - Движение игрока
  - Стрельба и перезарядка
  - Спавн врагов
  - Движение врагов и боссов
  - Система волн
  - Система домика отдыха
  - Окончание игры и победа
  - Отрисовка UI

## Разделение ответственности

| Задача | Модуль |
|--------|--------|
| Константы и конфиг | `constants.py` |
| Загрузка ресурсов | `assets.py` |
| Утилиты и помощники | `utils.py` |
| Менеджмент сохранений | `save_data.py` |
| Интерфейс (меню, дом) | `menus.py` |
| Игровой цикл | `game_loop.py` |
| Инициализация и запуск | `main.py` |

## Поиск по функциям

Ищите код по типу выполняемой задачи:

- **Враги и их поведение** → `constants.py` (ENEMY_TYPES), `game_loop.py` (spawn_enemy, движение врагов)
- **Оружие и стрельба** → `constants.py` (WEAPONS), `assets.py` (WEAPON_IMAGES), `game_loop.py` (make_player_bullets)
- **Волны и уровни** → `constants.py` (BASE_WAVE_CONFIGS, MAP_THEMES), `game_loop.py` (волновая система)
- **Интерфейс** → `menus.py`
- **Шрифты и текст** → `utils.py`
- **Карты** → `assets.py` (load_tmx_map), `constants.py` (MAP_THEMES)
- **Логика урона и HP** → `game_loop.py` (hurt_player, урон врагам/боссам)
