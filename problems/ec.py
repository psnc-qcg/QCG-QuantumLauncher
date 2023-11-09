""" Exact Cover Problem """
import ast

from templates import Problem


class EC(Problem):
    """ Class for exact cover problem """

    def __init__(self, onehot: str, instance: any = None,
                 instance_name: str | None = None, instance_path: str = None) -> None:
        super().__init__(instance=instance, instance_name=instance_name,
                         instance_path=instance_path)
        self.name = 'ec'
        self.onehot = onehot

    @property
    def setup(self) -> dict:
        return {
            'onehot':self.onehot,
            'instance_name':self.instance_name
        }

    def _get_path(self) -> str:
        return f'{self.name}/{self.instance_name}@{self.onehot}'

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
