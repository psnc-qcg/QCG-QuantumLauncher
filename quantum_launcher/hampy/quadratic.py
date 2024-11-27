from qiskit.quantum_info import SparsePauliOp
from itertools import combinations
from math import comb
from .hamiltonian import H_x

def H_func(func):
    def inner1(*args, **kwargs):
        return func(*args, **kwargs).simplify()
    return inner1

@H_func
def quadratic_onehot(to_encode: list, n: int = -1) -> SparsePauliOp:
    # Auto adjusting size
    if n == -1: n = max(to_encode) + 1
    prod = None
    for i in to_encode:
        if prod is None:
            prod = H_x(i, n)
        else:
            prod += H_x(i, n)
    sparse_list = []
    sparse_list.append((('I', [0], 1)))
    sp = SparsePauliOp.from_sparse_list(sparse_list, n)

    prod = (sp - prod) if len(to_encode) > 0 else sp
    return prod.compose(prod)

'''           
def ham_to_base_zero(Ham: SparsePauliOp) -> SparsePauliOp:
    truth = Ham_to_truth(Ham, dict)
    min_value = 2
    for i in truth:
        if min_value == 2:
            min_value = i
        if truth[i] < truth[min_value]:
            min_value = i
    k = truth[min_value]
    sparse_list = []
    sparse_list.append((('I', [0], -k)))
    sp = SparsePauliOp.from_sparse_list(sparse_list, int(log2(len(truth))))
    return PauliSumOp(Ham.to_pauli_op() + sp)'''

@H_func
def quad_or(s: list = [0, 1], size: int = -1) -> SparsePauliOp:
    # Auto adjusting size
    if size == -1: size = max(s) + 1
    if size == -1: size = max(s) + 1
    sparse_list = []
    sparse_list.append((('I', [0], len(s))))
    for el in s:
        sparse_list.append((('Z', [el], -1)))
    return SparsePauliOp.from_sparse_list(sparse_list, size)

@H_func
def quad_nand(s: list = [0, 1], size: int = -1) -> SparsePauliOp:
    # Auto adjusting size
    if size == -1: size = max(s) + 1
    if size == -1: size = max(s) + 1
    sparse_list = []
    sparse_list.append((('I', [0], len(s))))
    for el in s:
        sparse_list.append((('Z', [el], 1)))
    return SparsePauliOp.from_sparse_list(sparse_list, size)

@H_func
def quad_nae(s: list = [0, 1], size: int = -1) -> SparsePauliOp:
    # Auto adjusting size
    if size == -1: size = max(s) + 1
    if size == -1: size = max(s) + 1
    sparse_list = []
    sparse_list.append((('I', [0], comb(len(s), 2))))
    for el in combinations(s, 2):
        sparse_list.append((('ZZ', el, -1)))
    return SparsePauliOp.from_sparse_list(sparse_list, size)

@H_func
def test_hamiltonian(s: list, size: int = -1) -> SparsePauliOp:
    '''
    Returns quadratic Hamiltonian that returns 0 if value is in half
    '''
    # Auto adjusting size
    if size == -1: size = max(s) + 1
    if size == -1: size = max(s) + 1
    sparse_list = []
    sparse_list.append((('I', [0], int(len(s)/2))))
    for el in combinations(s, 2):
        sparse_list.append((('ZZ', el, 1)))
    return SparsePauliOp.from_sparse_list(sparse_list, size)

@H_func
def quad_ham_or(H1: SparsePauliOp, H2: SparsePauliOp) -> SparsePauliOp:
    '''
    or gate that works between two Hamiltonianss they will be left in quadratic form
    so don't use that to normal Hamiltonianss with results of 0's and 1's
    '''
    return H1 + H2