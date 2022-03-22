import socket, json

from gossip.constants import PORTS_ORIGIN


class GossipClient:
    """A client interface to connect to a server in a peer-to-peer gossip network."""

    def __init__(self, address):
        self.address = address
        host, port = self.address.split(":")
        self.host_port_tup = (host, int(port))
        self.id = int(port) - PORTS_ORIGIN
        self.node_name = f"Gossip-Node-{self.id}"

    def __repr__(self):
        return self.node_name

    def send_message(self, message, is_relay=False, relay_limit=1):
        """Send a message to the current server."""
        cmd = "/RELAY" if is_relay else "/NEW"
        self._send_to_server(f"{cmd}:{relay_limit}|{message}")

    @staticmethod
    def _parse_msg_id(msg_id: str):
        if msg_id.count("_") == 1:
            msg, ts = msg_id.split("_")
        else:
            time_rev, msg_rev = msg_id[::-1].split("_", maxsplit=1)     # reversing the ID then splitting at most once on '_' allows message to contain underscores
            msg, ts = msg_rev[::-1], time_rev[::-1]
        return msg, int(ts)

    def get_messages(self, msgs_status_type, msgs_paths_type):
        """Fetch a list of all messages stored by the current server."""
        cmd_data = f"{msgs_status_type}|{msgs_paths_type}"
        msgs_data = self._send_to_then_get_from_server(f"/GET:{cmd_data}\n")
        return {GossipClient._parse_msg_id(msg_id): [' ➜ '.join(str(n) for n in nodes) for nodes in msg_paths]
            for msg_id, msg_paths in msgs_data.items()}

    def get_peers_info(self, get_ids=False, get_names=False):
        """Fetch the list of peers connected to the current server."""
        peer_ids, peer_names = zip(*self._send_to_then_get_from_server("/PEERS:\n"))

        if get_ids and get_names:
            return peer_ids, peer_names
        elif get_ids:
            return peer_ids
        elif get_names:
            return peer_names
        else:
            raise Exception("must fetch either peer IDs or peer names")

    def remove_peer(self, node_id):
        """Remove the given node as a peer from the current server."""
        self._send_to_server(f"/REMOVE:{node_id}\n")

    def _send_to_server(self, cmd_data):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            self._send_to_socket(sock, cmd_data)

    def _send_to_then_get_from_server(self, cmd_data):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            self._send_to_socket(sock, cmd_data)
            response = self._recv_server_full_response(sock)
        return response

    def _send_to_socket(self, sock, cmd_data):
        sock.connect(self.host_port_tup)
        sock.send(bytes(cmd_data, "utf-8"))

    def _recv_server_full_response(self, sock):
        response_ls = []
        while True:
            received = str(sock.recv(1024), "utf-8")
            if received == "":
                break
            response_ls.append(received)
        return json.loads("".join(response_ls))
