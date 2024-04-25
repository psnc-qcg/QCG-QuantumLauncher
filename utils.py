from qat.core import Observable, Term
from qiskit.quantum_info import SparsePauliOp
from typing import Iterable


def ham_from_qiskit_to_atos(q_h: SparsePauliOp) -> Observable:
    line_obs = Observable(q_h.num_qubits)
    qubit_list = list(range(q_h.num_qubits))
    for term in q_h.to_list():
        line_obs.add_term(Term(term[1].real, term[0], qubit_list))
    return line_obs


def qubo_into_hamiltonian(qubo: Iterable[Iterable[int]], bias: float = 0) -> SparsePauliOp:
    """
    Convert a QUBO matrix into a quadratic Hamiltonian in the form of a SparsePauliOp.

    Args:
        qubo (Iterable[Iterable[int]]): Quadratic Unconstrained Binary Optimization Matrix.
        bias (float, optional): The bias value that will be added to identity. Defaults to 0.

    Returns:
        SparsePauliOp: The quadratic Hamiltonian in the form of a SparsePauliOp.
    """
    N = len(qubo)
    assert all(len(row) == N for row in qubo), "QUBO matrix must be square"

    def _create_string(z_index: int | list[int] | None) -> str:
        if z_index is None:
            return 'I' * N

        if isinstance(z_index, int):
            z_index = [z_index]

        string = ''.join('I' if i not in z_index else 'Z' for i in range(N))
        return string

    hamiltonian = SparsePauliOp(_create_string(None), bias)
    for ind_r, row in enumerate(qubo):
        for ind_c, val in enumerate(row[:ind_r + 1]):
            if ind_c == ind_r:
                hamiltonian += SparsePauliOp(_create_string(ind_c), val)
                continue
            if val != 0:
                hamiltonian += SparsePauliOp(
                    _create_string([ind_c, ind_r]), val)
    return hamiltonian
