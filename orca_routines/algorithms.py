""" file with orca algorithms subclasses """

from ptseries.algorithms.binary_solvers import BinaryBosonicSolver

from templates import Problem, Algorithm
from .backend import OrcaBackend
from .orca_templates import OrcaRoutine


class BinaryBosonic(Algorithm, OrcaRoutine):
    """ Orca Algorithm """

    def __init__(self) -> None:
        super().__init__()
        self.bbs = None

    def _get_path(self) -> str:
        return 'BinaryBosonic'

    def run(self, problem: Problem, backend: OrcaBackend):
        qubo_fn_fact, Q = problem.get_orca_qubo()
        self.bbs = BinaryBosonicSolver(len(Q),
                                       qubo_fn_fact(Q)
                                       )
        self.bbs.train(
            learning_rate=1e-1,
            updates=80,
            print_frequency=20
        )

        return self.bbs.return_solution()
