"""File to check and perform certain actions before running the editor"""

import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import platform
import sys
from pathlib import Path

import pygame
import tomlkit

from axedit import shared
from axedit.funcs import get_config, get_config_path, offset_font_size, reset_config
from axedit.logs import logger
from axedit.themes import apply_theme

# Create the config folder if it doesnt exist
config_path = get_config_path()
if not config_path.exists():
    config_path.mkdir()


# Add the config file if it doesnt exist
config_file_path = config_path / "config.toml"
if not config_file_path.exists():
    reset_config()


def apply_config():
    # Apply font
    shared.config = get_config()
    shared.FONT_SIZE = shared.config["font"]["size"]
    if shared.config["font"]["path"] not in ("default", False):
        logger.debug("Applying path font")
        shared.FONT = pygame.Font(
            shared.config["font"]["path"], shared.config["font"]["size"]
        )
        shared.FONT_PATH = shared.config["font"]["path"]
        shared.FONT_WIDTH = shared.FONT.render("w", True, "white").get_width()
        shared.FONT_HEIGHT = shared.FONT.get_height()

    elif shared.config["font"]["family"]:
        logger.debug("Apply family font")
        shared.FONT = pygame.sysfont.SysFont(
            shared.config["font"]["family"], shared.config["font"]["size"]
        )
        shared.FONT_WIDTH = shared.FONT.render("w", True, "white").get_width()
        shared.FONT_HEIGHT = shared.FONT.get_height()

    offset_font_size(shared.config["font"]["size"] - shared.FONT_SIZE)
    apply_theme(shared.config["theme"]["name"])


if len(sys.argv) > 1 and sys.argv[1] == "--debug":
    apply_config()
