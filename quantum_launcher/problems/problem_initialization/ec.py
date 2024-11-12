"""  This module contains the EC class."""
import ast

from quantum_launcher.base import Problem


class EC(Problem):
    """
    Class for exact cover problem.

    The exact cover problem is a combinatorial optimization problem that involves finding a subset of a given set
    of elements such that the subset covers all elements and the number of elements in the subset is minimized.
    The class contains an instance of the problem, so it can be passed into Quantum Launcher.

    Attributes:
        onehot (str): The one-hot encoding used for the problem.
        instance (any): The instance of the problem.
        instance_name (str | None): The name of the instance.
        instance_path (str): The path to the instance file.

    Methods:
        set_instance: Sets the instance of the problem.
        read_instance: Reads the instance from a file.

    """

    def __init__(self, onehot: str, instance: any = None,
                 instance_name: str | None = None, instance_path: str = None) -> None:
        super().__init__(instance=instance, instance_name=instance_name,
                         instance_path=instance_path)
        self.onehot = onehot

    @property
    def setup(self) -> dict:
        return {
            'onehot': self.onehot,
            'instance_name': self.instance_name
        }

    def _get_path(self) -> str:
        return f'{self.name}@{self.instance_name}@{self.onehot}'

    def set_instance(self, instance: any, instance_name: str | None = None):
        super().set_instance(instance, instance_name)
        if instance is None:
            match instance_name:
                case 'micro':
                    self.instance = [{1, 2},
                                     {1}]
                case 'toy':
                    self.instance = [{1, 4, 7},
                                     {1, 4},
                                     {4, 5, 7},
                                     {3, 5, 6},
                                     {2, 3, 6, 7},
                                     {2, 7}]

    def read_instance(self, instance_path: str):
        with open(instance_path, 'r', encoding='utf-8') as file:
            read_file = file.read()
        self.instance = ast.literal_eval(read_file)
