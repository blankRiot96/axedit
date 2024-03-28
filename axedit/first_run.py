"""File to check and perform certain actions before running the editor"""

import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import platform
from pathlib import Path

import pygame
import tomlkit

from axedit import shared
from axedit.funcs import get_config, get_config_path, offset_font_size, reset_config
from axedit.themes import apply_theme

# Create the config folder if it doesnt exist
config_path = get_config_path()
if not config_path.exists():
    config_path.mkdir()


# Add the config file if it doesnt exist
config_file_path = config_path / "config.toml"
if not config_file_path.exists():
    reset_config()

# Apply config
# Apply font
shared.config = get_config()
if shared.config["font"]["path"] not in ("default", False):
    shared.FONT = pygame.Font(
        shared.config["font"]["path"], shared.config["font"]["size"]
    )
elif shared.config["font"]["family"]:
    shared.FONT = pygame.sysfont.SysFont(
        shared.config["font"]["family"], shared.config["font"]["size"]
    )
# Apply font size
offset_font_size(shared.config["font"]["size"] - shared.FONT_SIZE)
apply_theme(shared.config["theme"]["name"])
