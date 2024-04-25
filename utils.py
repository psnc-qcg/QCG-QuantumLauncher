from qat.core import Observable, Term
from qiskit.quantum_info import SparsePauliOp
from typing import Iterable, Dict, Tuple
from collections import defaultdict


def ham_from_qiskit_to_atos(q_h: SparsePauliOp) -> Observable:
    line_obs = Observable(q_h.num_qubits)
    qubit_list = list(range(q_h.num_qubits))
    for term in q_h.to_list():
        line_obs.add_term(Term(term[1].real, term[0], qubit_list))
    return line_obs


def qubo_to_hamiltonian(qubo: Iterable[Iterable[int]] | Dict[Tuple[str, str], float], offset: float = 0) -> SparsePauliOp:
    """
    Convert a QUBO into a quadratic Hamiltonian in the form of a SparsePauliOp.

    Args:
        qubo (Iterable[Iterable[int]] | Dict[Tuple[str, str], float]): Quadratic Unconstrained Binary Optimization written in the form of matrix or dictionary[Tuple[key, key], value].
        offset (float, optional): The offset (constant) value that will be added to identity. Defaults to 0.

    Returns:
        SparsePauliOp: _description_
    """

    if isinstance(qubo, dict):
        return _qubo_dict_into_hamiltonian(qubo, offset)
    elif isinstance(qubo, Iterable):
        return _qubo_matrix_into_hamiltonian(qubo, offset)
    raise ValueError("QUBO must be a matrix or a dictionary")


def _qubo_matrix_into_hamiltonian(qubo: Iterable[Iterable[int]], offset: float = 0) -> SparsePauliOp:
    N = len(qubo)
    assert all(len(row) == N for row in qubo), "QUBO matrix must be square"

    def _create_string(z_index: int | list[int] | None) -> str:
        if z_index is None:
            return 'I' * N

        if isinstance(z_index, int):
            z_index = [z_index]

        string = ''.join('I' if i not in z_index else 'Z' for i in range(N))
        return string

    hamiltonian = SparsePauliOp(_create_string(None), offset)
    for ind_r, row in enumerate(qubo):
        for ind_c, val in enumerate(row[:ind_r + 1]):
            if val != 0:
                hamiltonian += SparsePauliOp(
                    _create_string([ind_c, ind_r]), val)
    return hamiltonian


def _qubo_dict_into_hamiltonian(qubo: Dict[Tuple[str, str], float], offset: float = 0) -> SparsePauliOp:

    labels: Dict[str, int] = defaultdict(
        lambda: max(labels.values(), default=-1) + 1)
    for (arg1, arg2) in sorted(qubo.keys()):
        if arg1 not in labels:
            labels[arg1]
        if arg2 not in labels:
            labels[arg2]

    N: int = len(labels)

    def _create_string(z_index: int | list[int] | None) -> str:
        if z_index is None:
            return 'I' * N

        if isinstance(z_index, int):
            z_index = [z_index]

        string = ''.join('I' if i not in z_index else 'Z' for i in range(N))
        return string

    hamiltonian: SparsePauliOp = SparsePauliOp(_create_string(None), offset)
    for (arg1, arg2), coeff in qubo.items():
        hamiltonian += SparsePauliOp(_create_string(
            [labels[arg1], labels[arg2]]), coeff)
    return hamiltonian
