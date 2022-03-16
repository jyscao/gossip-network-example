import os
import multiprocessing as mp

import gossip.server_pids as sp
from gossip.server import GossipServer

LOCALHOST = "127.0.0.1"
NUM_NODES = 16


def get_left_peer(node_id, num_nodes):
    return num_nodes if node_id == 1 else node_id - 1


def get_right_peer(node_id, num_nodes):
    return 1 if node_id == num_nodes else node_id + 1


def generate_peer_name(own_node_id, num_nodes, peer_id_getter):
    peer_node_id = peer_id_getter(own_node_id, num_nodes)
    peer_port    = 7000 + peer_node_id
    # TODO: generate more readable/distinctive peer names
    return f"{LOCALHOST}:{peer_port}"


def get_initial_peers(node_id, port, num_nodes):
    return [generate_peer_name(node_id, num_nodes, get_left_peer), generate_peer_name(node_id, num_nodes, get_right_peer)]


def start_server(node_id, num_nodes):
    port = 7000 + node_id
    peers = get_initial_peers(node_id, port, num_nodes)
    server = GossipServer(node_id, port, peers)
    server.start()


if __name__ == "__main__":
    pids_map = {0: os.getpid()}    # "0" will be used to denote this parent Python process

    srv_procs = [mp.Process(target=start_server, args=(node_id, NUM_NODES)) for node_id in range(1, NUM_NODES + 1)]
    for node_id, proc in enumerate(srv_procs, start=1):
        proc.start()
        pids_map[node_id] = proc.pid

    sp.write_pids_map_to_file(pids_map)

    for proc in srv_procs:
        proc.join()
