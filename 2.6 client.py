"""
Program that communicates with the servers, sends it input
and prints the responses.

Author - Asaf Biran
Date - 1/11/25
Program name - 2.6 Client
"""

import socket
import os
import logging

MAX_PACKET = 1024

#logging setup
def createlogs():
    os.makedirs("logsuser", exist_ok=True)
    logging.basicConfig(filename='logsuser/program.log', filemode='w', level=logging.INFO)
    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


def main():
    Action = None
    while (Action!="EXIT"):

        my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            Action = input("enter action: ").upper()
            logging.info("recieved action")
            my_socket.connect(('127.0.0.1', 8080))
            logging.info("connected to server")
            my_socket.send(Action.encode())
            logging.info("sent action")
            response = my_socket.recv(MAX_PACKET).decode()
            logging.info("recieved response")
            print(response)

        except socket.error as err:
            print('received socket error' + str(err))
            logging.error("socket error")

        finally:
            my_socket.close()
            logging.info("closing socket")


if __name__ == '__main__':
    createlogs()
    main()