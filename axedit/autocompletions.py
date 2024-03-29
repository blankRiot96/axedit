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

SERVER_HOST = "127.0.0.1"  # Loopback address


class AutoCompletions:
    """
    Receives autocompletions from `axedit/completions_server.py`
    which is started as a separate process
    """

    def __init__(self) -> None:
        self.connected = False
        thread = threading.Thread(
            target=lambda: [self.spawn_server(), self.connect_to_server()], daemon=True
        )
        thread.start()

    def spawn_server(self):
        lang_server_path = shared.AXE_FOLDER_PATH / "completions_server.py"
        while True:
            try:
                self.server_port = random.randint(1024, 65535)
                logger.debug(f"AutoCompletion PORT={self.server_port}")
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

    def receive_completions(self):
        text = get_text()
        loc = (shared.cursor_pos.x, shared.cursor_pos.y + 1)

        data = {"text": text, "loc": loc}
        data = json.dumps(data)
        l = len(data.encode())

        try:
            self.client_socket.sendall(f"{l};{data}".encode())
        except OSError:
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

        received_data = json.loads(received_data)
        # if received_data:
        #     logger.debug(f"autocompletion={received_data[0]["name"]}")

    def close_connections(self):
        if hasattr(self, "client_socket"):
            self.client_socket.close()
        if hasattr(self, "server_process"):
            self.server_process.kill()

    def update(self):
        if not self.connected:
            return
        if not self.to_update():
            return

        self.receive_completions()

    def draw(self, editor_surf: pygame.Surface):
        pass
