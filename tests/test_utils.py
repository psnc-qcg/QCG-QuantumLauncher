# TODO: reimplement
# from qiskit_optimization.converters import QuadraticProgramToQubo
# from qiskit_optimization.translators import from_ising
# from qiskit.quantum_info import SparsePauliOp
# import numpy as np

# from quantum_launcher.utils import qubo_to_hamiltonian, _qubo_dict_into_hamiltonian, _qubo_matrix_into_hamiltonian


# def _hamiltonian_to_qubo(hamiltonian: SparsePauliOp) -> tuple[np.ndarray, float]:
#     qp = from_ising(hamiltonian)
#     conv = QuadraticProgramToQubo()
#     qubo = conv.convert(qp).objective
#     return qubo.quadratic.to_array(), qubo.constant


# def test_qubo_dict_to_hamiltonian():
#     qubo, offset = {('a', 'a'): 1, ('a', 'b'): 2, ('b', 'b'): 3}, 2
#     hamiltonian = _qubo_dict_into_hamiltonian(qubo, offset=offset)
#     assert hamiltonian.num_qubits == 2
#     new_qubo, new_offset = _hamiltonian_to_qubo(hamiltonian)
#     assert new_offset == offset
#     qubo_matrix = [[1, 2], [0, 3]]
#     assert (new_qubo == qubo_matrix).all()
