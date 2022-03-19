import os
import multiprocessing as mp

import gossip.server_pids as sp
from gossip.server import GossipServer
from gossip.network import CircularNetwork
from gossip.constants import *


def get_peer_addrs(peer_ids):
    g_p = lambda p: f"{LOCALHOST}:{PORTS_ORIGIN + p}"
    return [g_p(p) for p in peer_ids]


def start_server(network_graph, node_id):
    port = PORTS_ORIGIN + node_id

    peer_ids = network_graph.get_peers_for_node(node_id)
    peer_addrs = get_peer_addrs(peer_ids)

    server = GossipServer(node_id, port, peer_addrs)
    server.start()


if __name__ == "__main__":
    network = CircularNetwork(NUM_NODES)
    pids_map = {0: os.getpid()}    # "0" will be used to denote this parent Python process

    srv_procs = [mp.Process(target=start_server, args=(network, node_id)) for node_id in network.network.nodes]
    for node_id, proc in enumerate(srv_procs, start=1):
        proc.start()
        pids_map[node_id] = proc.pid

    sp.write_pids_map_to_file(pids_map)

    for proc in srv_procs:
        proc.join()
