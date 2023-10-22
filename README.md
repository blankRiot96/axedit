<div align="center">
    <h1>Modal Editor</h1>
    A modal editor
</div>

## Keymaps

### Normal Mode

- **Defaults:**

| Key | Action         |
| --- | -------------- |
| W   | Write mode     |
| S   | Select mode    |
| F   | Edit file name |

- **Movement binds**:

| Key       | Action                                |
| --------- | ------------------------------------- |
| Q         | Start of file                         |
| E         | End of file                           |
| M         | Set marker / Delete marker            |
| I         | Up                                    |
| K         | Down                                  |
| L         | Right                                 |
| J         | Left                                  |
| Shift + I | Above marker                          |
| Shift + K | Below marker                          |
| Shift + L | Next word                             |
| Shift + J | Previous word                         |
| X         | Delete and copy line                  |
| Y         | Copy line                             |
| )         | Go to next bracket                    |
| (         | Go to previous bracket                |
| G         | Switch between corresponding brackets |
| H         | Switch between corresponding quotes   |

- NOTE: Can combine any number before action to make it repeat _n_ times

### Select Mode

- All movement binds from NORMAL mode
- Selects text from cursor's position at start of SELECT mode to current cursor position

### Write Mode

- All insertions are added to the file
- Arrow keys -> movement in file
- ENTER -> create new line
- BACKSPACE -> delete character
