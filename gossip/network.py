from abc import ABC, abstractmethod
import networkx as nx


class GossipNetwork(ABC):

    def __init__(self, num_nodes):
        self.num_nodes = num_nodes
        self.nodes_ls = range(1, self.num_nodes + 1)
        self.network = self._get_network_graph()

    @abstractmethod
    def _get_network_graph(self):
        pass

    def get_peers_for_node(self, node_id):
        return self.network[node_id]


class CircularNetwork(GossipNetwork):

    def _get_network_graph(self):
        return nx.cycle_graph(self.nodes_ls)
