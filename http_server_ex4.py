"""
Author: Asaf Biran
program name - ex4
Description: A http protocol server that handles client requests from
browser and infinite clients, one after the other.
"""
import socket
from pathlib import Path


QUEUE_SIZE = 10
IP = '127.0.0.1'
PORT = 80
SOCKET_TIMEOUT = 2
WEBROOT = Path("C:\\cyber\\ex4\\webroot")
DEFAULT_URL = "/index.html"

STATUS_CODES = {
    "/400": {
        "status": "400 Bad Request",
        "headers": {},
        "body": True
    },
    "/404": {
        "status": "404 Not Found",
        "headers": {},
        "body": True
    },
    "/forbidden": {
        "status": "403 Forbidden",
        "headers": {},
        "body": True
    },
    "/forbidden/": {
        "status": "403 Forbidden",
        "headers": {},
        "body": True
    },
    "/moved": {
        "status": "302 Moved Temporarily",
        "headers": {"Location": "/"},
        "body": False
    },
    "/moved/": {
        "status": "302 Moved Temporarily",
        "headers": {"Location": "/"},
        "body": False
    },
    "/error": {
        "status": "500 Internal Server Error",
        "headers": {},
        "body": True
    },
    "/error/": {
        "status": "500 Internal Server Error",
        "headers": {},
        "body": True
    }
}

def get_file_data(file_name):
    """
    Get data from file
    :param file_name: the name of the file
    :return: the file data in a string
    """

    #body = file_name.read_bytes()
    #return body
    if file_name.suffix[1:] in ['html', 'js', 'txt', 'css']:  # check extension without dot
        body = file_name.read_text(encoding="utf-8")  # text files
    else:
        body = file_name.read_bytes()  # images

    return body


def handle_client_request(resource, client_socket):
    """
    Check the required resource, generate proper HTTP response and send
    to client
    """
    global WEBROOT
    if resource == '/' or '':
        uri = DEFAULT_URL
    else:
        uri = resource




    filename = WEBROOT / uri.lstrip("/")


    file_type = filename.suffix

    body = get_file_data(filename)
    if file_type == '.html':
        http_header_and_body =   ( "HTTP/1.1 200 OK\r\n"
                                   "Content-Type: text/html; charset=utf-8\r\n"
                                   f"Content-Length: {len(body.encode('utf-8'))}\r\n\r\n"
                                   f"{body}")
        http_response = http_header_and_body.encode('utf-8')
    elif file_type == '.jpg':
        http_header_and_body =  ( "HTTP/1.1 200 OK\r\n"
                                  "Content-Type: image/jpeg\r\n"
                                  f"Content-Length: {len(body)}\r\n\r\n"
                                  )
        http_response = http_header_and_body.encode('utf-8') + body
    elif file_type == '.css':
        http_header_and_body = ( "HTTP/1.1 200 OK\r\n"
                                 "Content-Type: text/css\r\n"
                                 f"Content-Length: {len(body.encode())}\r\n\r\n"
                                 f"{body}")
        http_response = http_header_and_body.encode('utf-8')
    elif file_type == '.js':
        http_header_and_body = ( "HTTP/1.1 200 OK\r\n"
                                 "Content-Type: text/javascript; charset=UTF-8\r\n"
                                 f"Content-Length: {len(body.encode('utf-8'))}\r\n\r\n"
                                 f"{body}")
        http_response = http_header_and_body.encode('utf-8')
    elif file_type == '.txt':
        http_header_and_body = ( "HTTP/1.1 200 OK\r\n"
                                 "Content-Type: text/plain\r\n"
                                 f"Content-Length: {len(body)}\r\n\r\n"
                                 f"{body}")
        http_response = http_header_and_body.encode('utf-8')
    elif file_type == '.ico':
        http_header_and_body = ( "HTTP/1.1 200 OK\r\n"
                                 "Content-Type: image/x-icon\r\n"
                                 f"Content-Length: {len(body)}\r\n\r\n"
                                 )
        http_response = http_header_and_body.encode('utf-8') + body
    elif file_type == '.gif':
        http_header_and_body = ( "HTTP/1.1 200 OK\r\n"
                                 "Content-Type: image/jpeg\r\n"
                                 f"Content-Length: {len(body)}\r\n\r\n"
                                 )
        http_response = http_header_and_body.encode('utf-8') + body
    elif file_type == '.png':
        http_header_and_body = ( "HTTP/1.1 200 OK\r\n"
                                 "Content-Type: image/png\r\n"
                                 f"Content-Length: {len(body)}\r\n\r\n"
                                 )
        http_response = http_header_and_body.encode('utf-8') + body
    else:
        handle_client_request("/404", client_socket)
        return


    print ("=== SERVER RESPONSE: ", http_response)
    client_socket.send(http_response)



def validate_http_request(request):
    """
    Checks if request is a valid HTTP request and returns TRUE / FALSE and
    the requested URL
    """

    if not request:
        return (False,None)

    if "\r\n\r\n" not in request:
        return False

    lines = request.split("\r\n")
    if len(lines) < 1:
        return (False,None)

    request_line = lines[0]
    parts = request_line.split()

    if len(parts) != 3:
        return (False,None)

    method, url, version = parts

    valid_methods = {"GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS", "PATCH"}
    if method not in valid_methods:
        return (False, url)

    if not url.startswith("/"):
        return (False, url)

    if not version.startswith("HTTP/"):
        return (False, url)

    return (True, url)


def handle_client(client_socket):
    """
    Handles client requests: verifies client's requests are legal HTTP, calls
    function to handle the requests
    """
    print('Client connected')
    while True:
        client_request = client_socket.recv(4096).decode("utf-8")
        print ("=== CLIENT REQUEST: ", client_request )
        valid_http, resource = validate_http_request(client_request)
        if valid_http:
            print('Got a valid HTTP request')
            handle_client_request(resource, client_socket)
        else:
            handle_client_request("/400", client_socket)
            break
    print('Closing connection')


def main():
    # Open a socket and loop forever while waiting for clients
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((IP, PORT))
        server_socket.listen(QUEUE_SIZE)
        print("Listening for connections on port %d" % PORT)
        while True:
            client_socket, client_address = server_socket.accept()
            try:
                print('New connection received')
                client_socket.settimeout(SOCKET_TIMEOUT)
                handle_client(client_socket)
            except socket.error as err:
                print('received socket exception - ' + str(err))
            finally:
                client_socket.close()
    except socket.error as err:
        print('received socket exception - ' + str(err))
    finally:
        server_socket.close()


if __name__ == "__main__":
    assert validate_http_request("GET / HTTP/1.1\r\n\r\n") == (True, "/")
    assert validate_http_request("GET /index.html HTTP/1.1\r\n\r\n") == (True, "/index.html")
    assert validate_http_request("") == (False, None)
    assert validate_http_request("GET / HTTP/1.1") is False
    assert validate_http_request("TIGRIS / HTTP/1.1\r\n\r\n") == (False, "/")
    assert validate_http_request("GET index.html HTTP/1.1\r\n\r\n") == (False, "index.html")
    assert validate_http_request("GET / index\r\n\r\n") == (False, "/")
    print("All tests passed")
    main()