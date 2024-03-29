from abc import ABC, abstractmethod
import networkx as nx


class GossipNetwork(ABC):

    def __init__(self, num_nodes):
        self.num_nodes = num_nodes
        self.G = self._get_network_graph()
        nx.relabel_nodes(self.G, {0: self.num_nodes}, copy=False)   # change graph to be 1-indexed
        self.edge_color = "black"   # the default edge color to be used

    @abstractmethod
    def _get_network_graph(self):
        pass

    def get_peers_for_node(self, node_id):
        return self.G[node_id]  # this returns an AtlasView (read-only dict-of-dict data struct) object

    def show_graph(self):
        import matplotlib.pyplot as plt
        self._draw_network()
        plt.show()

    def _draw_network(self):
        nx.draw_networkx(self.G)

    def _get_dynamic_edge_colors(self):
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
        return nx.cycle_graph(range(self.num_nodes))

    def _draw_network(self):
        nx.draw_circular(self.G, with_labels=True, node_color="cyan", edge_color="black")


class RandomRegularNetwork(GossipNetwork):

    def __init__(self, num_nodes, k_degrees):
        self.k_deg = self.edge_cardinality = k_degrees
        super().__init__(num_nodes)

    def _get_network_graph(self):
        return nx.random_regular_graph(self.k_deg, self.num_nodes)

    def _draw_network(self):
        nx.draw_networkx(self.G, node_color="yellow", edge_color=self._get_dynamic_edge_colors())


class PowerlawClusterNetwork(GossipNetwork):

    def __init__(self, num_nodes, m_edges=3, p_triangle=0.5):
        self.m_edges = self.edge_cardinality = m_edges
        self.p_triangle = p_triangle
        super().__init__(num_nodes)

    def _get_network_graph(self):
        return nx.powerlaw_cluster_graph(self.num_nodes, self.m_edges, self.p_triangle)

    def _draw_network(self):
        pos = nx.shell_layout(self.G)
        nx.draw_networkx(self.G, pos=pos, node_color="lawngreen", edge_color=self._get_dynamic_edge_colors())
