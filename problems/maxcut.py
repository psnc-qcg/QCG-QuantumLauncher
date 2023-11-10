""" Max Cut Problem """
import networkx as nx

from templates import Problem


class MaxCut(Problem):
    """ MacCut for Orca """

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
        return f'{self.name}/{self.instance_name}'
