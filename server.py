import os
import multiprocessing as mp

from gossip.server import GossipServer

PROJECT = "gossip"
SERVICE = "node"
NUM_NODES = 16


def generate_hostname(project, service, index):
    return "{project}_{service}_{index}_1".format(
        project=project, service=service, index=index
    )


def get_left_peer(node_id, num_nodes):
    if node_id == 1:
        return num_nodes

    return node_id - 1


def get_right_peer(node_id, num_nodes):
    if node_id == num_nodes:
        return 1

    return node_id + 1


def get_initial_peers(node_id, port, num_nodes):

    peer_a = (
        generate_hostname(PROJECT, SERVICE, get_left_peer(node_id, num_nodes))
        + f":{port}"
    )
    peer_b = (
        generate_hostname(PROJECT, SERVICE, get_right_peer(node_id, num_nodes))
        + f":{port}"
    )

    return [peer_a, peer_b]


def start_server(node_id):
    port = 7000 + node_id
    peers = get_initial_peers(node_id, port, NUM_NODES)
    server = GossipServer(node_id, port, peers)
    server.start()


if __name__ == "__main__":
    pid_map = {0: os.getpid()}    # "0" will be used to denote this parent Python process

    srv_procs = [mp.Process(target=start_server, args=(node_id,)) for node_id in range(1, NUM_NODES+1)]
    for node_id, proc in enumerate(srv_procs):
        proc.start()
        pid_map[node_id] = proc.pid

    for proc in srv_procs:
        proc.join()
