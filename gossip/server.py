import socket, json, time
from dataclasses import dataclass, field
from collections import Counter

from socketserver import ThreadingTCPServer, StreamRequestHandler
from gossip.client import GossipClient
from gossip.constants import PORTS_ORIGIN, RELAY_COUNTS


@dataclass
class ServerSettings:
    hostname:   str
    port:       int
    peer_addrs: list[str]
    node_id:    int = None
    peers:      list[GossipClient] = field(init=False)
    msgs_box:   dict[dict] = field(default_factory=dict)

    def __post_init__(self):
        self.node_id = int(self.port) - PORTS_ORIGIN
        self.peers = [GossipClient(addr) for addr in self.peer_addrs]


class GossipServer:
    """A server that participates in a peer-to-peer gossip network."""

    def __init__(self, server_address, peer_addrs):
        """Initialize a server with a list of peer addresses.

        Peer addresses are in the form HOSTNAME:PORT.
        """
        hostname, port = server_address.split(":")
        self.host_port_tup = (hostname, int(port))
        self.ss = ServerSettings(hostname, port, peer_addrs)

    def start(self):
        print(f"Starting server {self.ss.node_id} with peers: {self.ss.peers}")
        with GossipTCPServer(self.host_port_tup, GossipMessageHandler, self.ss) as server:
            server.serve_forever()


class GossipTCPServer(ThreadingTCPServer):

    def __init__(self, host_port_tup, request_handler, server_settings):
        super().__init__(host_port_tup, request_handler)
        self.ss = server_settings


class GossipMessageHandler(StreamRequestHandler):

    # TODO: make appropriate properties private, e.g. self._msg_id

    def handle(self):
        self.cmd, self.msg_data = self.rfile.readline().strip().decode().split(":", maxsplit=1)
        self._get_cmd_handler()()

    def _get_cmd_handler(self):
        return {
            "/NEW":   self._proc_new_msg,
            "/RELAY": self._proc_relayed_msg,
            "/GET":   self._send_client_msgs_data,
            "/PEERS": self._get_peers_info,
            "/REMOVE": self._remove_peer,
        }[self.cmd]

    def _proc_new_msg(self):
        new_msg_timestamp = time.time_ns()
        self.msg_id = f"{self.msg_data}_{new_msg_timestamp}"
        self.curr_msg_attrs = self.server.ss.msgs_box[self.msg_id] = self._init_new_msg_attrs(self.msg_id)
        self.node_path = [self.server.ss.node_id]
        self._save_path_and_relay()

    def _proc_relayed_msg(self):
        self.msg_id, self.node_path = json.loads(self.msg_data)
        pn = self.prev_node = self.node_path[-1]

        if self.msg_id in self.server.ss.msgs_box:
            self.curr_msg_attrs = self.server.ss.msgs_box[self.msg_id]
        else:
            self.curr_msg_attrs = self.server.ss.msgs_box[self.msg_id] = self._init_new_msg_attrs(self.msg_id)

        self.curr_msg_attrs["in_counts"][pn] += 1
        within_receive_limit = self.curr_msg_attrs["in_counts"][pn] <= RELAY_COUNTS
        is_first_reception   = self.msg_id not in self.server.ss.msgs_box

        if within_receive_limit or is_first_reception:
            self.node_path.append(self.server.ss.node_id)
            self._save_path_and_relay()

    def _send_client_msgs_data(self):
        status_type, paths_type = self.msg_data.split("|")

        # TODO: refactor below using structural pattern matching
        assert status_type in {"unread", "read", "all"}
        status_type_filter = {
            "unread": (True,),
            "read":   (False,),
            "all":    (True, False),
        }[status_type]

        msgs_data = {msg_id: GossipMessageHandler._filter_in_paths(msg_attrs["in_paths"], paths_type) for msg_id, msg_attrs
            in self.server.ss.msgs_box.items() if msg_attrs["is_unread"] in status_type_filter}
        self.wfile.write(bytes(json.dumps(msgs_data), "utf-8"))
        self._mark_msgs_as_read_on_get(status_type)

    def _get_peers_info(self):
        peers_info = [(p.id, f"{p.node_name} ({p.address})") for p in self.server.ss.peers]
        self.wfile.write(bytes(json.dumps(peers_info), "utf-8"))

    def _remove_peer(self):
        peer_id   = int(self.msg_data)
        peer_port = str(PORTS_ORIGIN + peer_id)
        self.server.ss.peers = [p for p in self.server.ss.peers if p.id != peer_id]
        self.server.ss.peer_addrs = [paddr for paddr in self.server.ss.peer_addrs if peer_port not in paddr]

    def _init_new_msg_attrs(self, msg_id):
        return {
            "in_paths":   [],
            "in_counts":  Counter({p.id: 0 for p in self.server.ss.peers}),
            "out_counts": Counter({p.id: 0 for p in self.server.ss.peers}),
            "is_unread":  True,
        }

    def _save_path_and_relay(self):
        self.curr_msg_attrs["in_paths"].append(self.node_path)
        self._relay_to_peers((self.msg_id, self.node_path))

    def _relay_to_peers(self, data):
        for p in self._get_peers_to_relay():
            if self.curr_msg_attrs["out_counts"][p.id] < RELAY_COUNTS:
                p.send_message(json.dumps(data), is_relay=True)
                self.curr_msg_attrs["out_counts"][p.id] += 1

    def _get_peers_to_relay(self):
        if self.cmd == "/NEW":
            return self.server.ss.peers
        elif self.cmd == "/RELAY":
            # filter out the preceeding node which relayed the current message to this node
            return [p for p in self.server.ss.peers if p.id != self.prev_node]
        else:
            raise Exception("this should never be reached!")

    def _mark_msgs_as_read_on_get(self, status_type):
        if status_type in {"unread", "all"}:
            for msg_attrs in self.server.ss.msgs_box.values():
                msg_attrs["is_unread"] = False

    @staticmethod
    def _filter_in_paths(in_paths_ls, paths_type):
        assert paths_type in {"both", "longest", "shortest", "all"}

        if paths_type == "all":
            return in_paths_ls

        max_hops = max(len(ps) for ps in in_paths_ls) if paths_type in {"both", "longest"} else None
        min_hops = min(len(ps) for ps in in_paths_ls) if paths_type in {"both", "shortest"} else None

        if paths_type == "both":
            return [pl for pl in in_paths_ls if len(pl) in {max_hops, min_hops}]
        elif paths_type == "longest":
            return [pl for pl in in_paths_ls if len(pl) == max_hops]
        elif paths_type == "shortest":
            return [pl for pl in in_paths_ls if len(pl) == min_hops]
        else:
            raise Exception("this should never be reached!")
