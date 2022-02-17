class GossipClient:
    """A client interface to connect to a server in a peer-to-peer gossip network."""

    def __init__(self, address):
        self.address = address

    def send_message(self, message):
        """Send a message to the server."""

        # TODO: implement GossipClient.send_message

        return None

    def get_messages(self):
        """Fetch a list of all messages stored by the server."""

        # TODO: implement GossipClient.get_messages

        return [
            "Apple (Node 1 -> Node 8 -> Node 10)",
            "Banana (Node 3 -> Node 5 -> Node 10)",
            "Orange (Node 7 -> Node 15 -> Node 9 -> Node 10)",
        ]
