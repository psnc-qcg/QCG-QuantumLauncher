""" Basic problems for atos """

from problems import EC, JSSP, MaxCut, QATM
from qiskit_stuff.basic_problems import ECQiskit, JSSPQiskit, MaxCutQiskit, QATMQiskit
from utils import ham_from_qiskit_to_atos
from .atos_templates import AtosStuff


class QiskitToAtos:
    def get_atos_hamiltonian(self):
        return ham_from_qiskit_to_atos(self.get_qiskit_hamiltonian())


class ECAtos(ECQiskit, EC, QiskitToAtos, AtosStuff):
    pass


class JSSPAtos(JSSPQiskit, JSSP, QiskitToAtos, AtosStuff):
    pass


class MaxCutAtos(MaxCutQiskit, MaxCut, QiskitToAtos, AtosStuff):
    pass


class QATMAtos(QATMQiskit, QATM, QiskitToAtos, AtosStuff):
    pass
