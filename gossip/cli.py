"""Gossip.

Usage:
  gossip start-network [circular | powerlaw | random [<degree>]] [-n <nn>] [-p]
  gossip stop-network
  gossip send-message <node-number> <message>
  gossip get-messages <node-number> [unread | read | all] [-t...]
  gossip remove-node <node-number>
  gossip list-peers <node-number>

--Options:
  -n <nn>, --num-nodes <nn>    Number of nodes to initialize the Gossip Network with [default: 16]
  -p, --plot                   Plot the network graph on start-network (requires matplotlib)
  -t, --time                   Display the times when each message was received by the network

  <degree>      The degree of connectedness for each node in a random regular graph [default: 3]
"""

import subprocess, time
from docopt import docopt

import gossip.server_pids as sp
from gossip.start_network import start_network
from gossip.client import GossipClient
from gossip.constants import *


def get_port(node_number):
    return PORTS_ORIGIN + int(node_number)

def init_gossip_client(node_number):
    node_addr = f"{LOCALHOST}:{get_port(node_number)}"
    return GossipClient(node_addr)

def get_network_type(docopt_args_dict):
    if docopt_args_dict["circular"]:
        return "circular"
    elif docopt_args_dict["powerlaw"]:
        return "powerlaw"
    else:
        return "random"

def get_msgs_status_type(docopt_args_dict):
    if docopt_args_dict["unread"]:
        return "unread"
    elif docopt_args_dict["read"]:
        return "read"
    else:
        return "all"

def format_msg_w_time(docopt_args_dict, msg_ts_tup):
    msg, ts_ns = msg_ts_tup
    # TODO: refactor this using structural pattern matching
    if docopt_args_dict["--time"] >= 3:
        time_display_format = "%b %d, %Y - %H:%M:%S (UTC%z)"
        timestamp = time.strftime(time_display_format, time.localtime(int(ts_ns) // 1e9))
        return f"{timestamp}: {msg}"
    elif docopt_args_dict["--time"] == 2:
        time_display_format = "%H:%M:%S - %d/%m/%Y"
        timestamp = time.strftime(time_display_format, time.localtime(int(ts_ns) // 1e9))
        return f"{msg} [{timestamp}]"
    elif docopt_args_dict["--time"] == 1:
        timestamp = time.strftime("%H:%M:%S", time.localtime(int(ts_ns) // 1e9))
        return f"{msg} [{timestamp}]"
    elif docopt_args_dict["--time"] == 0:
        return msg
    else:
        raise Exception("this should never be reached!")


def main():
    args = docopt(__doc__, version="Gossip 0.1")

    if args["start-network"]:
        num_nodes = int(args["--num-nodes"])
        network_type = get_network_type(args)
        random_k_deg = int(args["<degree>"]) if args["<degree>"] else 3
        start_network(network_type, num_nodes, random_k_deg, args["--plot"])

    elif args["stop-network"]:
        pids_ls_str = " ".join(str(pid) for pid in sp.read_server_pids_to_map().values())
        comp_proc = subprocess.run([f"echo {pids_ls_str} | xargs -n1 -I% kill %"], shell=True)
        if comp_proc.returncode == 0:
            print("Gossip network stopped")
            sp.write_pids_map_to_file({})
        else:
            print("Gossip network stopping failed")

    elif args["send-message"]:
        message = args["<message>"]
        client = init_gossip_client(args["<node-number>"])
        client.send_message(message)
        print(f"Message sent to {client}")

    elif args["get-messages"]:
        client = init_gossip_client(args["<node-number>"])
        msgs_status_type = get_msgs_status_type(args)
        msgs_data = client.get_messages(msgs_status_type)
        print(f"Fetched {msgs_status_type} messages from {client}")
        for msg_ts_tup, msg_paths in msgs_data.items():
            print()
            print(f"• {format_msg_w_time(args, msg_ts_tup)}")
            for mp in msg_paths:
                print(f"  ↳ {mp}")

    elif args["remove-node"]:
        node_number = args["<node-number>"]
        client = init_gossip_client(node_number)
        peer_ids = client.get_peers_info(get_ids=True)

        pids_map = sp.read_server_pids_to_map()
        node_pid = pids_map.pop(node_number)
        comp_proc = subprocess.run([f"kill {node_pid}"], shell=True)

        if comp_proc.returncode == 0:
            for p in peer_ids:
                init_gossip_client(p).remove_peer(node_number)
            print(f"Gossip node {node_number} removed")
            sp.write_pids_map_to_file(pids_map)
        else:
            print(f"Failed to remove Gossip node {node_number}")

    elif args["list-peers"]:
        client = init_gossip_client(args["<node-number>"])
        peer_names = client.get_peers_info(get_names=True)
        print(f"{client} has peers:")
        for pn in peer_names:
            print(f"* {pn}")

    else:
        raise Exception("this should never be reached!")


if __name__ == "__main__":
    main()
