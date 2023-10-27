""" templates for atos """
from utils import ham_from_qiskit_to_atos
class AtosStuff:
    SYSTEM_NAME = 'atos'

    @property
    def SYSTEM_CLASS(self):
        return AtosStuff

    def get_atos_hamiltonian(self):
        return ham_from_qiskit_to_atos(self.get_qiskit_hamiltonian())
