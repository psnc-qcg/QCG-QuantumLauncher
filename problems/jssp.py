""" Job Shop Sheduling Problem """
from collections import defaultdict

from jssp.qiskit_scheduler import get_jss_hamiltonian
from templates import Problem


class JSSP(Problem):
    """ Ckass for Job Shop Shedueling Problem """

    def __init__(self, max_time: int, onehot: str, instance: any = None,
                 instance_name: str | None = None, instance_path: str | None = None,
                 optimization_problem: bool = False) -> None:
        super().__init__(instance=instance, instance_name=instance_name,
                         instance_path=instance_path)
        self.max_time = max_time
        self.onehot = onehot
        self.optimization_problem = optimization_problem

        self.h_d, self.h_o, self.h_pos_by_label, self.h_label_by_pos = get_jss_hamiltonian(self.instance, max_time,
                                                                                           onehot)

        self.results = {'instance_name': instance_name,
                        'max_time': max_time,
                        'onehot': onehot,
                        'H_pos_by_label': self.h_pos_by_label,
                        'H_label_by_pos': self.h_label_by_pos}
        opt = 'optimization' if optimization_problem else 'decision'
        self.variant = opt
        self.opt = opt

    @property
    def setup(self) -> dict:
        return {
            'max_time': self.max_time,
            'onehot': self.onehot,
            'optimization_problem': self.optimization_problem,
            'instance_name': self.instance_name
        }

    def _get_path(self) -> str:
        return f'{self.name}@{self.instance_name}@{self.max_time}@{self.opt}@{self.onehot}'

    def set_instance(self, instance: any, instance_name: str | None = None):
        super().set_instance(instance, instance_name)
        if instance is None:
            match instance_name:
                case 'toy':
                    self.instance = {"cupcakes": [("mixer", 2), ("oven", 1)],
                                     "smoothie": [("mixer", 1)],
                                     "lasagna": [("oven", 2)]}

    def read_instance(self, instance_path: str):
        """ Sth """
        job_dict = defaultdict(list)
        with open(instance_path, 'r', encoding='utf-8') as file_:
            file_.readline()
            for i, line in enumerate(file_):
                lint = list(map(int, line.split()))
                job_dict[i + 1] = [x for x in
                                   zip(lint[::2],  # machines
                                       lint[1::2]  # operation lengths
                                       )]
        self.instance = job_dict
