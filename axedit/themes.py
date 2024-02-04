from pathlib import Path

import yaml

from axedit import shared


def get_available_theme_names() -> list[str]:
    return [path.stem for path in shared.THEMES_PATH.iterdir()]


def _get_readable_theme(theme: dict) -> dict:
    colors = iter(
        (
            "default-bg",
            "light-bg",
            "select-bg",
            "comment",
            "dark-fg",
            "default-fg",
            "light-fg",
            "light-fg",
            "var",
            "const",
            "class",
            "string",
            "match",
            "func",
            "keyword",
            "dep",
        )
    )
    return {next(colors): f"#{color}" for color in theme.values()}


def apply_theme(theme_name: str) -> None:
    shared.theme_changed = True
    theme_path = shared.THEMES_PATH / f"{theme_name}.yaml"
    with open(theme_path) as f:
        shared.theme = _get_readable_theme(yaml.safe_load(f))
