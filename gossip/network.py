from abc import ABC, abstractmethod
import networkx as nx


class GossipNetwork(ABC):

    def __init__(self, num_nodes):
        self.num_nodes = num_nodes
        self.G = self._get_network_graph()
        self.node_color = ""        # this is set in each subclass
        self.edge_color = "black"   # the default edge color to be used

    @abstractmethod
    def _get_network_graph(self):
        pass

    def get_peers_for_node(self, node_id):
        return self.G[node_id]

    def show_graph(self):
        import matplotlib.pyplot as plt
        nx.draw_networkx(self.G, node_color=self.node_color, **{"with_labels": True, "edge_color":  self._get_edge_colors(),})
        plt.show()

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

    def __init__(self, num_nodes):
        super().__init__(num_nodes)
        self.node_color = "cyan"

    def _get_network_graph(self):
        return nx.cycle_graph(range(1, self.num_nodes + 1))


class RandomRegularNetwork(GossipNetwork):

    def __init__(self, num_nodes, k_degrees):
        self.k_deg = k_degrees
        super().__init__(num_nodes)
        self.node_color = "yellow"
        self.edge_color, self.edge_cardinality = None, self.k_deg

    def _get_network_graph(self):
        G = nx.random_regular_graph(self.k_deg, self.num_nodes)
        nx.relabel_nodes(G, {0: self.num_nodes}, copy=False)
        return G


class PowerlawClusterNetwork(GossipNetwork):

    def __init__(self, num_nodes, m_edges=3, p_triangle=0.5):
        self.m_edges = m_edges
        self.p_triangle = p_triangle
        super().__init__(num_nodes)
        self.node_color = "lawngreen"
        self.edge_color, self.edge_cardinality = None, self.m_edges

    def _get_network_graph(self):
        G = nx.powerlaw_cluster_graph(self.num_nodes, self.m_edges, self.p_triangle)
        nx.relabel_nodes(G, {0: self.num_nodes}, copy=False)
        return G
