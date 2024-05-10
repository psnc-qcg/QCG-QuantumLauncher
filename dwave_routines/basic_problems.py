import numpy as np
from problems import EC, JSSP, MaxCut, QATM
from qiskit_routines.basic_problems import (
    ECQiskit,
    JSSPQiskit,
    MaxCutQiskit,
    QATMQiskit,
)
from .dwave_templates import DwaveRoutine
from qiskit.quantum_info import SparsePauliOp
from qiskit_optimization.converters import QuadraticProgramToQubo
from qiskit_optimization.translators import from_ising


class QiskitToDwave:
    def get_qubo(self):
        return self._hamiltonian_to_qubo(self.get_qiskit_hamiltonian())

    def _hamiltonian_to_qubo(self, hamiltonian: SparsePauliOp) -> tuple[np.ndarray, float]:
        qp = from_ising(hamiltonian)
        conv = QuadraticProgramToQubo()
        qubo = conv.convert(qp).objective
        return qubo.quadratic.to_array(), qubo.constant


class ECDwave(ECQiskit, EC, QiskitToDwave, DwaveRoutine):
    pass


class JSSPDwave(JSSPQiskit, JSSP, QiskitToDwave, DwaveRoutine):
    pass


class MaxCutDwave(MaxCutQiskit, MaxCut, QiskitToDwave, DwaveRoutine):
    pass


class QATMDwave(QATMQiskit, QATM, QiskitToDwave, DwaveRoutine):
    pass
