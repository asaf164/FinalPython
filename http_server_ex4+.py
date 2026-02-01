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
WEBROOT = Path(r"C:\cyber\ex4\webroot")
UPLOAD_DIR = Path(r"C:\cyber\upload")

if not UPLOAD_DIR.exists():
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_URL = "/index.html"

MIME_TYPES = {
    '.html': 'text/html;charset=utf-8',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.css': 'text/css',
    '.js': 'text/javascript; charset=UTF-8',
    '.txt': 'text/plain',
    '.ico': 'image/x-icon',
    '.gif': 'image/gif',
    '.png': 'image/png'
}


def get_file_data(filename):
    """
    Reads binary data from a file safely.
    Returns the file content as bytes or None if an error occurs.
    """
    try:
        return filename.read_bytes()
    except Exception:
        return None


def send_response(client_socket, status_code, status_text, headers=None, body=None):
    """
    Constructs and sends a properly formatted HTTP response to the client.
    Handles headers, calculates content length, and sends the body.
    """
    if headers is None:
        headers = {}

    if body is None:
        body_bytes = b""
    elif isinstance(body, str):
        body_bytes = body.encode('utf-8')
    else:
        body_bytes = body  # Already bytes

    if len(body_bytes) > 0 and "Content-Type" not in headers:
        headers["Content-Type"] = "text/plain; charset=utf-8"

    response_header = f"HTTP/1.1 {status_code} {status_text}\r\n"
    for key, value in headers.items():
        response_header += f"{key}: {value}\r\n"

    response_header += f"Content-Length: {len(body_bytes)}\r\n"
    response_header += "\r\n"

    try:
        client_socket.send(response_header.encode('utf-8'))
        if len(body_bytes) > 0:
            client_socket.send(body_bytes)
    except socket.error as e:
        print(f"Error sending response: {e}")


def parse_query_params(query_string):
    """
    Parses a query string (e.g., 'key=value&a=b') into a dictionary.
    """
    params = {}
    if not query_string:
        return params

    pairs = query_string.split('&')
    for pair in pairs:
        if '=' in pair:
            key, value = pair.split('=', 1)
            params[key] = value
    return params


def handle_client_request(resource, method, body, client_socket):
    """
    Processes the specific client request based on the method and resource path.
    Handles specific logic for calculation, file uploads, and static file serving.
    """
    if '?' in resource:
        path, query_string = resource.split('?', 1)
    else:
        path = resource
        query_string = ""

    params = parse_query_params(query_string)

    if path == "/calculate-next":
        num_str = params.get('num')
        if num_str and num_str.strip().lstrip('-').isdigit():
            result = str(int(num_str.strip()) + 1)
            send_response(client_socket, "200", "OK", {"Content-Type": "text/plain"}, result)
        else:
            send_response(client_socket, "400", "Bad Request", {}, "Error: Missing or invalid 'num' parameter")
        return

    if path == "/calculate-area":
        height_str = params.get('height')
        width_str = params.get('width')

        try:
            h = float(height_str.strip())
            w = float(width_str.strip())
            area = (h * w) / 2.0
            send_response(client_socket, "200", "OK", {"Content-Type": "text/plain"}, str(area))
        except (AttributeError, ValueError, TypeError):
            send_response(client_socket, "400", "Bad Request", {}, "Error: height and width must be valid numbers")
        return

    if path == "/upload":
        if method == "POST":
            file_name = params.get('file-name')
            if file_name:
                file_path = UPLOAD_DIR / file_name
                try:
                    with open(file_path, 'wb') as f:
                        f.write(body)
                    send_response(client_socket, "200", "OK", {}, "File uploaded successfully")
                except Exception as e:
                    print(f"Upload error: {e}")
                    send_response(client_socket, "500", "Internal Server Error", {}, "Failed to save file")
            else:
                send_response(client_socket, "400", "Bad Request", {}, "Error: Missing 'file-name' parameter")
        else:
            send_response(client_socket, "400", "Bad Request", {}, "Error: Upload must use POST")
        return

    if path == "/image":
        image_name = params.get('image-name')
        if image_name:
            file_path = UPLOAD_DIR / image_name
            if file_path.exists() and file_path.is_file():
                file_content = get_file_data(file_path)
                ctype = MIME_TYPES.get(file_path.suffix.lower(), 'image/jpeg')
                send_response(client_socket, "200", "OK", {"Content-Type": ctype}, file_content)
            else:
                send_response(client_socket, "404", "Not Found", {}, "Error: Image file not found")
        else:
            send_response(client_socket, "400", "Bad Request", {}, "Error: Missing 'image-name' parameter")
        return

    if path == "/400":
        send_response(client_socket, "400", "Bad Request", {}, "Error: 400 Bad Request Triggered")
        return
    if path == "/forbidden":
        send_response(client_socket, "403", "Forbidden", {}, "Error: 403 Forbidden Triggered")
        return
    if path == "/error":
        send_response(client_socket, "500", "Internal Server Error", {}, "Error: 500 Internal Error Triggered")
        return
    if path == "/moved":
        send_response(client_socket, "302", "Moved Temporarily", {"Location": "/"})
        return

    uri = path
    if uri == '/' or uri == '':
        uri = DEFAULT_URL

    filename = WEBROOT / uri.lstrip("/")

    if not filename.exists() or not filename.is_file():
        send_response(client_socket, "404", "Not Found", {}, "404 Not Found")
        return

    body_data = get_file_data(filename)
    if body_data is None:
        send_response(client_socket, "500", "Internal Server Error", {}, "Error reading static file")
    else:
        ctype = MIME_TYPES.get(filename.suffix.lower(), 'text/plain')
        send_response(client_socket, "200", "OK", {"Content-Type": ctype}, body_data)


def validate_http_request(request_text):
    """
    Validates if the HTTP request line is correctly formatted.
    Returns a tuple of (is_valid, method, url).
    """
    if not request_text:
        return False, None, None

    lines = request_text.split("\r\n")
    if len(lines) < 1:
        return False, None, None

    parts = lines[0].split()
    if len(parts) != 3:
        return False, None, None

    method, url, version = parts

    valid_methods = {"GET", "POST", "PUT", "DELETE"}
    if method not in valid_methods:
        return False, None, url

    if not version.startswith("HTTP/"):
        return False, method, url

    return True, method, url


def handle_client(client_socket):
    """
    Handles a single client connection: reads the request, validates it,
    and delegates processing to handle_client_request.
    """
    print('Client connected')
    try:
        raw_data = client_socket.recv(8192)
        if not raw_data:
            return

        if b'\r\n\r\n' in raw_data:
            header_bytes, body_bytes = raw_data.split(b'\r\n\r\n', 1)
        else:
            header_bytes = raw_data
            body_bytes = b""

        try:
            header_text = header_bytes.decode('utf-8')
            full_header = header_text + "\r\n\r\n"
        except UnicodeDecodeError:
            send_response(client_socket, "400", "Bad Request", {}, "Error: Header encoding invalid")
            return

        valid_http, method, resource = validate_http_request(full_header)

        if valid_http:
            handle_client_request(resource, method, body_bytes, client_socket)
        else:
            print("Invalid HTTP Request")
            send_response(client_socket, "400", "Bad Request", {}, "Error: Malformed HTTP Request")

    except socket.timeout:
        print("Socket timed out")
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        client_socket.close()


def main():
    """
    Main server loop: sets up the socket, listens for connections,
    and accepts incoming clients.
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server_socket.bind((IP, PORT))
        server_socket.listen(QUEUE_SIZE)
        print(f"Server is listening on port {PORT}")
        while True:
            client_socket, client_address = server_socket.accept()
            try:
                client_socket.settimeout(SOCKET_TIMEOUT)
                handle_client(client_socket)
            except socket.error:
                pass
    except socket.error as err:
        print(f"Socket Error: {err}")
    finally:
        server_socket.close()


if __name__ == "__main__":
    valid, meth, url = validate_http_request("GET / HTTP/1.1\r\n\r\n")
    assert valid and meth == "GET" and url == "/"
    valid, meth, url = validate_http_request("POST /upload?file=x HTTP/1.1\r\n\r\n")
    assert valid and meth == "POST" and url == "/upload?file=x"

    main()