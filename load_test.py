import socket
import threading
import random
import time

HOST = "127.0.0.1"
PORT = 5000

NUM_PLAYERS = 100


def simulate_player(player_id):
    username = f"player{player_id}"

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    while True:
        lap_time = random.randint(70, 120)

        message = f"{username}#{lap_time}"
        client.send(message.encode())

        time.sleep(random.uniform(0.5, 2))


threads = []

for i in range(NUM_PLAYERS):
    t = threading.Thread(target=simulate_player, args=(i,))
    t.start()
    threads.append(t)

for t in threads:
    t.join()