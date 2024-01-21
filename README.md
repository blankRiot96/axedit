<div align="center">
    <h1>Modal Editor</h1>
    A modal editor
</div>

## Keymaps

### Modal bindings

| Keys  | Action      |
| ----- | ----------- |
| `i`   | Insert mode |
| `v`   | Visual mode |
| `ESC` | Normal mode |

### Cursor bindings

 <!-- TODO: Continue this :) -->

| Keys | Action            |
| ---- | ----------------- |
| `h`  | Move cursor left  |
| `l`  | Move cursor right |
| `j`  | Move cursor down  |
| `k`  | Move cursor up    |

### Commands

Note: Writing to/Saving the file also invokes on-save hooks

| Command                         | Action                             |
| ------------------------------- | ---------------------------------- |
| `:`                             | Previous command                   |
| `:q[uit]`                       | Quit the editor                    |
| `:w[write]`                     | Write the file                     |
| `:wq` or `:x`                   | Write and quit the editor          |
| `:save[as] file-name`           | Save the file as                   |
| `:theme theme-name`             | Set the theme of the editor        |
| `:hooks`                        | Open the on-save hooks file        |
| `:line-numbers:relative on/off` | Set whether line no to be relative |
