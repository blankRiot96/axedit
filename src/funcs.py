from src import shared


def open_file(file: str) -> None:
    with open(file) as f:
        content = f.readlines()

    shared.file_name = file
    shared.chars = [list(line) for line in content]


def get_text():
    text = ""
    for row in shared.chars:
        text += "".join(row) + "\n"
    return text


def save_file():
    with open(shared.file_name, "w") as f:
        f.write(get_text())
