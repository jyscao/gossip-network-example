import socket


class GossipClient:
    """A client interface to connect to a server in a peer-to-peer gossip network."""

    def __init__(self, address):
        self.host, port = address.split(":")
        self.port = int(port)

    def send_message(self, message):
        """Send a message to the server."""

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((self.host, self.port))
            sock.sendall(bytes(message, "utf-8"))

    def get_messages(self):
        """Fetch a list of all messages stored by the server."""

        # TODO: implement GossipClient.get_messages

        return [
            "Apple (Node 1 -> Node 8 -> Node 10)",
            "Banana (Node 3 -> Node 5 -> Node 10)",
            "Orange (Node 7 -> Node 15 -> Node 9 -> Node 10)",
        ]
