''' file with orca algorithms subclasses '''

from ptseries.algorithms.binary_solvers import BinaryBosonicSolver

from templates import Problem, Algorithm
from orca_stuff.backend import OrcaBackend


class BinaryBosonic(Algorithm):
    ''' Orca Algorithm '''

    def __init__(self) -> None:
        super().__init__()
        self.bbs = None

    def run(self, problem: Problem, backend: OrcaBackend):
        qubo_fn_fact, Q = self.get_problem_data(problem)
        self.bbs = BinaryBosonicSolver(6,
                                       qubo_fn_fact(Q)
                                       )
        self.bbs.train(
            learning_rate=1e-1,
            updates=80,
            print_frequency=20
        )

        return self.bbs.return_solution()

    def check_problem(self, problem: Problem) -> bool:
        ''' Check if the problem implements get_hamiltonian method'''
        return callable(getattr(problem, 'get_orca_qubo', False))

    def get_problem_data(self, problem: Problem):
        if self.check_problem(problem):
            return problem.get_orca_qubo()
        else:
            raise NotImplementedError('The problem does not have orca qubo getter implemented')
