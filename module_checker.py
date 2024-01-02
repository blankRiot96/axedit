"""
Problem: We need to figure out if something imported is a submodule or not
Solution: Try to see local and site-packages directories?
"""

import sys
from pathlib import Path


def _is_submodule(mod_path: Path, sub_module_name: str) -> bool:
    if not mod_path.exists():
        return False

    modules = []

    for file in mod_path.iterdir():
        if file.name.endswith(".pyi") or file.name.endswith(".py"):
            modules.append(file.stem)

        if file.is_dir() and (file / "__init__.py").exists():
            modules.append(file.stem)

    return sub_module_name in modules


def _is_local_module(main_module_name: str, sub_module_name: str) -> bool:
    dots = "."
    if main_module_name.startswith("."):
        *dots, main_module_name = main_module_name.split(".")
        dots = len(dots) * "."

    current_path = Path(dots)
    mod_path = current_path / main_module_name

    return _is_submodule(mod_path, sub_module_name)


def _is_site_package_module(main_module_name: str, sub_module_name: str) -> bool:
    scripts_path = Path(sys.executable).parent / "Lib/site-packages/"
    mod_path = scripts_path / main_module_name

    return _is_submodule(mod_path, sub_module_name)


def is_editable_module(main_module_name: str, sub_module_name: str) -> bool:
    scripts_path = Path(sys.executable).parent / "Lib/site-packages/"
    easy_install = scripts_path / "easy-install.pth"
    


def is_module(main_module_name: str, sub_module_name: str) -> bool:
    if _is_local_module(main_module_name, sub_module_name):
        return True

    if _is_site_package_module(main_module_name, sub_module_name):
        return True

    return False
