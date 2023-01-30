from abc import ABC, abstractmethod
import networkx as nx


class GossipNetwork(ABC):

    def __init__(self, num_nodes):
        self.num_nodes = num_nodes
        self.nodes_ls = range(1, self.num_nodes + 1)
        self.G = self._get_network_graph()
        self.edge_color = "black"   # the default edge color to be used

    @abstractmethod
    def _get_network_graph(self):
        pass

    def get_peers_for_node(self, node_id):
        return self.G[node_id]  # this returns an AtlasView (read-only dict-of-dict data struct) object

    def show_graph(self):
        import matplotlib.pyplot as plt
        self._draw_network(**{"with_labels": True, "edge_color":  self._get_edge_colors(),})
        plt.show()

    @abstractmethod
    def _draw_network(self):
        pass

    def _get_edge_colors(self):
        if self.edge_color is not None:
            return self.edge_color
        else:
            palette = GossipNetwork._select_palette(self.edge_cardinality)
            mult, rem = divmod(len(self.G.edges), self.edge_cardinality)
            return palette * mult + palette[:rem]

    @staticmethod
    def _select_palette(cardinality: int):
        cc_scaler = 3   # color cardinality scale factor
        return ["tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple",
                "tab:brown", "tab:pink", "tab:gray", "tab:olive", "tab:cyan",][:3 * cardinality]


class CircularNetwork(GossipNetwork):

    def _get_network_graph(self):
        return nx.cycle_graph(self.nodes_ls)

    def _draw_network(self, **kwargs):
        nx.draw_circular(self.G, node_color="cyan", **kwargs)


class RandomRegularNetwork(GossipNetwork):

    def __init__(self, num_nodes, k_degrees):
        self.k_deg = k_degrees
        super().__init__(num_nodes)
        self.edge_color, self.edge_cardinality = None, self.k_deg

    def _get_network_graph(self):
        G = nx.random_regular_graph(self.k_deg, self.num_nodes)
        nx.relabel_nodes(G, {0: self.num_nodes}, copy=False)
        return G

    def _draw_network(self, **kwargs):
        nx.draw_networkx(self.G, node_color="yellow", **kwargs)


class PowerlawClusterNetwork(GossipNetwork):

    def __init__(self, num_nodes, m_edges=3, p_triangle=0.5):
        self.m_edges = m_edges
        self.p_triangle = p_triangle
        super().__init__(num_nodes)
        self.edge_color, self.edge_cardinality = None, self.m_edges

    def _get_network_graph(self):
        G = nx.powerlaw_cluster_graph(self.num_nodes, self.m_edges, self.p_triangle)
        nx.relabel_nodes(G, {0: self.num_nodes}, copy=False)
        return G

    def _draw_network(self, **kwargs):
        nx.draw_networkx(self.G, node_color="lawngreen", **kwargs)
