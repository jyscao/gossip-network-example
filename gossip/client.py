import socket, json

from gossip.constants import *


class GossipClient:
    """A client interface to connect to a server in a peer-to-peer gossip network."""

    def __init__(self, address):
        host, port = address.split(":")
        self.id = int(port) - PORTS_ORIGIN
        self.host_port_tup = (host, int(port))

    def send_message(self, message, is_relay=False):
        """Send a message to the server."""

        cmd = "/RELAY" if is_relay else "/NEW"
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(self.host_port_tup)
            sock.send(bytes(f"{cmd}:{message}", "utf-8"))

    def get_messages(self):
        """Fetch a list of all messages stored by the server."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(self.host_port_tup)
            sock.send(bytes("/GET:\n", "utf-8"))

            recvd_msgs_ls = []
            while True:
                received = str(sock.recv(1024), "utf-8")
                if received == "":
                    break
                recvd_msgs_ls.append(received)

        return json.loads("".join(recvd_msgs_ls))
