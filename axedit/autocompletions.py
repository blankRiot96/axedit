import json
import random
import socket
import subprocess
import sys
import time

import pygame

from axedit import shared
from axedit.funcs import get_text
from axedit.input_queue import InputManager
from axedit.logs import logger
from axedit.state_enums import FileState

_POSSIBLE_COMPLETIONS = {}

SERVER_HOST = "127.0.0.1"  # Loopback address
SERVER_PORT = random.randint(1024, 65535)  # Port server is listening on


class AutoCompletions:
    """
    Receives autocompletions from `axedit/lang_server.py`
    which is started as a separate process
    """

    def __init__(self) -> None:
        # Start the server
        lang_server_path = shared.AXE_FOLDER_PATH / "lang_server.py"
        command = [sys.executable, str(lang_server_path.absolute()), str(SERVER_PORT)]
        shared.server_process = subprocess.Popen(
            command,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True,
        )

        # Give some time for the server to start *** Very important ***
        time.sleep(0.1)

        # Start the client
        shared.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        shared.client_socket.connect((SERVER_HOST, SERVER_PORT))

    def update(self):
        text = get_text()
        loc = (shared.cursor_pos.x + 1, shared.cursor_pos.y + 1)

        data = {"text": text, "loc": loc}
        data = json.dumps(data)

        try:
            shared.client_socket.sendall(data.encode())
        except OSError:
            exit()

        response = shared.client_socket.recv(1024).decode()
        logger.debug(f"Received from server: {response}")

    def draw(self, editor_surf: pygame.Surface):
        pass
