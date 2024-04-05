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


class QiskitToDwave:
    def get_dwave_qubo(self):
        return self._hamiltonian_to_qubo(self.get_qiskit_hamiltonian())

    def _hamiltonian_to_qubo(self, values: SparsePauliOp):
        """
        Function to convert Z matrix to QUBO matrix
        """
        max_qubit = values.num_qubits
        # print(max_qubit)
        qubo = np.zeros((max_qubit, max_qubit))
        for value in values:
            pauli = value.paulis[0]
            coeff: np.complex128 = value.coeffs[0]
            target_qubits = [ind for ind, x in enumerate(
                str(pauli)) if x == 'Z']
            pauli_type = str(value.paulis[0]).replace('I', '')
            if pauli_type != '':
                if pauli_type == 'ZZ':
                    qubo[target_qubits[0], target_qubits[1]] = coeff.real
                    qubo[target_qubits[1], target_qubits[0]] = coeff.real
                elif pauli_type == 'Z':
                    qubo[target_qubits[0], target_qubits[0]] = coeff.real

            else:
                offset = coeff.real
        return qubo, offset


class ECDwave(ECQiskit, EC, QiskitToDwave, DwaveRoutine):
    pass


class JSSPDwave(JSSPQiskit, JSSP, QiskitToDwave, DwaveRoutine):
    pass


class MaxCutDwave(MaxCutQiskit, MaxCut, QiskitToDwave, DwaveRoutine):
    pass


class QATMDwave(QATMQiskit, QATM, QiskitToDwave, DwaveRoutine):
    pass
