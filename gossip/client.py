import socket, json

from gossip.constants import *


class GossipClient:
    """A client interface to connect to a server in a peer-to-peer gossip network."""

    def __init__(self, address):
        host, port = address.split(":")
        self.id = int(port) - PORTS_ORIGIN
        self.host_port_tup = (host, int(port))

    def __repr__(self):
        return f"Gossip-Node-{self.id}"

    def send_message(self, message, is_relay=False):
        """Send a message to the server."""

        cmd = "/RELAY" if is_relay else "/NEW"
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            self._send_to_socket(sock, f"{cmd}:{message}")

    def get_messages(self):
        """Fetch a list of all messages stored by the server."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            self._send_to_socket(sock, "/GET:\n")

            recvd_msgs_ls = []
            while True:
                received = str(sock.recv(1024), "utf-8")
                if received == "":
                    break
                recvd_msgs_ls.append(received)

        return json.loads("".join(recvd_msgs_ls))

    def _send_to_socket(self, sock, cmd_data):
        sock.connect(self.host_port_tup)
        sock.send(bytes(cmd_data, "utf-8"))
