import socket
import threading
from redis_db import update_score, get_leaderboard

HOST = "127.0.0.1"
PORT = 5000

clients = []
clients_lock = threading.Lock()


def broadcast(message):
    with clients_lock:
        clients_copy = clients.copy()  # snapshot

    dead_clients = []

    for client in clients_copy:
        try:
            client.send(message.encode())
        except:
            dead_clients.append(client)

    # clean up dead clients safely
    if dead_clients:
        with clients_lock:
            for dc in dead_clients:
                if dc in clients:
                    clients.remove(dc)


def handle_client(client_socket, addr):
    print(f"Client connected: {addr}")

    try:
        while True:
            data = client_socket.recv(1024).decode()

            if not data:
                break

            # format: username#score
            try:
                username, score = data.split("#")
                score = float(score)
            except ValueError:
                continue  # ignore malformed input

            update_score(username, score)
            leaderboard = get_leaderboard()

            message = "LEADERBOARD\n" + leaderboard
            broadcast(message)

    except Exception as e:
        print(f"Error with {addr}: {e}")

    finally:
        print(f"Client disconnected: {addr}")

        with clients_lock:
            if client_socket in clients:
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

        with clients_lock:
            clients.append(client_socket)

        thread = threading.Thread(
            target=handle_client,
            args=(client_socket, addr),
            daemon=True   # avoids zombie threads on exit
        )
        thread.start()


if __name__ == "__main__":
    start_server()