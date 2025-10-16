<div align="center">
    <img src="https://github.com/blankRiot96/axedit/assets/77634274/d087fa6e-7225-45f9-b100-53df78a3000f" width=700><br>
    <a href=""><img src="https://img.shields.io/badge/License-MIT-green"></a>
    <a href=""><img src="https://img.shields.io/badge/Style-Black-black"></a>
    <a href=""><img src="https://img.shields.io/badge/Python-3.12-blue"></a>
    <a href=""><img src="https://img.shields.io/badge/Platforms-Windows, Mac, Linux-1E1E2E"></a>
    <a href=""><img src="https://img.shields.io/badge/Contributors-Welcome-A6E3A1"></a><br>
    <img src="https://github.com/blankRiot96/axedit/assets/77634274/b3e62314-2eb1-4ef9-860f-cfb640cd2b0c"><br>
</div>

## About

Axedit is a light, fast and aesthetic modal editor for Python. Attempts to implement vim-like motions.

## Installation

```
pip install axedit
```

You can also install it with `pipx` or `uv`:
```
pipx install axedit
```
or
```
uv tool install axedit
```


## Usage

Run `axedit` in your project folder

## Features

### Provisions

- Linting offered with `ruff`. Tracks your `pyproject.toml` or `ruff.toml` for ruff specific configuration
- Autocompletions with `jedi`
- Syntax highlighting self implemented (for now)
- 20+ Themes available - Gruvbox, Catppuccin, One Dark, Rosepine etc.
- Font, Opacity, On Save hooks, Manner of squiggly lines and Theme are configurable. See [config.toml](https://github.com/blankRiot96/axedit/blob/main/axedit/assets/data/default_config/config.toml)
- Detects your Python environment based on the shell you launch `axedit` from and uses it accordingly for autocomplete

### Modal Bindings

| Keys  | Action      |
| ----- | ----------- |
| `i`   | Insert mode |
| `v`   | Visual mode |
| `ESC` | Normal mode |

### Cursor Motions

| Keys | Action                     |
| ---- | -------------------------- |
| `h`  | Move cursor left           |
| `l`  | Move cursor right          |
| `j`  | Move cursor down           |
| `k`  | Move cursor up             |
| `w`  | Move to the next word      |
| `{`  | Move to previous paragraph |
| `}`  | Move to next paragraph     |
| `0`  | Move to start of the line  |
| `$`  | Move to end of the line    |

### Editor Commands

| Command               | Action                                   |
| --------------------- | ---------------------------------------- |
| `:q[uit]`             | Quit the editor                          |
| `:w[rite]`            | Write the file                           |
| `:wq` or `:x`         | Write and quit the editor                |
| `:save[as] file-name` | Save the file as                         |
| `:rn` or `:rename`    | Rename the file                          |
| `:theme theme-name`   | Set the theme of the editor              |
| `:config`             | Open the config file                     |
| `:reset-config`       | Reset the editor's config to its default |
| `:reload-config`      | Apply the config                         |
| `:rel-no on/off`      | Set whether line no to be relative       |

## Credits

- [Matt](https://github.com/Matiiss) - For VCing with me and frankly solving major issues which would have delayed the release by months otherwise
- [Dylan](https://github.com/Dylan-DPC) - For always giving me direction on what to do
- Tim - For suggesting the idea of a modal text editor
- [Suyashtnt](https://github.com/Suyashtnt/) - For providing the [kleur](https://github.com/Suyashtnt/kleur) theme
