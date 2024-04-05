import numpy as np
import ast
from templates import Algorithm
from .dwave_templates import DwaveRoutine
from .backend import DwaveBackend
import collections
from pyqubo import Spin
from tabu import TabuSampler


class DwaveSolver(Algorithm, DwaveRoutine):
    def __init__(self, **alg_kwargs) -> None:
        super().__init__(**alg_kwargs)

    def run(self, problem):
        pass

    def _get_path(self) -> str:
        return super()._get_path()

    def solve_dwave(self, qubo, offset, num_reads=1000):
        qubo_matrix = QUBOMatrixDwave(qubo, offset)
        bqm, model = qubo_matrix.Qubo_matrix_into_bqm()
        best_sample = qubo_matrix.solve(bqm, model, num_reads=num_reads)

        return dict(collections.OrderedDict(sorted(best_sample.sample.items())))


class QUBOMatrix:
    def __init__(self, qubo_matrix, offset):
        self.qubo_matrix = qubo_matrix
        self.offset = offset

        if type(self.qubo_matrix) == str:
            try:
                self.qubo_matrix = np.array(ast.literal_eval(self.qubo_matrix))
            except:
                raise SystemExit(
                    """Wrong matrix format, please use list of lists\nIf you are using <nazwa_matrixa> please use -z flag"""
                )

        self.symetric = True
        self.check_if_symetric()

    def check_if_symetric(self):
        """
        Function to check if matrix is symetric
        """
        self.symetric = (self.qubo_matrix.transpose()
                         == self.qubo_matrix).all()
        if not self.symetric:
            self.qubo_matrix = self.remove_lower_triangle(self.qubo_matrix)
            print("Matrix is not symetric, only upper triangle will be used\n")
            print("New QUBO matrix:\n", self.qubo_matrix)

    def remove_lower_triangle(self, matrix):
        """
        Function to remove lower triangle from matrix
        """
        for i in range(len(matrix)):
            for j in range(len(matrix)):
                if i > j:
                    matrix[i][j] = 0
        return matrix

    def get_values_and_qubits(self, matrix):
        """
        Function to get values and qubits from matrix in form of dictionary
        where keys are indexes of qubits and values are values of matrix
        The function does not take into account zeros in matrix
        Example:
        matrix = [[0,1,2],[1,0,3],[2,3,0]]
        result = {(0,1):1, (0,2):2, (1,0):1, (1,2):3, (2,0):2, (2,1):3}
        Function also return second value which is the number of qubits
        """
        result = {
            (x, y): c for y, r in enumerate(matrix) for x, c in enumerate(r) if c != 0
        }
        return result, len(matrix)


class QUBOMatrixDwave(QUBOMatrix):

    def Qubo_matrix_into_bqm(self):
        """
        Function to convert matrix into BQM object
        Steps:
        1. Get values and qubits from matrix
        2. Create Spin variables
        3. Create hamiltonian object
        4. Add values to hamiltonian object
        5. Compile hamiltonian object to model
        6. Transform model to BQM object
        7. Add offset to BQM object
        8. Return BQM object
        """
        values_and_qubits, number_of_qubits = self.get_values_and_qubits(
            self.qubo_matrix
        )
        qubits = [Spin(f"x{i}") for i in range(number_of_qubits)]
        H = 0
        for (x, y), value in values_and_qubits.items():
            if self.symetric:
                H += value / len(set((x, y))) * qubits[x] * qubits[y]
            else:
                H += value * qubits[x] * qubits[y]
        model = H.compile()
        bqm = model.to_bqm()
        bqm.offset += self.offset
        return bqm, model

    def solve(self, bqm, model, num_reads=100):
        """
        Function to solve BQM object
        """
        # sampler = neal.SimulatedAnnealingSampler()
        # sampleset = sampler.sample(bqm, num_reads=100)
        sampler = TabuSampler()
        sampleset = sampler.sample(
            bqm, num_reads=num_reads, return_embedding=True)
        decoded_samples = model.decode_sampleset(sampleset)
        best_sample = min(decoded_samples, key=lambda x: x.energy)
        return best_sample
