import json
import socket
import sys

import jedi
from rapidfuzz import fuzz

HOST = "127.0.0.1"
PORT = int(sys.argv[1])


def get_fuzzy_matched_indeces(name: str, item: str) -> list[int]:
    res = []
    name, item = name.lower(), item.lower()
    for c1 in name:
        for i, c2 in enumerate(item):
            if i in res:
                continue
            if len(res) == len(name):
                return res
            if c1 == c2:
                res.append(i)

    return res


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    while True:
        try:
            server_socket.bind((HOST, PORT))
            break
        except OSError:
            continue

    server_socket.listen()

    conn, addr = server_socket.accept()

    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                break

            received_data = data.decode()
            size, received_data = received_data.split(";", 1)

            size = int(size)
            size -= len(data) - len(str(size)) - 1
            while size > 0:
                data = conn.recv(1024)
                size -= 1024

                received_data += data.decode()

            if received_data.lower() == "exit":
                break

            received_data = json.loads(received_data)
            script = jedi.Script(received_data["text"])

            x, y = received_data["loc"]
            try:
                completions = script.complete(y, x)
            except ValueError as e:
                raise ValueError(e)

            if received_data["fuzzy"]:
                prefix_name = received_data["prefix_name"]
                completions.sort(
                    key=lambda comp: fuzz.ratio(prefix_name, comp.name), reverse=True
                )
                completions = [
                    {
                        "name": comp.name,
                        "matched_indeces": get_fuzzy_matched_indeces(
                            prefix_name, comp.name
                        ),
                        "type": comp.type,
                    }
                    for comp in completions
                ]
            else:
                completions = [
                    {
                        "name": comp.name,
                        "matched_indeces": list(
                            range(comp.get_completion_prefix_length())
                        ),
                        "type": comp.type,
                    }
                    for comp in completions
                ]
            response = json.dumps(completions).encode()
            response = f"{len(response)};{response.decode()}".encode()

            conn.sendall(response)
