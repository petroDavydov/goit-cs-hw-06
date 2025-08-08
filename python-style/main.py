import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from multiprocessing import Process
import socket
import json
from datetime import datetime
from pymongo import MongoClient
import os

logging.basicConfig(level=logging.INFO)

FRONT_DIR = os.path.join(os.path.dirname(__file__), "..", "front-init")
STORAGE_PATH = os.path.join(os.path.dirname(
    __file__), "..", "storage", "data.json")


def backup_to_json(data):
    try:
        with open(STORAGE_PATH, "r") as f:
            existing = json.load(f)
    except Exception:
        existing = []

    existing.append(data)

    with open(STORAGE_PATH, "w") as f:
        json.dump(existing, f, indent=2)


class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        if parsed_url.path == "/":
            self.send_html_file("index.html")
        elif parsed_url.path == "/message.html":
            self.send_html_file("message.html")
        elif parsed_url.path == "/error.html":
            self.send_html_file("error.html")
        elif parsed_url.path == "/style.css":
            self.send_static_file("style.css", "text/css")
        elif parsed_url.path == "/logo.png":
            self.send_static_file("logo.png", "image/png")
        else:
            self.send_html_file("error.html", 404)

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)
        parsed_data = parse_qs(post_data.decode("utf-8"))
        username = parsed_data.get("username", [""])[0]
        message = parsed_data.get("message", [""])[0]

        if not username or not message:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Invalid input")
            return

        message_data = {
            "username": username,
            "message": message
        }

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(("localhost", 5000))
                s.sendall(json.dumps(message_data).encode("utf-8"))
        except Exception as e:
            logging.error(f"Socket error: {e}")
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"Failed to send message")
            return

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Message sent!")

    def send_html_file(self, filename, status=200):
        path = os.path.join(FRONT_DIR, filename)
        try:
            with open(path, "rb") as file:
                self.send_response(status)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(file.read())
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 Not Found")

    def send_static_file(self, filename, content_type):
        path = os.path.join(FRONT_DIR, filename)
        try:
            with open(path, "rb") as file:
                self.send_response(200)
                self.send_header("Content-type", content_type)
                self.end_headers()
                self.wfile.write(file.read())
        except FileNotFoundError:
            self.send_html_file("error.html", 404)


def run_http_server():
    server_address = ("", 3000)
    httpd = HTTPServer(server_address, HttpHandler)
    logging.info("HTTP server started on port 3000")
    httpd.serve_forever()


def run_socket_server():
    client = MongoClient("mongodb://mongodb:27017/")
    db = client["message_db"]
    collection = db["messages"]

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("0.0.0.0", 5000))
        s.listen()
        logging.info("Socket server started on port 5000")

        while True:
            conn, addr = s.accept()
            with conn:
                data = conn.recv(1024)
                if not data:
                    continue
                try:
                    message = json.loads(data.decode("utf-8"))
                    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                    message_data = {
                        "date": date,
                        "username": message["username"],
                        "message": message["message"]
                    }

                    collection.insert_one(message_data)

                    # Створюємо копію без _id для JSON
                    safe_data = {
                        "date": message_data["date"],
                        "username": message_data["username"],
                        "message": message_data["message"]
                    }

                    backup_to_json(safe_data)
                    logging.info(f"Saved message: {safe_data}")
                except Exception as e:
                    logging.error(f"Failed to process message: {e}")


if __name__ == "__main__":
    http_process = Process(target=run_http_server)
    socket_process = Process(target=run_socket_server)

    http_process.start()
    socket_process.start()

    http_process.join()
    socket_process.join()
