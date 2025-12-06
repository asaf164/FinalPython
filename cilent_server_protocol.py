import socket
import logging
import os

MAX_PACKET = 1024

def _private_send_command_to_server(my_socket, command):
    try:
        my_socket.send(command.encode())
        while True:
            response = my_socket.recv(MAX_PACKET)
            dec_response = response.decode()
            should_break = False
            if dec_response.endswith("EOM"):
                dec_response = dec_response[:-3]
                should_break = True
            print(dec_response)
            if should_break:
                break
    except socket.error as err:
        print('received socket error' + str(err))
        logging.error("socket error")

def dir(my_socket, path):
    command_to_server = "DIR " + path
    _private_send_command_to_server(my_socket, command_to_server)

def copy(my_socket, src_path, dst_path):
    command_to_server = "COPY " + src_path + " " + dst_path
    _private_send_command_to_server(my_socket, command_to_server)

def execute(my_socket, path):
    command_to_server = "EXECUTE " + path
    _private_send_command_to_server(my_socket, command_to_server)

def delete(my_socket, path):
    command_to_server = "DELETE " + path
    _private_send_command_to_server(my_socket, command_to_server)

def screenshot(my_socket):
    command_to_server = "TAKE_SCREENSHOT"
    my_socket.send(command_to_server.encode())

    folder = r"C:/cyber/ss_from_server"
    os.makedirs(folder, exist_ok=True)
    full_path = os.path.join(folder, "received_screen.jpg")
    with open(full_path, "wb") as f:
        while True:
            data = my_socket.recv (MAX_PACKET)
            should_break = False
            if b"EOM" in data:
                print("File location: ", full_path)
                should_break = True
            if not should_break:
                f.write(data)
            else:
                break

def exit(my_socket):
    command_to_server = "EXIT"
    _private_send_command_to_server(my_socket, command_to_server)







