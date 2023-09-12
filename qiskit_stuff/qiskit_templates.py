from abc import abstractmethod

from primitive_strategy import PrimitiveStrategy
from templates import Algorithm, Problem


class HamiltonianAlgorithm(Algorithm):

    @abstractmethod
    def run(self, problem: Problem, primitive_strategy: PrimitiveStrategy):
        ''' Runs the hamiltonian on current algorithm '''

    def check_problem(self, problem: Problem) -> bool:
        ''' Check if the problem implements get_hamiltonian method'''
        return callable(getattr(problem, 'get_hamiltonian', False))

    def get_problem_data(self, problem: Problem):
        if self.check_problem(problem):
            return problem.get_hamiltonian()
        else:
            raise NotImplementedError('The problem does not have hamiltonian getter implemented')
