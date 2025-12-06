"""
Author - Asaf Biran
Date - 1/11/25
Program name - 2.7 Client
"""

import socket
import logging
import os
import cilent_server_protocol

from mouseinfo import screenshot

#logging setup
def createlogs():
    os.makedirs("logsuser", exist_ok=True)
    logging.basicConfig(filename='logsuser/program.log', filemode='w', level=logging.INFO)
    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


def main():
    cmd = None
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.connect(('127.0.0.1', 8080))
    logging.info("connected to server")

    while cmd != "EXIT":
        Action = input("enter action: ")
        data_from_user = Action.split()
        data_from_user_count = len(data_from_user)
        if data_from_user_count == 0:
            print ("No Action from user")
            continue
        else:
            cmd = data_from_user[0].upper()
            if cmd == "DIR":
                assert data_from_user_count == 2
                path = data_from_user[1]
                cilent_server_protocol.dir(my_socket, path)
            elif cmd == "COPY":
                assert data_from_user_count == 3
                src_path = data_from_user[1]
                dst_path = data_from_user[2]
                cilent_server_protocol.copy(my_socket, src_path, dst_path)
            elif cmd == "EXECUTE":
                assert data_from_user_count == 2
                path = data_from_user[1]
                cilent_server_protocol.execute(my_socket, path)
            elif cmd == "DELETE":
                assert data_from_user_count == 2
                path = data_from_user[1]
                cilent_server_protocol.delete(my_socket, path)
            elif cmd == "TAKE_SCREENSHOT":
                assert data_from_user_count == 1
                cilent_server_protocol.screenshot(my_socket)
            elif cmd == "EXIT":
                assert data_from_user_count == 1
                cilent_server_protocol.exit(my_socket)
            else:
                print(Action + " is not a valid action")

    my_socket.close()
    logging.info("closing socket")
    print("Client Exit...")

if __name__ == '__main__':
    createlogs()
    main()