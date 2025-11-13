# udp_presence.py
import socket
import json
import threading
import time

BROADCAST_ADDR = "<broadcast>"   # socket option uses '' or broadcast IP; we'll use sendto(('255.255.255.255',port))
DEFAULT_UDP_PORT = 6000
BROADCAST_INTERVAL = 15.0  # seconds for periodic snapshot

class UDPPresenceBroadcaster(threading.Thread):
    def __init__(self, server_ref, udp_port=DEFAULT_UDP_PORT, interval=BROADCAST_INTERVAL):
        super().__init__(daemon=True)
        self.server = server_ref
        self.udp_port = udp_port
        self.interval = interval
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # allow broadcast
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.running = True

    def run(self):
        # Periodically broadcast full user list
        while self.running:
            self.broadcast_full_state()
            time.sleep(self.interval)

    def stop(self):
        self.running = False
        try:
            self.sock.close()
        except Exception:
            pass

    def broadcast_raw(self, obj):
        try:
            data = json.dumps(obj).encode("utf-8")
            # Broadcast on global broadcast address. Works on typical LANs and VM bridged mode.
            self.sock.sendto(data, ('255.255.255.255', self.udp_port))
        except Exception as e:
            # Non-fatal — log for debugging
            print(f"[UDP] Broadcast error: {e}")

    def broadcast_join(self, username):
        msg = {"type": "presence", "event": "joined", "user": username, "users": self.server.get_user_list()}
        self.broadcast_raw(msg)

    def broadcast_leave(self, username):
        msg = {"type": "presence", "event": "left", "user": username, "users": self.server.get_user_list()}
        self.broadcast_raw(msg)

    def broadcast_full_state(self):
        msg = {"type": "presence", "event": "full_state", "users": self.server.get_user_list()}
        self.broadcast_raw(msg)

        try:
            data = json.dumps(obj).encode("utf-8")
            # Broadcast on global broadcast address. Works on typical LANs and VM bridged mode.
            self.sock.sendto(data, ('255.255.255.255', self.udp_port))
        except Exception as e:
            # Non-fatal — log for debugging
            print(f"[UDP] Broadcast error: {e}")