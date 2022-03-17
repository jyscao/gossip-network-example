import socket, json

from gossip.constants import *


class GossipClient:
    """A client interface to connect to a server in a peer-to-peer gossip network."""

    def __init__(self, address):
        self.address = address
        host, port = self.address.split(":")
        self.host_port_tup = (host, int(port))
        self.id = int(port) - PORTS_ORIGIN
        self.node_name = f"Gossip-Node-{self.id}"

    def __repr__(self):
        return self.node_name

    def send_message(self, message, is_relay=False):
        """Send a message to the server."""
        cmd = "/RELAY" if is_relay else "/NEW"
        self._send_to_server(f"{cmd}:{message}\n")

    def get_messages(self):
        """Fetch a list of all messages stored by the server."""
        return self._send_to_then_get_from_server("/GET:\n")

    def _send_to_server(self, cmd_data):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            self._send_to_socket(sock, cmd_data)

    def _send_to_then_get_from_server(self, cmd_data):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            self._send_to_socket(sock, cmd_data)
            response = self._recv_server_full_response(sock)
        return response

    def _send_to_socket(self, sock, cmd_data):
        sock.connect(self.host_port_tup)
        sock.send(bytes(cmd_data, "utf-8"))

    def _recv_server_full_response(self, sock):
        response_ls = []
        while True:
            received = str(sock.recv(1024), "utf-8")
            if received == "":
                break
            response_ls.append(received)
        return json.loads("".join(response_ls))
