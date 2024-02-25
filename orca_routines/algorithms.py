""" file with orca algorithms subclasses """

from ptseries.algorithms.binary_solvers import BinaryBosonicSolver
from ptseries.common.logger import Logger

from templates import Problem, Algorithm
from .backend import OrcaBackend
from .orca_templates import OrcaRoutine


class BinaryBosonic(Algorithm, OrcaRoutine):
    """ Orca Algorithm """

    def __init__(self, learning_rate:float=1e-1, updates:int=80, tbi_loops:str='single-loop') -> None:
        super().__init__()
        self.bbs = None
        self.learning_rate = learning_rate
        self.updates = updates
        self.tbi_loops = tbi_loops
        self.logger = Logger(log_dir=None)

    def _get_path(self) -> str:
        return 'BinaryBosonic'

    def run(self, problem: Problem, backend: OrcaBackend):
        qubo_fn_fact, Q = problem.get_orca_qubo()
        self.bbs = BinaryBosonicSolver(
            len(Q),
            qubo_fn_fact(Q),
            tbi_params={"tbi_type": self.tbi_loops}
        )
        self.bbs.train(
            learning_rate=self.learning_rate,
            updates=self.updates,
            print_frequency=20,
            logger=self.logger
        )

        return self.bbs.return_solution()
