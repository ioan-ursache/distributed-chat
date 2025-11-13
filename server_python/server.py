# server.py (only showing integration highlights)
import socket
import threading
import json
from client_handler import ClientHandler
from chat_room import ChatRoom
from udp_presence import UDPPresenceBroadcaster

HOST = "0.0.0.0"
PORT = 5000
UDP_PORT = 6000

class Server:
    def __init__(self, host=HOST, port=PORT, udp_port=UDP_PORT):
        self.host = host
        self.port = port
        self.udp_port = udp_port
        self.server_socket = None
        self.clients = []
        self.lock = threading.Lock()
        self.lobby = ChatRoom("Lobby")
        self.udp_broadcaster = UDPPresenceBroadcaster(self, udp_port=self.udp_port)

    def start(self):
        self.udp_broadcaster.start()

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"[SERVER] Listening on {self.host}:{self.port} (UDP presence on port {self.udp_port})")

        try:
            while True:
                client_sock, client_addr = self.server_socket.accept()
                print(f"[CONNECT] {client_addr} connected.")
                handler = ClientHandler(client_sock, client_addr, self)
                handler.start()
                with self.lock:
                    self.clients.append(handler)
                self.lobby.join(handler)
                self.udp_broadcaster.broadcast_join(handler.username)
        except KeyboardInterrupt:
            print("\n[SERVER] Shutting down...")
        finally:
            self.stop()

    def remove_client(self, handler):
        """Remove disconnected client from server and lobby."""
        with self.lock:
            if handler in self.clients:
                self.clients.remove(handler)
        self.lobby.leave(handler)
        # broadcast leave over UDP
        try:
            self.udp_broadcaster.broadcast_leave(handler.username)
        except Exception:
            pass

    def stop(self):
        """Cleanly close server socket and UDP broadcaster."""
        # stop UDP broadcaster
        try:
            self.udp_broadcaster.stop()
        except Exception:
            pass
        for client in list(self.clients):
            client.close()
        if self.server_socket:
            self.server_socket.close()
        print("[SERVER] Closed.")
