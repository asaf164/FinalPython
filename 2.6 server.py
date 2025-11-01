"""
Server program that listens for incoming connections and responds to commands such as:
'TIME' - sends the current time.
'NAME' - sends the server's name.
'RAND' - sends a random number between 1 and 10.
'EXIT' - disconnection request.
*anything else will return 'Illegal action'.

Author - Asaf Biran
Date - 1/11/25
Program name - 2.6 Server
"""

import socket
import random
import datetime
import os
import logging


MAX_PACKET = 1024
QUEUE_LEN = 1
MODE = None

#logging setup
def createlogs():
    os.makedirs("logsserver", exist_ok=True)
    logging.basicConfig(filename='logsserver/program.log', filemode='w', level=logging.INFO)
    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

#random setup
def rand():
    rnd = random.randint(1, 10)
    return rnd


def main():
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    logging.info("Socket created")
    my_socket.bind(('0.0.0.0', 8080))
    logging.info("Socket binded")
    my_socket.listen(QUEUE_LEN)
    logging.info("Socket listening")

    while True:
        try:
            client_socket, client_address = my_socket.accept()
            logging.info("Client connected")

            try:
                request = client_socket.recv(MAX_PACKET).decode().strip()
                logging.info("Received request: {}".format(request))

                if request == 'EXIT':
                    client_socket.sendall("disconnecting from the server".encode())
                    logging.info("Client disconnected")

                elif request == 'NAME':
                    client_socket.sendall("TIGRIS".encode())
                    logging.info("Client disconnected")

                elif request == 'TIME':
                    now = datetime.datetime.now()
                    logging.info("Current time: {}".format(now))
                    text = str(now)
                    logging.info("Current time: {}".format(text))
                    client_socket.sendall(text.encode())
                    logging.info("Client disconnected")

                elif request == 'RAND':
                    rnd = rand()
                    logging.info("Random number generated: {}".format(rnd))
                    text = str(rnd)
                    logging.info("Random number generated: {}".format(text))
                    client_socket.sendall(text.encode())
                    logging.info("Client disconnected")

                else:
                    client_socket.sendall("Unknown action ".encode())
                    logging.info("Client disconnected")

            except socket.error as err:
                print(err)
                logging.info("Client disconnected")

            finally:
                client_socket.close()
                logging.info("Client disconnected")

        except socket.error as err:
            print(err)
            logging.info("Client disconnected")


if __name__ == '__main__':
    assert rand()<11 and rand()>0
    createlogs()
    main()