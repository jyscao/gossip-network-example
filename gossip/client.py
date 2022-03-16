import socket, json


class GossipClient:
    """A client interface to connect to a server in a peer-to-peer gossip network."""

    def __init__(self, address):
        self.host, port = address.split(":")
        self.port = int(port)

    def send_message(self, message, is_relay=False):
        """Send a message to the server."""

        cmd, msg = ("/RELAY", json.dumps(message)) if is_relay else ("/NEW", message)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((self.host, self.port))
            sock.send(bytes(f"{cmd}:{msg}", "utf-8"))

    def get_messages(self):
        """Fetch a list of all messages stored by the server."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((self.host, self.port))
            sock.send(bytes("/GET:\n", "utf-8"))

            recvd_msgs_ls = []
            while True:
                received = str(sock.recv(1024), "utf-8")
                if received == "":
                    break
                recvd_msgs_ls.append(received)

        return json.loads("".join(recvd_msgs_ls))
