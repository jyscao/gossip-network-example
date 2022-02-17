import time

from gossip.client import GossipClient


class GossipServer:
    """A server that participates in a peer-to-peer gossip network."""

    def __init__(self, node_id, port, peers):
        """Initialize a server with a list of peer addresses.

        Peer addresses are in the form HOSTNAME:PORT.
        """

        self.node_id = node_id
        self.port = port

        self.peers = [GossipClient(address) for address in peers]

        print(f"Starting server {node_id} with peers: {peers}")

    def start(self):
        """Starts the server."""

        # TODO: implement GossipServer.start

        try:
            while True:
                time.sleep(5)
        except KeyboardInterrupt:
            return
