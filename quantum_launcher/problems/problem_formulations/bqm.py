import numpy as np
from qiskit.quantum_info import SparsePauliOp
from qiskit_optimization.converters import QuadraticProgramToQubo
from qiskit_optimization.translators import from_ising
from quantum_launcher.base import adapter, formatter
from typing import Tuple
import ast
from pyqubo import Spin
from .qubo import *
from quantum_launcher.problems import Raw


@adapter('qubo', 'bqm')
def qubo_to_bqm(qubo_with_offset) -> dict:
    qubo, offset = qubo_with_offset
    bqm, _ = QUBOMatrix(qubo, 0).qubo_matrix_into_bqm()
    return bqm


@adapter('hamiltonian', 'qubo')
def hamiltonian_to_qubo(hamiltonian) -> Tuple[np.ndarray, float]:
    qp = from_ising(hamiltonian)
    conv = QuadraticProgramToQubo()
    qubo = conv.convert(qp).objective
    return qubo.quadratic.to_array(), qubo.constant


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


@formatter(Raw, 'bqm')
def Rawbqm(problem: Raw):
    return problem.instance
