import json
import socket
import subprocess
import sys

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

            # Send the random number back to the client
            conn.sendall(response)
