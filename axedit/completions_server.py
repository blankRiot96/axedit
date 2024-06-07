import json
import socket
import sys

import jedi

# Server configuration
HOST = "127.0.0.1"  # Loopback address
PORT = int(sys.argv[1])

# Create a socket object
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    # Bind the socket to the address and port
    while True:
        try:
            server_socket.bind((HOST, PORT))
            break
        except OSError:
            continue

    # Listen for incoming connections
    server_socket.listen()

    # Accept connections from clients
    conn, addr = server_socket.accept()

    with conn:
        while True:
            # Receive data from the client
            data = conn.recv(1024)
            if not data:
                break

            # Process received data (in this example, we simply decode it and send back a response)
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

            # Generate a random number as response
            received_data = json.loads(received_data)
            script = jedi.Script(received_data["text"])

            x, y = received_data["loc"]
            try:
                completions = script.complete(y, x)
            except ValueError as e:
                raise ValueError(e)
            completions = [
                {
                    "name": comp.name,
                    "prefix-len": comp.get_completion_prefix_length(),
                    "type": comp.type,
                }
                for comp in completions
            ]
            response = json.dumps(completions).encode()
            response = f"{len(response)};{response.decode()}".encode()

            # Send the random number back to the client
            conn.sendall(response)
