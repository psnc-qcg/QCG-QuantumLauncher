""" Basic problems for atos """

from problems import EC, JSSP, MaxCut, QATM, Raw, Problem
from qiskit_routines.basic_problems import ECQiskit, JSSPQiskit, MaxCutQiskit, QATMQiskit
from quantum_launcher.utils import ham_from_qiskit_to_atos
from .atos_templates import AtosRoutine


class QiskitToAtos:
    @Problem.output
    def get_atos_hamiltonian(self):
        return ham_from_qiskit_to_atos(self.get_qiskit_hamiltonian())


class ECAtos(ECQiskit, EC, QiskitToAtos, AtosRoutine):
    pass


class JSSPAtos(JSSPQiskit, JSSP, QiskitToAtos, AtosRoutine):
    pass


class MaxCutAtos(MaxCutQiskit, MaxCut, QiskitToAtos, AtosRoutine):
    pass


class QATMAtos(QATMQiskit, QATM, QiskitToAtos, AtosRoutine):
    pass


class RawAtos(Raw, AtosRoutine):
    @Problem.output
    def get_atos_hamiltonian(self):
        return self.instance
