from src import shared


def get_text():
    text = ""
    for row in shared.chars:
        text += "".join(row) + "\n"
    return text


def save_file():
    with open(shared.file_name, "w") as f:
        f.write(get_text())
