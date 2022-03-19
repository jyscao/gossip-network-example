import sys
import multiprocessing as mp

import gossip.server_pids as sp
from gossip.server import GossipServer
from gossip.network import CircularNetwork, RandomKdegNetwork
from gossip.constants import *


gn_addr = lambda n: f"{LOCALHOST}:{PORTS_ORIGIN + n}"

def get_peer_addrs(peer_ids):
    return [gn_addr(p) for p in peer_ids]


def start_server(network_graph, node_id):
    peer_ids = network_graph.get_peers_for_node(node_id)
    peer_addrs = get_peer_addrs(peer_ids)

    server = GossipServer(gn_addr(node_id), peer_addrs)
    server.start()

def get_network(network_type):
    return {
        "circular": (CircularNetwork, (NUM_NODES,)),
        "random":   (RandomKdegNetwork, (NUM_NODES, 3)),
    }[network_type]


if __name__ == "__main__":
    NetworkCls, ncls_args = get_network(sys.argv[1])
    network = NetworkCls(*ncls_args)

    pids_map = {}
    srv_procs = [mp.Process(target=start_server, args=(network, node_id)) for node_id in network.network.nodes]
    for node_id, proc in enumerate(srv_procs, start=1):
        proc.start()
        pids_map[node_id] = proc.pid

    sp.write_pids_map_to_file(pids_map)

    for proc in srv_procs:
        proc.join()
