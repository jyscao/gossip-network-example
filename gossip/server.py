import socket, json
from dataclasses import dataclass, field

from socketserver import ThreadingTCPServer, StreamRequestHandler
from gossip.client import GossipClient
from gossip.constants import *


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
        self.cmd, self.msg_data = self.rfile.readline().decode().split(":", maxsplit=1)
        self._get_cmd_handler()()

    def _get_cmd_handler(self):
        return {
            "/NEW":   self._proc_new_msg,
            "/GET":   self._show_client_msgs,
            "/RELAY": self._proc_relayed_msg,
        }[self.cmd]

    def _proc_new_msg(self):
        msg_tup = (self.msg_data, [self.server.ss.node_id])
        self.src_node = None
        self.server.ss.msg_box.append(msg_tup)
        self._send_to_peers(msg_tup)

    def _show_client_msgs(self):
        f_n  = lambda n: f"Node {str(n)}"
        msgs_list = [f"{msg} ({' -> '.join(f_n(n) for n in nodes)})" for msg, nodes in self.server.ss.msg_box]
        self.wfile.write(bytes(json.dumps(msgs_list), "utf-8"))

    def _store_msg(self, msg_tup):
        self.server.ss.msg_box.append(msg_tup)

    def _dump_msgs(self, _):
        f_n  = lambda n: f"Node {str(n)}"
        msgs = [f"{msg} ({' -> '.join(f_n(n) for n in nodes)})" for msg, nodes in self.server.ss.msg_box]
        self._write_json_msg(msgs)

    def _relay_msg(self, msg_tup):
        pass
