from abc import ABC, abstractmethod
import networkx as nx


class GossipNetwork(ABC):

    def __init__(self, num_nodes):
        self.num_nodes = num_nodes
        self.nodes_ls = range(1, self.num_nodes + 1)
        self.G = self._get_network_graph()

    @abstractmethod
    def _get_network_graph(self):
        pass

    def get_peers_for_node(self, node_id):
        return self.G[node_id]

    @abstractmethod
    def _draw_network(self):
        pass

    def show_graph(self):
        import matplotlib.pyplot as plt
        self._draw_network()
        plt.show()


class CircularNetwork(GossipNetwork):

    def _get_network_graph(self):
        return nx.cycle_graph(self.nodes_ls)

    def _draw_network(self):
        nx.draw_circular(self.G, with_labels=True, node_color="yellow")


class RandomRegularNetwork(GossipNetwork):

    def __init__(self, num_nodes, k_degrees):
        self.k_deg = k_degrees
        super().__init__(num_nodes)

    def _get_network_graph(self):
        G = nx.random_regular_graph(self.k_deg, self.num_nodes)
        nx.relabel_nodes(G, {0: self.num_nodes}, copy=False)
        return G

    def _draw_network(self):
        nx.draw_networkx(self.G, with_labels=True, node_color="cyan")


class PowerlawClusterNetwork(GossipNetwork):

    def __init__(self, num_nodes, m_edges=3, p_triangle=0.5):
        self.m_edges = m_edges
        self.p_triangle = p_triangle
        super().__init__(num_nodes)

    def _get_network_graph(self):
        G = nx.powerlaw_cluster_graph(self.num_nodes, self.m_edges, self.p_triangle)
        nx.relabel_nodes(G, {0: self.num_nodes}, copy=False)
        return G

    def _draw_network(self):
        nx.draw_networkx(self.G, with_labels=True, node_color="pink")
