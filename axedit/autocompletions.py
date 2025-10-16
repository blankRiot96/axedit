import json
import random
import socket
import subprocess
import sys
import threading
import time
from dataclasses import dataclass

import pygame
import typing_extensions as t

from axedit import shared
from axedit.funcs import get_text
from axedit.logs import logger
from axedit.state_enums import FileState
from axedit.utils import Time, highlight_text

SERVER_HOST = "127.0.0.1"  # Loopback address

_POSSIBLE_COMPLETIONS = {
    "module": ("󰅩", "class"),
    "class": ("", "class"),
    "param": ("󰭅", "var"),
    "function": ("", "func"),
    "statement": ("", "string"),
    "keyword": ("", "keyword"),
    "instance": ("", "const"),
}


@dataclass
class Symbol:
    icon: str
    color: str

    @classmethod
    def get_from_comp_type(cls, comp_type: str) -> t.Self:
        icon, key = _POSSIBLE_COMPLETIONS.get(comp_type, ("", "default-fg"))
        return Symbol(icon=icon, color=shared.theme[key])


class AutoCompletions:
    """
    Receives autocompletions from `axedit/completions_server.py`
    which is started as a separate process
    """

    def __init__(self) -> None:
        self.connected = False
        self.selected_index = 0
        thread = threading.Thread(
            target=lambda: [
                self.spawn_server(),
                self.connect_to_server(),
                self.threaded_completions_receiver(),
            ],
            daemon=True,
        )
        thread.start()
        self.completions: list[dict] = []
        self.gen_blank()
        self.receiving = False
        self.post_receive_clarity = False
        self.entered_editor = False

    def gen_blank(self):
        try:
            width = (
                max(len(comp["name"]) for comp in self.completions) + 3
            ) * shared.FONT_WIDTH
            height = len(self.completions) * shared.FONT_HEIGHT
        except ValueError:
            width, height = 0, 0

        self.surf = pygame.Surface((width, height))
        self.surf.fill(shared.theme["light-bg"])

    def spawn_server(self):
        lang_server_path = shared.AXE_FOLDER_PATH / "completions_server.py"
        while True:
            try:
                self.server_port = random.randint(1024, 65535)
                logger.info(f"AutoCompletion PORT={self.server_port}")
                command = [
                    sys.executable,
                    str(lang_server_path.absolute()),
                    str(self.server_port),
                ]
                self.server_process = subprocess.Popen(
                    command,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    close_fds=True,
                )
                self.server_process.wait(1.0)
            except subprocess.TimeoutExpired:
                break

    def connect_to_server(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                self.client_socket.connect((SERVER_HOST, self.server_port))
                self.connected = True
                break
            except socket.error:
                continue

    def to_update(self) -> bool:
        if self.entered_editor:
            self.post_receive_clarity = True

        changed_state = (
            shared.chars_changed or shared.cursor_x_changed or shared.cursor_y_changed
        )
        gatekeepers = bool(
            shared.mode == FileState.INSERT
            and "".join(shared.chars[shared.cursor_pos.y]).strip()
            and shared.cursor_pos.x > 0
        )

        if changed_state:
            if self.receiving:
                self.post_receive_clarity = True
            self.completions.clear()

        return changed_state and gatekeepers

    def receive_completions(self):
        text = get_text()
        loc = (shared.cursor_pos.x, shared.cursor_pos.y + 1)

        data_to_send = {"text": text, "loc": loc, "fuzzy": False}
        data_to_send = json.dumps(data_to_send)
        l = len(data_to_send.encode())

        try:
            self.client_socket.sendall(f"{l};{data_to_send}".encode())
        except OSError:
            exit()
        while True:
            self.receiving = True
            try:
                data = self.client_socket.recv(1024)

                if not data:
                    continue

                received_data = data.decode()
                size, received_data = received_data.split(";", 1)

                size = int(size)
                size -= len(data) - len(str(size)) - 1
                while size > 0:
                    data = self.client_socket.recv(1024)
                    size -= 1024

                    received_data += data.decode()

                # ***
                break
            except socket.error as e:
                logger.info(f"{data_to_send = }")
                logger.error(e)
                continue

                # exit()

        if self.post_receive_clarity:
            self.post_receive_clarity = False
            self.selected_index = 0
            self.receive_completions()
            return

        self.receiving = False
        self.completions = json.loads(received_data)
        self.filter_completions()
        self.selected_index = 0

    def close_connections(self):
        if hasattr(self, "client_socket"):
            self.client_socket.close()
        if hasattr(self, "server_process"):
            self.server_process.kill()

    def on_enter(self):
        if not shared.kp[pygame.K_RETURN]:
            return

        diff = shared.cursor_pos.x - self.get_selected_prefix_len()
        shared.chars[shared.cursor_pos.y][diff:] = (
            list(self.get_selected_name())
            + shared.chars[shared.cursor_pos.y][shared.cursor_pos.x :]
        )
        shared.cursor_pos.x += (
            len(self.get_selected_name()) - self.get_selected_prefix_len()
        )

    def filter_completions(self):
        # TODO: PREFIX-LEN AND STUFF
        if (
            self.completions
            and len(self.completions[self.selected_index]["name"])
            == self.completions[self.selected_index]["prefix-len"]
        ):
            self.completions.clear()
            return

        for comp in self.completions[:]:
            try:
                char = shared.chars[shared.cursor_pos.y][shared.cursor_pos.x - 1]
            except IndexError:
                continue
            if comp["prefix-len"] == 0 and char != ".":
                self.completions.remove(comp)

    def threaded_completions_receiver(self) -> None:
        while True:
            to_upd = self.to_update()
            if not self.connected or not self.entered_editor or not to_upd:
                time.sleep(0)
                continue

            self.receive_completions()

    def shuffle_suggestions(self):
        if shared.kp[pygame.K_DOWN]:
            self.selected_index += 1
        elif shared.kp[pygame.K_UP]:
            self.selected_index -= 1
        else:
            return

        if self.selected_index >= len(self.completions):
            self.selected_index = 0
        if self.selected_index < 0:
            self.selected_index = len(self.completions) - 1

    def update(self):
        shared.autocompleting = bool(self.completions)
        self.entered_editor = True
        if shared.mode != FileState.INSERT:
            self.completions = []
            return
        if not self.connected:
            return

        self.shuffle_suggestions()
        self.on_enter()

    def draw_suggestions(self) -> None:
        for index, comp in enumerate(self.completions):
            symbol: Symbol = Symbol.get_from_comp_type(comp["type"])
            symbol_surf = shared.FONT.render(symbol.icon, True, symbol.color)

            if index == self.selected_index:
                pygame.draw.rect(
                    self.surf,
                    shared.theme["select-bg"],
                    (
                        0,
                        index * shared.FONT_HEIGHT,
                        self.surf.get_width(),
                        shared.FONT_HEIGHT,
                    ),
                )
            comp_surf = highlight_text(
                shared.FONT,
                comp["name"],
                True,
                shared.theme["default-fg"],
                list(range(comp["prefix-len"])),
                shared.theme["keyword"],
            )

            self.surf.blit(
                symbol_surf, (shared.FONT_WIDTH / 2, index * shared.FONT_HEIGHT)
            )
            self.surf.blit(
                comp_surf, (symbol_surf.get_width() * 2, index * shared.FONT_HEIGHT)
            )

    def get_selected_name(self) -> str:
        if self.completions:
            return self.completions[self.selected_index]["name"]
        return ""

    def get_selected_prefix_len(self) -> int:
        if self.completions:
            return self.completions[self.selected_index]["prefix-len"]
        return 0

    def draw(self, editor_surf: pygame.Surface):
        self.gen_blank()
        self.draw_suggestions()

        x = shared.cursor_pos.x * shared.FONT_WIDTH
        y = ((shared.cursor_pos.y + 1) * shared.FONT_HEIGHT) + shared.scroll.y
        editor_surf.blit(self.surf, (x, y))
