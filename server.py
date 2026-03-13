import socket
import threading
from redis_db import update_score, get_leaderboard

HOST = "127.0.0.1"
PORT = 5000

clients = []


def broadcast(message):
    for client in clients:
        try:
            client.send(message.encode())
        except:
            clients.remove(client)


def handle_client(client_socket, addr):
    print(f"Client connected: {addr}")

    while True:
        try:
            data = client_socket.recv(1024).decode()

            if not data:
                break

            # format: username#score
            username, score = data.split("#")
            score = float(score)

            update_score(username, score)

            leaderboard = get_leaderboard()

            message = "LEADERBOARD\n" + leaderboard

            broadcast(message)

        except:
            break

    print(f"Client disconnected: {addr}")
    clients.remove(client_socket)
    client_socket.close()


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print("Server started...")
    print(f"Listening on {HOST}:{PORT}")

    while True:
        client_socket, addr = server.accept()
        clients.append(client_socket)

        thread = threading.Thread(
            target=handle_client,
            args=(client_socket, addr)
        )

        thread.start()


if __name__ == "__main__":
    start_server()