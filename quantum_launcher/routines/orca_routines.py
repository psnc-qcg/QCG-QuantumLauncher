""" file with orca algorithms subclasses """
from typing import List, Literal
from ptseries.algorithms.binary_solvers import BinaryBosonicSolver
from ptseries.common.logger import Logger

from quantum_launcher.base import Problem, Algorithm, Result, Backend
from typing import Callable
import numpy as np


class OrcaBackend(Backend):
    """ local backend """

    def __init__(self, name: str) -> None:
        super().__init__(name)

    def get_args(self):
        return {}


class BBS(Algorithm):
    """
    Binary Bosonic Solver algorithm class.

    This class represents the Binary Bosonic Solver (BBS) algorithm. BBS is a quantum-inspired algorithm that
    solves optimization problems by mapping them onto a binary bosonic system. It uses a training process
    to find the optimal solution.

    Attributes:
    - learning_rate (float): The learning rate for the algorithm.
    - updates (int): The number of updates to perform during training.
    - tbi_loops (str): The type of TBI loops to use.
    - print_frequency (int): The frequency at which to print updates.
    - logger (Logger): The logger object for logging algorithm information.

    Methods:
    - __init__(self, learning_rate:float=1e-1, updates:int=80, tbi_loops:str='single-loop', print_frequency:int=20) -> None:
        Initialize the BBS algorithm.
    - run(self, problem: Problem, backend: OrcaBackend):
        Run the BBS algorithm.
    """
    _algorithm_format = 'qubo'

    def __init__(self, format: Literal['qubo', 'qubo_fn'] = 'qubo', **kwargs) -> None:
        super().__init__()
        self._algorithm_format = format
        self.kwargs = kwargs
        self.input_state = kwargs.get('input_state', None)

    def run(self, problem: Problem, backend: OrcaBackend, formatter: Callable[[Problem], np.ndarray]):
        # params = {"tbi_type": self.kwarga['tbi_type']}
        # if backend is not None:
        #     params.update(backend.get_args())
        objective = formatter(problem)
        # TODO: use offset somehow
        if not callable(objective):
            objective, offset = objective
            if self.input_state is None:
                self.input_state = [not i % 2 for i in range(len(objective))]
        self.bbs = BinaryBosonicSolver(
            len(self.input_state),
            objective,
            self.input_state,
            **self.kwargs
        )
        self.bbs.train(**self.kwargs)

        return self.construct_results(self.bbs)

    def get_bitstring(self, result: List[float]) -> str:
        return ''.join(map(str, map(int, result)))

    def construct_results(self, results: BinaryBosonicSolver) -> Result:
        # TODO: add support for distribution (probably with different logger)
        best_bitstring = ''.join(
            map(str, map(int, results.config_min_encountered)))
        best_energy = results.E_min_encountered
        most_common_bitstring = None
        most_common_bitstring_energy = None
        distribution = None
        energy = None
        num_of_samples = results.n_samples
        average_energy = None
        energy_std = None
        return Result(best_bitstring, best_energy, most_common_bitstring,
                      most_common_bitstring_energy, distribution, energy,
                      num_of_samples, average_energy, energy_std, results)
