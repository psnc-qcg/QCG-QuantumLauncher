"""  This module contains the MaxCut class."""
import networkx as nx

from base import Problem


class MaxCut(Problem):
    """ 
    Class for MaxCut Problem.

    This class represents MaxCut Problem which is a combinatorial optimization problem that involves partitioning the
    vertices of a graph into two sets such that the number of edges between the two sets is maximized. The class contains
    an instance of the problem, so it can be passed into Quantum Launcher.

    Attributes:
        instance (nx.Graph): The graph instance representing the problem.
        instance_name (str): The name of the instance.
        instance_path (str): The path to the instance.

    Methods:
        set_instance: Sets the instance of the problem.
        read_instance: Reads the instance from a file.
    """

    def __init__(self, instance: nx.Graph | None = None, instance_name: str | None = None,
                 instance_path: str | None = None) -> None:
        super().__init__(instance=instance, instance_name=instance_name,
                         instance_path=instance_path)

    @property
    def setup(self) -> dict:
        return {
            'instance_name': self.instance_name
        }

    def set_instance(self, instance: None = None, instance_name: str | None = None) -> None:
        super().set_instance(instance, instance_name)
        if instance is None:
            match instance_name:
                case 'default':
                    self.instance = nx.Graph()
                    edge_list = [(0, 1), (0, 2), (0, 5), (1, 3), (1, 4),
                                 (2, 4), (2, 5), (3, 4), (3, 5)]
                    self.instance.add_edges_from(edge_list)

    def _get_path(self) -> str:
        return f'{self.name}@{self.instance_name}'

    def visualize(self):
        import matplotlib.pyplot as plt
        pos = nx.spring_layout(self.instance)
        plt.figure(figsize=(8, 6))

        nx.draw(self.instance, pos, with_labels=True, node_color='skyblue',
                node_size=500, edge_color='gray', font_size=10, font_weight='bold')
        plt.title("Max-Cut Problem Instance Visualization")
        plt.show()

    @staticmethod
    def generate_maxcut_instance(num_vertices, edge_probability):
        G = nx.gnp_random_graph(num_vertices, edge_probability)
        return G
