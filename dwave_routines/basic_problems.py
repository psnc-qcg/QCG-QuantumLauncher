import numpy as np
from .dwave_templates import DwaveRoutine
from qiskit.quantum_info import SparsePauliOp
from qiskit_optimization.converters import QuadraticProgramToQubo
from qiskit_optimization.translators import from_ising
from base import adapter
from typing import Tuple


@adapter('qubo', 'bqm')
def qubo_to_bqm(qubo) -> dict:
    pass


@adapter('hamiltonian', 'qubo')
def hamiltonian_to_qubo(hamiltonian) -> Tuple[np.ndarray, float]:
    qp = from_ising(hamiltonian)
    conv = QuadraticProgramToQubo()
    qubo = conv.convert(qp).objective
    return qubo.quadratic.to_array(), qubo.constant
