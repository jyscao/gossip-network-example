"""Gossip.

Usage:
  gossip start-network
  gossip stop-network
  gossip send-message <node-number> <message>
  gossip get-messages <node-number>
  gossip remove-node <node-number>
"""

import subprocess

from docopt import docopt

import gossip.server_pids as sp
from gossip.client import GossipClient
from gossip.constants import *


def get_port(node_number):
    return PORTS_ORIGIN + int(node_number)

def init_gossip_client(node_number):
    node_addr = f"{LOCALHOST}:{get_port(node_number)}"
    return GossipClient(node_addr)


def main():
    args = docopt(__doc__, version="Gossip 0.1")

    if args["start-network"]:
        subprocess.run(["python3 start-network.py"], shell=True)

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
        messages = client.get_messages()
        print(f"Fetched messages from {client}")
        for msg in messages:
            print(f"- {msg}")

    elif args["remove-node"]:
        node_number = args["<node-number>"]
        pids_map = sp.read_server_pids_to_map()
        node_pid = pids_map.pop(node_number)
        comp_proc = subprocess.run([f"kill {node_pid}"], shell=True)
        if comp_proc.returncode == 0:
            print(f"Gossip node {node_number} removed")
            sp.write_pids_map_to_file(pids_map)
        else:
            print(f"Failed to remove Gossip node {node_number}")


if __name__ == "__main__":
    main()
