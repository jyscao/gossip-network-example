import json

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

        self.messages = []

    def start(self):
        """Starts the server."""

        print(f"Starting server {self.node_id} with peers: {self.peer_addrs}")

        with MsgQueueTCPServer((LOCALHOST, self.port), GossipMessageHandler, self.messages) as server:
            server.serve_forever()


class MsgQueueTCPServer(ThreadingTCPServer):

    def __init__(self, host_port_tup, request_handler, msg_q):
        super().__init__(host_port_tup, request_handler)
        self.msg_q = msg_q


class GossipMessageHandler(StreamRequestHandler):

    def handle(self):
        self.cmd, self.msg = self.rfile.readline().decode().split(":", maxsplit=1)
        self._get_cmd_handler()()

    def _get_cmd_handler(self):
        return {
            "/NEW": self._recv_message,
            "/GET": self._send_messages,
        }[self.cmd]

    def _recv_message(self):
        self.server.msg_q.append(self.msg)

    def _send_messages(self):
        msg = json.dumps(self.server.msg_q)
        self.wfile.write(bytes(msg, "utf-8"))
