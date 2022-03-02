import os
import multiprocessing as mp

import gossip.server_pids as sp
from gossip.server import GossipServer

PROJECT = "gossip"
SERVICE = "node"
NUM_NODES = 16


def generate_hostname(project, service, index):
    return f"{project}_{service}_{index}_1"


def get_left_peer(node_id, num_nodes):
    return num_nodes if node_id == 1 else node_id - 1


def get_right_peer(node_id, num_nodes):
    return 1 if node_id == num_nodes else node_id + 1


def get_initial_peers(node_id, port, num_nodes):
    node_l, node_r = get_left_peer(node_id, num_nodes), get_right_peer(node_id, num_nodes)
    port_l, port_r = 7000 + node_l, 7000 + node_r
    peer_l = f"{generate_hostname(PROJECT, SERVICE, node_l)}:{port_l}"
    peer_r = f"{generate_hostname(PROJECT, SERVICE, node_r)}:{port_r}"
    return [peer_l, peer_r]


def start_server(node_id):
    port = 7000 + node_id
    peers = get_initial_peers(node_id, port, NUM_NODES)
    server = GossipServer(node_id, port, peers)
    server.start()


if __name__ == "__main__":
    pids_map = {0: os.getpid()}    # "0" will be used to denote this parent Python process

    srv_procs = [mp.Process(target=start_server, args=(node_id,)) for node_id in range(1, NUM_NODES + 1)]
    for node_id, proc in enumerate(srv_procs, start=1):
        proc.start()
        pids_map[node_id] = proc.pid

    sp.write_pids_map_to_file(pids_map)

    for proc in srv_procs:
        proc.join()
