import sys
import multiprocessing as mp

import gossip.server_pids as sp
from gossip.server import GossipServer
from gossip.network import *
from gossip.constants import *


gn_addr = lambda n: f"{LOCALHOST}:{PORTS_ORIGIN + n}"

def get_peer_addrs(peer_ids):
    return [gn_addr(p) for p in peer_ids]


def start_server(network_graph, node_id):
    peer_ids = network_graph.get_peers_for_node(node_id)
    peer_addrs = get_peer_addrs(peer_ids)

    server = GossipServer(gn_addr(node_id), peer_addrs)
    server.start()


def get_network(network_type, num_nodes, extra_graph_params):
    random_k_deg = extra_graph_params.pop("random_k_deg")
    if network_type == "random":
        assert random_k_deg is not None
        assert num_nodes * random_k_deg % 2 == 0, "(num-nodes × degree) must be an even number for a regular graph"

    return {
        "circular": (CircularNetwork,        (num_nodes,)),
        "random":   (RandomRegularNetwork,   (num_nodes, random_k_deg)),
        "powerlaw": (PowerlawClusterNetwork, (num_nodes,)),
    }[network_type]


def plot_network(network, pids_map):    # plt.show() in separate process as to not block servers
    plt_proc = mp.Process(target=network.show_graph, args=())
    plt_proc.start()
    pids_map["plot"] = plt_proc.pid
    return plt_proc


def start_network(network_type, num_nodes, extra_graph_params=None, plot=False):
    if extra_graph_params is None:  # TODO: can remove this check after adding type hints
        extra_graph_params = {"random_k_deg": None}
    NetworkCls, ncls_args = get_network(network_type, num_nodes, extra_graph_params)
    network = NetworkCls(*ncls_args)

    pids_map = {}
    subprocs = {node_id: mp.Process(target=start_server, args=(network, node_id)) for node_id in network.G.nodes}
    for node_id, proc in subprocs.items():
        proc.start()
        pids_map[node_id] = proc.pid

    if plot:
        plt_proc = plot_network(network, pids_map)

    sp.write_pids_map_to_file(pids_map)
    for proc in subprocs.values():
        proc.join()
