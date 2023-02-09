# Gossip Network Example

This is an example of a simple peer-to-peer network of servers that
communicate with each other using a gossip protocol. Where a message submitted
to a single node is eventually received by **all nodes** in the network.



## Project Setup

To run this on your own computer, all you need are Python 3.9+ and basic Unix
tooling (specifically `kill` & `xargs`).

The project's Python dependencies are managed using [Poetry](https://python-poetry.org/),
which you may install yourself manually; or as I prefer, using an environment
manager such as [Conda](https://docs.conda.io/en/latest/).

After cloning this repo, setting up your Python environment (with poetry), you
can use install the Python dependencies with:

```bash
poetry install
```



## Commands

All interactions with the network take place through a simple CLI. To see the
full usage details of the CLI, run:

```bash
poetry run gossip -h
```

### start-network

The `start-network` command spins up a network of 16 nodes (by default) using
Python's `multiprocessing` module. Each node runs as a separate Python process
and is exposed at a unique port number ranging from 7001-7016. The default
*random network* starts with 3 neighbors assinged to each node.

**Example usages:**

```bash
# start the default random network, and plot its topology
poetry run gossip start-network --plot

# start a random network where all nodes have 5 neighboring connections
poetry run gossip start-network random 5

# start a circularly connected network with 32 nodes
poetry run gossip start-network circular --num-nodes=32
```

### stop-network

The `stop-network` command stops all nodes running in the network.

**Usage:**

```
poetry run gossip stop-network
```

### send-message

The `send-message` command sends a message to a node in the network after it
has been started with `start-network`.

**Example usages:**

```bash
# Send the message "apple" to node 4
poetry run gossip send-message 4 apple

# Send the message "banana" to node 8, where each node broadcasts the message
# 3× to its neighbors
poetry run gossip send-message 8 banana --relays=3
```

### get-messages

The `get-messages` command returns messages that have been received by a
single node.

**Example usages:**

```bash
# Get all messages received by node 8
poetry run gossip get-messages 8

# Get only unread messages received by node 3
poetry run gossip get-messages 3 unread

# Get only read messages received by node 3, along with their received times,
# showing the shortest path taken
poetry run gossip get-messages 3 read -p --time
```

### remove-node

The `remove-node` command stops a single node in the network.

**Example usage:**

```bash
# Stop node 9
poetry run gossip remove-node 9
```

### list-peers

The `list-peers` command displays all peers for a single node in the network.

**Example usage:**

```bash
# List the peers for node 5
poetry run gossip list-peers 5
```



## Status

This project is created strictly for self educational, with no practical
utilities, nor commitments to further development.

See my [blog post]() for a detailed walkthrough.
