from qiskit.quantum_info import SparsePauliOp
from qat.core import Observable, Term


def ham_from_qiskit_to_atos(q_h: SparsePauliOp) -> Observable:
    line_obs = Observable(q_h.num_qubits)
    qubit_list = list(range(q_h.num_qubits))
    for term in q_h.to_list():
        line_obs.add_term(Term(term[1].real, term[0], qubit_list))
    return line_obs
