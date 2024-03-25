import random
import socket
import sys

# Server configuration
HOST = "127.0.0.1"  # Loopback address
PORT = int(sys.argv[1])

# Create a socket object
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    # Bind the socket to the address and port
    server_socket.bind((HOST, PORT))

    # Listen for incoming connections
    server_socket.listen()

    print(f"Server is listening on {HOST}:{PORT}")

    # Accept connections from clients
    conn, addr = server_socket.accept()

    with conn:
        print("Connected by", addr)
        while True:
            # Receive data from the client
            data = conn.recv(1024)
            if not data:
                break

            # Process received data (in this example, we simply decode it and send back a response)
            received_data = data.decode()
            print("Received:")

            if received_data.lower() == "exit":
                break

            # Generate a random number as response
            random_number = random.randint(1, 100)
            response = str(random_number)

            # Send the random number back to the client
            conn.sendall(response.encode())
