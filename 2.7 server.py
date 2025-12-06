"""
Author - Asaf Biran
Date - 1/11/25
Program name - 2.7 Server
"""

import socket
import os
import logging
import glob
import shutil
import subprocess
import pyscreeze
import cilent_server_protocol

MAX_PACKET = 1024
QUEUE_LEN = 1
MODE = None

# logging setup
def createlogs():
    os.makedirs("logsserver", exist_ok=True)
    logging.basicConfig(filename='logsserver/program.log', filemode='w', level=logging.INFO)
    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


"""
EXIT command
disconnect client and wait for a new connection
"""
def fexit(client_socket, my_socket):
    logging.info("Exit command received")
    client_socket.sendall("disconnecting from the serverEOM".encode())
    logging.info("Client disconnected")
    client_socket, client_address = my_socket.accept()
    my_socket.listen(QUEUE_LEN)
    logging.info("New client connected after EXIT")
    return client_socket


"""
DIR command
return list of files in the given directory path using glob
"""
def fdir(client_socket, data):
    try:
        logging.info(f"DIR command received. Path: {data[1]}")
        path = data[1] + "/*.*"
        files = glob.glob(path)
        buf = ""
        for f in files:
            buf = buf + str(f) + "\n"
        if buf == "":
            client_socket.sendall("path either doesnt exist or empty file".encode())
            logging.info("DIR: path doesn't exist or empty")
        buf = buf + "EOM"
        client_socket.sendall(buf.encode())
        logging.info("DIR command completed successfully")
    except Exception as e:
        logging.error(f"DIR command failed: {e}")
        print(" failed:", e)


"""
DELETE command
delete the specified file using os.remove
"""
def fdelete(client_socket, data):
    try:
        logging.info(f"DELETE command received. File: {data[1]}")
        os.remove(data[1])
        client_socket.sendall("file deletedEOM".encode())
        logging.info("File deleted successfully")
    except Exception as e:
        logging.error(f"DELETE failed: {e}")
        print(" failed:", e)


"""
COPY command
copy a file from source to destination using shutil.copy
"""
def fcopy(client_socket, data):
    try:
        logging.info(f"COPY command received. Source: {data[1]} Destination: {data[2]}")
        shutil.copy(data[1], data[2])
        client_socket.sendall("file copied successfullyEOM".encode())
        logging.info("File copied successfully")
    except Exception as e:
        logging.error(f"COPY failed: {e}")
        print("Copy failed:", e)
        client_socket.sendall("copy failedEOM".encode())


"""
EXECUTE command
run the given system command using subprocess.call
"""
def fexecute(client_socket, data):
    try:
        logging.info(f"EXECUTE command received. Command: {data[1]}")
        subprocess.call(data[1])
        client_socket.sendall("executedEOM".encode())
        logging.info("Command executed successfully")
    except FileNotFoundError:
        logging.error(f"EXECUTE failed: Command not found: {data[1]}")
        print("Command not found:", data[1])
        client_socket.sendall("Execution failedEOM".encode())
    except PermissionError:
        logging.error(f"EXECUTE failed: Permission denied: {data[1]}")
        print("Permission denied:", data[1])
        client_socket.sendall("Execution failedEOM".encode())
    except Exception as e:
        logging.error(f"EXECUTE failed: {e}")
        print("Execution failed:", e)
        client_socket.sendall("Execution failedEOM".encode())

"""
TAKE_SCREENSHOT command
capture screen and send image to client using pyscreeze.screenshot
sends to screenshot's bytes in chunks and waits for b"EOM"
"""
def fscreenshot(client_socket):
    try:
        logging.info("TAKE_SCREENSHOT command received")
        folder = r"C:/cyber/server_ss"
        os.makedirs(folder, exist_ok=True)
        ss_full_path = os.path.join(folder, "screen.jpg")

        image = pyscreeze.screenshot(ss_full_path)
        logging.info(f"Screenshot saved to {ss_full_path}")

        with open(ss_full_path, "rb") as f:
            chunk = f.read(MAX_PACKET)
            while chunk:
                client_socket.sendall(chunk)
                chunk = f.read(MAX_PACKET)
        logging.info("Screenshot sent to client")

        client_socket.sendall(b"EOM")
    except Exception as e:
        logging.error(f"Screenshot failed: {e}")
        print("Failed to send photo:", e)

#main server loop
def main():
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    logging.info("Socket created")
    my_socket.bind(('0.0.0.0', 8080))
    logging.info("Socket binded")
    my_socket.listen(QUEUE_LEN)
    logging.info("Socket listening")

    client_socket, client_address = my_socket.accept()
    logging.info("Client connected")

    while True:
        try:
            request = client_socket.recv(MAX_PACKET).decode().strip()
            logging.info(f"Received request: {request}")
            data_from_client = request.split()
            data_from_client_count = len(data_from_client)

            if request == 'EXIT':
                client_socket = fexit(client_socket, my_socket)

            elif data_from_client[0] == 'DIR':
                fdir(client_socket, data_from_client)

            elif data_from_client[0] == 'DELETE':
                fdelete(client_socket, data_from_client)

            elif data_from_client[0] == 'COPY':
                fcopy(client_socket, data_from_client)

            elif data_from_client[0] == 'EXECUTE':
                fexecute(client_socket, data_from_client)

            elif data_from_client[0] == 'TAKE_SCREENSHOT':
                fscreenshot(client_socket)

            else:
                logging.warning(f"Unknown action: {request}")
                client_socket.sendall("Unknown actionEOM".encode())

        except socket.error as err:
            logging.error(f"Socket error: {err}")
            print(err)


if __name__ == '__main__':
    createlogs()
    main()
