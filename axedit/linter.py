import json
import random
import socket
import subprocess
import sys
import threading

import pygame

from axedit import shared
from axedit.funcs import get_text
from axedit.input_queue import InputManager
from axedit.logs import logger
from axedit.state_enums import FileState

SERVER_HOST = "127.0.0.1"


class Linter:
    """
    Receives autocompletions from `axedit/linter_server.py`
    which is started as a separate process
    """

    def __init__(self) -> None:
        self.connected = False
        thread = threading.Thread(
            target=lambda: [self.spawn_server(), self.connect_to_server()], daemon=True
        )
        thread.start()
        self.lints: list[dict] = []
        self.first_time_connected = True
        self.create_font()

    def create_font(self):
        self.font = pygame.Font(
            shared.AXE_FOLDER_PATH / "assets/fonts/IntoneMonoNerdFontMono-Regular.ttf",
            shared.FONT_SIZE,
        )

    def spawn_server(self):
        lang_server_path = shared.AXE_FOLDER_PATH / "linter_server.py"
        while True:
            try:
                self.server_port = random.randint(1024, 65535)
                logger.debug(f"Linter PORT={self.server_port}")
                command = [
                    sys.executable,
                    str(lang_server_path.absolute()),
                    str(self.server_port),
                ]
                self.server_process = subprocess.Popen(
                    command,
                    stdin=subprocess.DEVNULL,
                    stdout=sys.stdout,
                    stderr=sys.stderr,
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
        return shared.chars_changed

    def receive_lints(self):
        text = get_text()
        data = {"file": shared.file_name, "text": text}
        data = json.dumps(data)
        l = len(data.encode())

        try:
            self.client_socket.sendall(f"{l};{data}".encode())
        except OSError:
            logger.critical("exit by linter?")
            exit()
        while True:
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
                logger.debug(e)
                continue

        self.lints: list[dict] = json.loads(received_data)

    def close_connections(self):
        if hasattr(self, "client_socket"):
            self.client_socket.close()
        if hasattr(self, "server_process"):
            self.server_process.kill()

    def filter_lints(self):
        locs = []
        for lint in self.lints[::-1]:
            row = lint["location"]["row"]
            if row in locs:
                self.lints.remove(lint)
                continue
            locs.append(row)

    def update(self):
        if not self.connected:
            return
        if self.first_time_connected:
            self.receive_lints()
            self.filter_lints()
        self.first_time_connected = False
        if not self.to_update():
            return

        self.receive_lints()
        self.filter_lints()

    def render_squigline(
        self,
        row: int,
        start_column: int,
        end_column: int,
        editor_surf: pygame.Surface,
        squiggly: pygame.Surface,
    ):
        squiggly_bum = (end_column - start_column) * shared.FONT_WIDTH
        x = 0
        squiggly_surf = pygame.Surface(
            (shared.srect.width, shared.FONT_HEIGHT), pygame.SRCALPHA
        )

        factor = 1 if shared.config["squiggly"]["type"] == "separated" else 0.6
        squiggly_diff = squiggly.get_width() * factor
        while x < squiggly_bum:
            squiggly_surf.blit(squiggly, (x, 0))
            x += squiggly_diff

        bound_rect = squiggly_surf.get_bounding_rect()
        if shared.config["squiggly"]["type"] == "cut-off":
            bound_rect.width = squiggly_bum
        squiggly_surf = squiggly_surf.subsurface(bound_rect).copy()

        squiggly_rect = pygame.Rect(
            (
                (start_column * shared.FONT_WIDTH) - shared.scroll.x,
                ((row + 0.5) * shared.FONT_HEIGHT) + shared.scroll.y,
            ),
            (squiggly_bum, shared.FONT_HEIGHT),
        )
        if shared.config["squiggly"]["type"] == "centered-free":
            squiggly_rect = squiggly_surf.get_rect(center=squiggly_rect.center)
        else:
            ...
            squiggly_rect.y += shared.FONT_HEIGHT * 0.5
        editor_surf.blit(squiggly_surf, squiggly_rect)

    def render_squiggly(
        self,
        start,
        end,
        editor_surf: pygame.Surface,
        squiggly: pygame.Surface,
    ) -> None:
        start = int(start["column"]) - 1, int(start["row"]) - 1
        end = int(end["column"]) - 1, int(end["row"]) - 1

        if end[1] > start[1]:
            for i in range(start[1], end[1]):
                self.render_squigline(i, 0, len(shared.chars[i]), editor_surf, squiggly)
            start = 0, end[1]

        self.render_squigline(end[1], start[0], end[0], editor_surf, squiggly)

    def render_lints(self, editor_surf: pygame.Surface):
        wavy_dash = "~"
        red_squiggly = self.font.render(wavy_dash, True, shared.theme["var"])
        orange_squiggly = self.font.render(wavy_dash, True, shared.theme["const"])
        for lint in self.lints:
            y = lint["location"]["row"] - 1
            x = len(shared.chars[y]) + 2
            x, y = x * shared.FONT_WIDTH, y * shared.FONT_HEIGHT

            # Scrolllll
            x -= shared.scroll.x
            y += shared.scroll.y

            # Don't render lints that can't be seen!
            if y < 0 or y > shared.srect.height:
                continue

            msg = f"󰨓 {lint['message']}"
            red, orange = shared.theme["var"], shared.theme["const"]
            color = red if lint["code"][0] == "E" else orange
            squiggly = red_squiggly if lint["code"][0] == "E" else orange_squiggly

            self.render_squiggly(
                lint["location"], lint["end_location"], editor_surf, squiggly
            )
            surf = shared.FONT.render(msg, True, color)
            editor_surf.blit(surf, (x, y))

    def draw(self, editor_surf: pygame.Surface):
        self.render_lints(editor_surf)
