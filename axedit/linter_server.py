import json
import socket
import subprocess
import sys

HOST = "127.0.0.1"
PORT = int(sys.argv[1])


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

            command_str = f"ruff check --output-format=json --stdin-filename={received_data['file']}"
            command = command_str.split()

            try:
                linting_info = subprocess.check_output(
                    command, input=received_data["text"].encode()
                )
            except subprocess.CalledProcessError as e:
                linting_info = e.output

            response_data = json.loads(linting_info)
            response = json.dumps(response_data).encode()
            response = f"{len(response)};{response.decode()}".encode()

            conn.sendall(response)
