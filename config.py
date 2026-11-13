# -*- coding: utf-8 -*-
"""
Application configuration and constants for the Dam Break control system.
"""

# ---------------------------------------------------------------------------
# App metadata
# ---------------------------------------------------------------------------
APP_NAME = "Dambreak"
APP_VERSION_INFO = (
    "Controle de Dambreak\n"
    "Versão Alpha 0.0.1\n"
    "Última modificação: 03/12/2021"
)
AUTHOR = "CaioPorta"
CREATED_FOR = "Professor Geraldo de Freitas Maciel\nUNESP - FEIS"

# ---------------------------------------------------------------------------
# Parameter limits
# ---------------------------------------------------------------------------
PARAM_LIMITS = {
    "acceleration": {"min": 0.0, "max": 1.0},
    "velocity": {"min": 0.0, "max": 10.0},
    "position": {"min": 0.0, "max": 300.0},
    "inclination": {"min": 0.0, "max": 20.0},
}

# Precision step values (all precision levels use the same step)
PRECISION_STEP = 0.1

# Precision options displayed in the UI
PRECISION_OPTIONS = ["1", "1/2", "1/4", "1/8", "1/16", "1/32"]
DEFAULT_PRECISION = "1/32"

# ---------------------------------------------------------------------------
# Screen sizing ratios (relative to screen or widget dimensions)
# ---------------------------------------------------------------------------
SCREEN_RATIOS = {
    "title_height": 1 / 20,
    "spacer_height": 1 / 30,
    "button_size": 1 / 7,
    "theme_button_width": 1 / 15,
    "execute_button_width": 1 / 3,
    "text_field_width": 1 / 10,
    "history_table_width": 0.3,
    "macro_panel_width": 2 / 7,
    "macro_button_height": 1 / 15,
}

# ---------------------------------------------------------------------------
# Theme definitions
# ---------------------------------------------------------------------------
THEMES = {
    "Bright": {
        "background": "gray",
        "background_secondary": "white",
        "font": "black",
        "clear_db_icon": "./images/Limpar DB.png",
    },
    "Dark": {
        "background": "black",
        "background_secondary": "gray",
        "font": "white",
        "clear_db_icon": "./images/Limpar DB - Tema escuro.png",
    },
}

# ---------------------------------------------------------------------------
# Font definitions  (name, size, bold?)
# ---------------------------------------------------------------------------
FONTS = {
    "small": ("Times New Roman", 8, False),
    "normal": ("Times New Roman", 9, False),
    "base": ("Times New Roman", 10, False),
    "medium": ("Times New Roman", 12, False),
    "large": ("Times New Roman", 14, False),
    "xlarge": ("Times New Roman", 16, False),
    "xxlarge": ("Times New Roman", 18, False),
    "title": ("Times New Roman", 20, True),
    "heading": ("Times New Roman", 22, True),
    "section": ("Times New Roman", 24, False),
    "big": ("Cooper Black", 26, True),
    "bigger": ("Cooper Black", 28, True),
    "largest": ("Cooper Black", 30, True),
}

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
IMAGES_DIR = "./images"
ICON_PATH = "./images/Dambreak IHM icon.png"
SAVE_ICON = "./images/save.png"
ARDUINO_ICON = "./images/arduino-logo.png"
INFO_ICON = "./images/Info.png"

# Database
DB_PATH = "Database_Dambreak.db"

# Default macro names
DEFAULT_MACRO_NAMES = [f"Macro{i + 1}" for i in range(8)]

# Password for protected actions
PASSWORD = "0000"

# Arduino
ARDUINO_BAUDRATE = 9600
ARDUINO_TIMEOUT = 1

# Worker thread interval (seconds)
THREAD_INTERVAL = 0.2

# CSV export
CSV_HEADER = ["h (mm)", "v (mm/s)", "a (mm/s2)", "\u03b1 (graus)", "Atraso (s)"]

# Macro table columns
MACRO_TABLE_COLUMNS = ["h (mm)", "v (mm/s)", "a (mm/s²)", "\u03b1 (°)", "Atraso (s)"]

# Macro input masks
INPUT_MASKS = {
    "acceleration": "99.9mm/s²",
    "velocity": "99.9mm/s",
    "position": "999.9mm",
    "inclination": "99.9°",
}
