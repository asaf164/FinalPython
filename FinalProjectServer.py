"""
Author: Asaf Biran
Program Name - FinalProjectServer
Description: Central network hub. Accepts two client connections,
             assigns player IDs, and routes movement and item spawn data
             between clients to keep both screens in sync.
"""


import socket
import threading
import logging


logging.basicConfig(
    filename='game_server.log',
    filemode='w',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

HOST = '0.0.0.0'
PORT = 5555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    server.bind((HOST, PORT))
    logging.info(f"Server successfully bound to host {HOST} on port {PORT}.")
except socket.error as e:
    print(f"error:{e}")
    logging.critical(f"Socket binding error: {e}")
    exit()

server.listen(2)
print("server started waiting for two players...")
logging.info("Servers in listening state...")

clients = []

def handle_client(client_socket, client_index):
    opponent_index = 1 if client_index == 0 else 0
    logging.info(f"thread activated for player {client_index + 1}.")
    while True:
        try:
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                print(f"player {client_index + 1} disconnected.")
                logging.warning(f"Connection closed: Player {client_index + 1} disconnected.")
                break

            logging.info(f"Data received from Player {client_index + 1}: {data.strip()}")
            if len(clients) == 2:
                clients[opponent_index].send(data.encode('utf-8'))
                logging.info(f"Data successfully routed from Player {client_index + 1} to Player {opponent_index + 1}.")
        except:
            logging.error(f"Error for player {client_index + 1}.")
            break

    client_socket.close()
    logging.info(f"Socket connection closed safely for Player {client_index + 1}.")

while len(clients) < 2:
    client_socket, client_address = server.accept()
    print(f"player {len(clients) + 1} connected with address {client_address}")
    logging.info(f"Player {len(clients) + 1} connected from address {client_address}")

    player_id = str(len(clients) + 1)

    client_socket.send(f"{player_id}\n".encode('utf-8'))
    logging.info(f"Assigned and transmitted Player ID {player_id} to client.")

    clients.append(client_socket)

print("Both players connected. sending Start.")
logging.info("Matchmaking requirements fulfilled. Dispatching START broadcast to all clients.")

for c in clients:

    c.send("START\n".encode('utf-8'))

logging.info("Spawning threads for Player 1 and Player 2")
threading.Thread(target=handle_client, args=(clients[0], 0), daemon=True).start()
threading.Thread(target=handle_client, args=(clients[1], 1), daemon=True).start()

while True:
    pass