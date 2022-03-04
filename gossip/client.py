import socket


class GossipClient:
    """A client interface to connect to a server in a peer-to-peer gossip network."""

    def __init__(self, address):
        self.host, port = address.split(":")
        self.port = int(port)

    def send_message(self, message, is_new=True):
        """Send a message to the server."""

        cmd = "/NEW" if is_new else "/RELAY"
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((self.host, self.port))
            sock.send(bytes(f"{cmd}:{message}", "utf-8"))

    def get_messages(self):
        """Fetch a list of all messages stored by the server."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((self.host, self.port))
            sock.send(bytes("/GET:", "utf-8"))

            print("waiting on message from server...")
            received = str(sock.recv(1024), "utf-8")
            print(received)
