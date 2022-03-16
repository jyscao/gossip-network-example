import socket, json, time
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
    msg_box:    list[tuple[str, int, list[int]]] = field(default_factory=list)
    msg_id_set: set[str] = field(default_factory=set)

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

        print(f"Starting server {self.ss.node_id} with peers: {self.ss.peers}")

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
            "/RELAY": self._proc_relayed_msg,
            "/GET":   self._show_client_msgs,
        }[self.cmd]

    def _proc_new_msg(self):
        self.origin_node, self.prev_node = self.server.ss.node_id, None
        new_msg_timestamp = time.time_ns()
        self.msg_id = f"{self.msg_data}_{new_msg_timestamp}"
        self._store_and_relay((self.msg_data, new_msg_timestamp, [self.origin_node]))

    def _proc_relayed_msg(self):
        msg, timestamp, nodes = json.loads(self.msg_data)
        self.msg_id = f"{msg}_{timestamp}"
        self.origin_node, self.prev_node = nodes[0], nodes[-1]
        nodes.append(self.server.ss.node_id)
        self._store_and_relay((msg, timestamp, nodes))

    def _show_client_msgs(self):
        f_n  = lambda n: f"Node {str(n)}"
        msgs_list = [f"{msg} ({' -> '.join(f_n(n) for n in nodes)})" for msg, _, nodes in self.server.ss.msg_box]
        self.wfile.write(bytes(json.dumps(msgs_list), "utf-8"))

    def _store_and_relay(self, msg_tup):
        if self.msg_id not in self.server.ss.msg_id_set:
            self.server.ss.msg_box.append(msg_tup)
            # TODO: add ability to store all paths taken by relayed message in gossip network
            self.server.ss.msg_id_set.add(self.msg_id)

        if True:
            # TODO: implement checks to track if the same message has already been relayed to peers currently,
            # it's not a problem b/c all nodes are circularly-connected, and transmission stops at the origin
            # node; but transmission stoppage is not guaranteed when nodes are connected as an arbitrary graph
            self._relay_to_peers(msg_tup)

    def _relay_to_peers(self, data):
        for p in self._get_peers_to_relay():
            p.send_message(json.dumps(data), is_relay=True)

    def _get_peers_to_relay(self):
        if self.cmd == "/NEW":
            return self.server.ss.peers
        elif self.cmd == "/RELAY" and self._is_msg_originator():
            return []
        elif self.prev_node is not None:
            # filter out the source node of the current message
            return [p for p in self.server.ss.peers if p.id != self.prev_node]
        else:
            raise Exception("this should never be reached!")

    def _is_msg_originator(self):
        return self.server.ss.node_id == self.origin_node
