import json
from dataclasses import dataclass, field

from socketserver import ThreadingTCPServer, StreamRequestHandler
from gossip.client import GossipClient

LOCALHOST = "127.0.0.1"


@dataclass
class ServerSettings:
    node_id: int
    port: int
    peer_addrs: list[str]
    msg_box: list[tuple[str, list[int]]] = field(default_factory=list)

    #  @property
    #  def peers(self):
    #      # TODO: avoid instantiating new peer objects each time?
    #      return [GossipClient(addr) for addr in self.peer_addrs]


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
        self._get_cmd_handler()()

    def _get_cmd_handler(self):
        return {
            "/NEW":   self._store_msg,
            "/GET":   self._send_msgs,
            "/RELAY": self._relay_msg,
        }[self.cmd]

    def _store_msg(self):
        self.server.ss.msg_box.append(self.msg)

    def _send_msgs(self):
        msg = json.dumps(self.server.ss.msg_box)
        self.wfile.write(bytes(msg, "utf-8"))

    def _relay_msg(self):
        pass
