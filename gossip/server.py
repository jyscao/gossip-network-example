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


class GossipMessageHandler(StreamRequestHandler):

    def handle(self):
        self._recv_message()
        print(f"server messge queue: {self.server.msg_q}")

    def _dispatch_cmd(self, cmd):
        return {
            "GET": self._send_messages,
            "NEW": self._recv_message,
        }[cmd.decode("utf-8")]

    def _recv_message(self):
        msg = self.rfile.readline()
        print(f"received message '{msg}' from client")
        self.server.msg_q.append(msg)

    def _send_messages(self):
        for msg in self.messages:
            self.wfile.write(msg)


class MsgQueueTCPServer(ThreadingTCPServer):

    def __init__(self, host_port_tup, request_handler, msg_q):
        super().__init__(host_port_tup, request_handler)
        self.msg_q = msg_q

