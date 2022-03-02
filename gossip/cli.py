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

from gossip.client import GossipClient

LOCALHOST = "127.0.0.1"


def get_port(node_number):
    return 7000 + int(node_number)


def main():
    args = docopt(__doc__, version="Gossip 0.1")

    run_srv_cmd = "python3 server.py"

    if args["start-network"]:
        subprocess.run([run_srv_cmd], shell=True)
    elif args["stop-network"]:
        subprocess.run(["docker-compose down"], shell=True)
    elif args["send-message"]:
        node_number = args["<node-number>"]
        port = get_port(node_number)
        address = f"{LOCALHOST}:{port}"

        message = args["<message>"]

        client = GossipClient(address)
        client.send_message(message)

        print(f"Message sent to {address}")
    elif args["get-messages"]:
        node_number = args["<node-number>"]
        port = get_port(node_number)
        address = f"{LOCALHOST}:{port}"

        client = GossipClient(address)
        messages = client.get_messages()

        print(f"Fetched messages from {address}")
        for message in messages:
            print(f"- {message}")
    elif args["remove-node"]:
        node_number = args["<node-number>"]
        container_name = f"gossip_node_{node_number}_1"
        subprocess.run([f"docker kill {container_name}"], shell=True)


if __name__ == "__main__":
    main()
