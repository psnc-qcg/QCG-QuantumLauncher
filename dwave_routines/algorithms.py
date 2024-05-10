import numpy as np
import ast
from templates import Algorithm
from .dwave_templates import DwaveRoutine
from pyqubo import Spin
from dimod.binary.binary_quadratic_model import BinaryQuadraticModel


class DwaveSolver(Algorithm, DwaveRoutine):
    def __init__(self, **alg_kwargs) -> None:
        super().__init__(**alg_kwargs)

    def run(self, problem: DwaveRoutine, backend: DwaveRoutine, **kwargs):
        self._sampler = backend.sampler
        if 'get_bqm' in problem.__dict__:
            bqm: BinaryQuadraticModel = problem.get_bqm()
        else:
            qubo, offset = problem.get_qubo()
            bqm, _ = QUBOMatrix(qubo, offset).qubo_matrix_into_bqm()
        return self._solve_bqm(bqm, **kwargs)

    def _get_path(self) -> str:
        return super()._get_path()

    def _solve_bqm(self, bqm, **kwargs):
        return self._sampler.sample(bqm, **kwargs)


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
        self._check_if_symetric()

    def _check_if_symetric(self):
        """
        Function to check if matrix is symetric
        """
        self.symetric = (self.qubo_matrix.transpose()
                         == self.qubo_matrix).all()
        if not self.symetric:
            self.qubo_matrix = self._remove_lower_triangle(self.qubo_matrix)
            print("Matrix is not symetric, only upper triangle will be used\n")
            print("New QUBO matrix:\n", self.qubo_matrix)

    def _remove_lower_triangle(self, matrix):
        """
        Function to remove lower triangle from matrix
        """
        for i in range(len(matrix)):
            for j in range(len(matrix)):
                if i > j:
                    matrix[i][j] = 0
        return matrix

    def _get_values_and_qubits(self, matrix):
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

    def qubo_matrix_into_bqm(self):
        values_and_qubits, number_of_qubits = self._get_values_and_qubits(
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
