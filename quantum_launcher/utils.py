from qat.core import Observable, Term
from qiskit.quantum_info import SparsePauliOp
from typing import Iterable, Dict, Tuple, Set, List


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

    sparse_list: List[Tuple[str, List, float]] = []
    constant: float = offset
    for ind_r, row in enumerate(qubo):
        val = row[ind_r]
        constant += val/2
        sparse_list.append(('Z', [ind_r], -val / 2))
        for ind_c, val in enumerate(row[ind_r + 1:], ind_r + 1):
            if val != 0:
                constant += val / 4
                sparse_list.append(('Z', [ind_r], -val / 4))
                sparse_list.append(('Z', [ind_c], -val / 4))
                sparse_list.append(('ZZ', [ind_r, ind_c], val / 4))
    hamiltonian: SparsePauliOp = SparsePauliOp.from_sparse_list(sparse_list, N)
    hamiltonian += SparsePauliOp.from_sparse_list([('I', [0], constant)], N)
    return hamiltonian.simplify()


def _qubo_dict_into_hamiltonian(qubo: Dict[Tuple[str, str], float], offset: float = 0) -> SparsePauliOp:
    label_set: Set[str] = set()
    for (arg1, arg2) in sorted(qubo.keys()):
        if arg1 not in label_set:
            label_set.add(arg1)
        if arg2 not in label_set:
            label_set.add(arg2)

    labels = {label: i for i, label in enumerate(sorted(label_set))}

    N: int = len(labels)

    sparse_list: List[Tuple[str, List, float]] = []
    constant: float = offset
    for (arg1, arg2), coeff in qubo.items():
        if arg1 == arg2:
            constant += coeff / 2
            sparse_list.append(('Z', [labels[arg1]], -coeff / 2))
        else:
            constant += coeff / 4
            sparse_list.append(('ZZ', [labels[arg1], labels[arg2]], coeff / 4))
            sparse_list.append(('Z', [labels[arg1]], -coeff / 4))
            sparse_list.append(('Z', [labels[arg2]], -coeff / 4))

    hamiltonian = SparsePauliOp.from_sparse_list(sparse_list, N)
    hamiltonian += SparsePauliOp.from_sparse_list([('I', [0], constant)], N)

    return hamiltonian.simplify()
