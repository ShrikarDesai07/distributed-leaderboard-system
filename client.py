import socket
import threading
import os

HOST = "127.0.0.1"
PORT = 5000


def receive_messages(sock):
    while True:
        try:
            msg = sock.recv(4096).decode()

            # clear terminal
            os.system('cls' if os.name == 'nt' else 'clear')

            print("🏁 LIVE LEADERBOARD\n")
            print(msg)
        except:
            break

def start_client():
    username = input("Enter username: ")

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    thread = threading.Thread(target=receive_messages, args=(client,))
    thread.start()

    while True:
        lap_time = input("Enter lap time: ")

        message = f"{username}#{lap_time}"

        client.send(message.encode())


if __name__ == "__main__":
    start_client()