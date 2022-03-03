from socketserver import ThreadingTCPServer, StreamRequestHandler
from gossip.client import GossipClient

LOCALHOST = "127.0.0.1"


class GossipServer:
    """A server that participates in a peer-to-peer gossip network."""

    def __init__(self, node_id, port, peers):
        """Initialize a server with a list of peer addresses.

        Peer addresses are in the form HOSTNAME:PORT.
        """

        self.node_id = node_id
        self.port = port

        self.peer_addrs = peers
        self.peers = [GossipClient(address) for address in peers]

    def start(self):
        """Starts the server."""

        print(f"Starting server {self.node_id} with peers: {self.peer_addrs}")

        with ThreadingTCPServer((LOCALHOST, self.port), GossipMessageHandler) as server:
            server.serve_forever()


class GossipMessageHandler(StreamRequestHandler):

    def handle(self):
        self.data = self.rfile.readline().strip()
        print(self.data)
        self.wfile.write(self.data.upper())
