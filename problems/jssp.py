""" Job Shop Sheduling Problem """
from collections import defaultdict
from qiskit.quantum_info import SparsePauliOp
from job_shop_scheduler import get_jss_hamiltonian
from templates import Problem

class JSSP(Problem):
    """ Class for Job Shop Shedueling Problem """

    def __init__(self, max_time: int, onehot: str, optimization_problem: bool = False) -> None:
        super().__init__()
        self.name = 'jssp'
        self.max_time = max_time
        self.onehot = onehot
        self.optimization_problem = optimization_problem
        self.h_d, self.h_o, self.h_pos_by_label, self.h_label_by_pos = get_jss_hamiltonian(self.instance, max_time,
                                                                                           onehot)

        self.results = {'instance_name': self.instance_name,
                        'max_time': max_time,
                        'onehot': onehot,
                        'H_pos_by_label': self.h_pos_by_label,
                        'H_label_by_pos': self.h_label_by_pos}
        opt = 'optimization' if optimization_problem else 'decision'
        self.variant = opt
        self.opt = opt
        self._set_path()

    def set_instance(self, instance:dict[str, list[tuple[str, int]]],
                      instance_name:str | None= None) -> None:
        super().set_instance(instance, instance_name)
        self.results['instance_name'] = instance_name
        if instance is None:
            match instance_name:
                case 'toy':
                    self.instance = {"cupcakes": [("mixer", 2), ("oven", 1)],
                                    "smoothie": [("mixer", 1)],
                                    "lasagna": [("oven", 2)]}

    def read_instance(self, instance_path:str) -> None:
        self.instance_name = instance_path.rsplit('/',1)[1].split('.', 1)[0]     
        raw_instance = defaultdict(list)
        with open(instance_path, 'r', encoding='utf-8') as file_:
            file_.readline()
            for i, line in enumerate(file_):
                lint = list(map(int, line.split()))
                raw_instance[i + 1] = [x for x in
                                   zip(lint[::2],  # machines
                                       lint[1::2]  # operation lengths
                                       )]
        self.instance={k:[(m,1) if t<6 else (m,2) for m, t in v] for k, v in raw_instance.items()}

    def _set_path(self) -> None:
        self.path = f'{self.name}/{self.instance_name}@{self.max_time}@{self.opt}@{self.onehot}'

    def get_qiskit_hamiltonian(self, optimization_problem: bool = None) -> SparsePauliOp:
        if optimization_problem is None:
            optimization_problem = self.optimization_problem

        if optimization_problem:
            return self.h_o
        else:
            return self.h_d
