import json
from dataclasses import dataclass, field

from socketserver import ThreadingTCPServer, StreamRequestHandler
from gossip.client import GossipClient

LOCALHOST = "127.0.0.1"


@dataclass
class ServerSettings:
    node_id:    int
    port:       int
    peer_addrs: list[str]
    peers:      list[GossipClient] = field(init=False)
    msg_box:    list[tuple[str, list[int]]] = field(default_factory=list)

    def __post_init__(self):
        self.peers = [GossipClient(addr) for addr in self.peer_addrs]


class GossipServer:
    """A server that participates in a peer-to-peer gossip network."""

    def __init__(self, node_id, port, peer_addrs):
        """Initialize a server with a list of peer addresses.

        Peer addresses are in the form HOSTNAME:PORT.
        """
        self.ss = ServerSettings(node_id, port, peer_addrs)

    def start(self):
        """Starts the server."""

        print(f"Starting server {self.ss.node_id} with peers: {self.ss.peer_addrs}")

        host_port_tup = (LOCALHOST, self.ss.port)
        with MsgQueueTCPServer(host_port_tup, GossipMessageHandler, self.ss) as server:
            server.serve_forever()


class MsgQueueTCPServer(ThreadingTCPServer):

    def __init__(self, host_port_tup, request_handler, server_settings):
        super().__init__(host_port_tup, request_handler)
        self.ss = server_settings


class GossipMessageHandler(StreamRequestHandler):

    def handle(self):
        self.cmd, self.msg = self.rfile.readline().decode().split(":", maxsplit=1)
        self._get_cmd_handler()(self._get_handler_args())

    def _get_cmd_handler(self):
        return {
            "/NEW":   self._store_msg,
            "/GET":   self._dump_msgs,
            "/RELAY": self._relay_msg,
        }[self.cmd]

    def _get_handler_args(self):
        return {
            "/NEW":   (self.msg, [self.server.ss.node_id]),
            "/GET":   None,
            "/RELAY": (self.msg, ["HELLO", "WORLD"]),
        }[self.cmd]

    def _store_msg(self, msg_tup):
        self.server.ss.msg_box.append(msg_tup)

    def _dump_msgs(self, _):
        f_n = lambda n: f"Node {str(n)}"
        messages = json.dumps([f"{msg} ({' -> '.join(f_n(n) for n in nodes)})" for msg, nodes in self.server.ss.msg_box])
        self.wfile.write(bytes(messages, "utf-8"))

    def _relay_msg(self, msg_tup):
        pass
