# Gossip Network Assignment

## Introduction

The goal of this assignment is to build a simple peer-to-peer network of servers that communicate with each other using a gossip protocol.

## Requirements

- The network must support up to 16 individual servers (nodes) running simultaneously.
- At any given time, each node can only have knowledge of 3 other nodes in the network.
- At minimum, each node must provide two API methods:

```py
def submit_message(message: str) -> None:
    """Handle an incoming message."""

def get_messages() -> List[str]:
    """Returns a list of all messages since this node started.

    Each message should include the path it followed to reach this node.
    
    Example output:
    - Apple (Node 1 -> Node 8 -> Node 10)
    - Banana (Node 3 -> Node 5 -> Node 10)
    - Orange (Node 7 -> Node 15 -> Node 9 -> Node 10)
    """
```
- A message submitted to a single node should eventually be received by **all nodes** in the network.
- Nodes can only communicate with each other through network calls (not in-process function calls). The actual networking protocol is up to you, so feel free to choose between TCP, UDP, HTTP, etc.
- Your solution must be implemented in Python.

## Installation

This assignment requires you to have Python 3.7 and basic Unix tooling installed on your system. If you don't already have Python, please follow the instructions below:

- [Python setup instructions](https://docs.python.org/3/using/index.html)
- Basic Unix command line tools (specifically `kill` & `xargs`) are available by default on Linux and macOS, as well as on Windows through WSL or MinGW.

### Project setup

This codebase uses [Poetry](https://poetry.eustace.io/) to manage the Python environment and dependencies. Poetry can be installed on most systems with the following command:

```bash
curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python
```

After cloning this repo, you can use Poetry to install the dependencies:

```bash
poetry install
```

## Getting started

We have provided you with a basic template to help you get started on this assignment. This template contains a skeleton Python project.

*__Important__: Although it's encouraged, you are not required to use the provided starter code. Feel free to start from scratch if you don't find it useful.*

**GossipClient**

The [GossipClient](gossip/client.py) class is a stub implementation of the client interface for a node. It should be able to make network calls to a `GossipServer`.

A `GossipClient` instance is initialized with the address of a node.

**GossipServer**

The [GossipServer](gossip/server.py) class is a stub implementation of a node's server. It should be able to respond to network calls made by a `GossipClient`.

## Commands

We have provided you with a simple CLI to test your solution. 

### start-network

The `start-network` command spins up a network of 16 nodes using Python's `multiprocessing` module. Each node runs as a separate Python process and is exposed at a unique port number ranging from 7001-7016.

Each node is initialized with the addresses of two other peers in the network. This creates a simple network topology, but you are encouraged to find more optimal structures.

**Example usage:**

```
poetry run gossip start-network
```

### stop-network

The `stop-network` command stops any nodes currently running in the test network.

**Example usage:**

```
poetry run gossip stop-network
```

### send-message

The `send-message` command can be used to send a message to a node in the network. This command should only be used after the network has been started with `start-network`.

**Arguments:**

- `node-number`: The node number to connect to. Must be between 1-16.
- `message`: The message to send. Must be a single phrase with no spaces.

**Example usage:**

```bash
# Send the message "apple" to node 4
poetry run gossip send-message 4 apple
```

### get-messages

The `get-messages` command returns all messages that have been received by a single node.

**Arguments:**

- `node-number`: The node number to connect to. Must be between 1-16.

**Example usage:**

```bash
# Get all messages received by node 8
poetry run gossip get-messages 8
```

### remove-node

The `remove-node` command stops a single node in the network.

**Arguments:**

- `node-number`: The node number to remove. Must be between 1-16.

**Example usage:**

```bash
# Stop node 9
poetry run gossip remove-node 9
```

## FAQ

**Can I make use of third-party libraries?**

Yes, you may use any third-party library. In this project you can add Python packages to the project with `poetry add <package-name>`.

**How will this assignment be assessed?**

Your solution should demonstrate the key components of a robust distributed system. While the code itself should be clean and readable, your solution will be evaluated based on its functionality.
