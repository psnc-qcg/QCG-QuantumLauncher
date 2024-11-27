# Done in 3.10.4
from qiskit.quantum_info import SparsePauliOp
from typing import Callable
from itertools import combinations, product
from math import log2, comb
from numpy import zeros, ones


# To Change
def Ham_to_truth(H: SparsePauliOp, output: type = list) -> list | dict:
    '''
    Method that transforms Hamiltonian into a truth table respresented as a list with outputs

    ### Parameters
    H: SparsePauliOp
        Hamiltonian function
    *output: type == list
        if it's change into a set method will give output as a dict
    
    '''
    l = [[str(H.paulis[i]), H.coeffs[i]] for i in range(len(H.paulis))]
    for k in l:
        k[0] = [1 if s == 'I' else -1 for s in reversed(k[0])]
    truth_table = []
    for perm in product([0, 1], repeat=len(l[0][0])):
        val = 0
        for parm in l:
            sign = 1
            for i, s in enumerate(perm): sign *= parm[0][len(perm) - 1 - i] ** s
            val += sign * parm[1]
        truth_table.append(val)

    if output == dict:
        out = {}
        for i, k in enumerate(product([0, 1], repeat= len(l[0][0]))): out[''.join([str(s) for s in k])] = truth_table[i]
        return out

    return truth_table

def check_Hamiltonian(H: SparsePauliOp) -> bool:
    '''
    Checks if Hamiltonian is a boolean function
    returns False if Hamiltonian is not a boolean function
    return True if Hamiltonian is a boolean function
    ### Parameters
    H: SparsePauliOp
        Hamiltonian function we want to check
    '''
    truth = Ham_to_truth(H)
    for el in truth:
        if not el in [0, 1]:
            return False
    return True

def truth_to_com(truth: list[int], output: type = list) -> list | dict:
    '''
    Method that changes truth table into a commutative table
    Returns False if function from thuth table is not commutative

    ### Parameters
    truth : list
        truth table writen as a list
    * output : type
        Can be changed to set in order to get set as an output
        which for every number of positive values returns their output

    '''
    perms = list(product([0, 1], repeat= int(log2(len(truth)))))
    com = {} # Creating variable
    for i in range(len(truth)):
        z = str(sum(perms[i])) 
        if not z in com or com[z] == truth[i]: com[z] = truth[i] # Checking if method values repeat
        else: return False # breaking of the method, because function is not commutative
    if output == dict: return com # it was easier to make it first as an set
    return list(com.values()) # changing type to list, if not specified otherwise

def com_to_truth(com: list[int], mode: type = list) -> list | dict:
    '''
    Method that changes commutative table into a truth table

    ### Parameters
    truth : list
        truth table writen as a list
    * output : type
        Can be changed to dict in order to get set as an output
        which for every combination written as a string returns their output

    '''
    perms = product([0, 1], repeat= len(com) - 1)
    if mode == dict:
        truth = {}
        for i in perms: truth[''.join([str(k) for k in i])] = com[sum(i)] # Adding element to a dictionary
    elif mode == list: truth = [com[sum(i)] for i in perms] # Adding element to a list
    return truth

def func_to_truth(func: Callable[[list], bool] , n: int, output: type = list) -> list | dict:
    '''
    Method takes a function that takes n element list as an argument and returns boolean
    and changes it into a truth table
    '''
    perm = product([0, 1], repeat= n)
    if output == list: 
        truth = []
        for i in perm: truth.append(func(list(reversed(i))))
    elif output == dict:
        truth = {}
        for i in perm: truth[''.join([str(k) for k in i])] = func(list(reversed(i)))
    return truth

def create_ham(truth: Callable[[list[bool]],bool], k: int = -1) -> SparsePauliOp:
    '''
    Function that creates a hamiltonian from truth table
    Suggested to be used with functions func_to_truth and com_to_truth

    ### Parameters
    truth: list
        Truth table in ordered list that we want to transform into hamiltonian
    k: (if non-specified it takes the smallest possible value)
        Size of Hamiltonian
        Will be ignored if size of required Hamiltonian will be bigger
    '''
    from numpy.linalg import solve
    # Creating Option Matrix
    matrix = ones((len(truth), len(truth)))
    n = int(log2(len(truth)))
    for row_iter, perm in enumerate(product([0, 1], repeat= n)):
        column_iter = 0
        for part in range(n + 1):
            for combination in combinations(range(n), part):
                s = sum([perm[len(perm) - c - 1] for c in combination]) % 2
                if s == 1: matrix[row_iter][column_iter] = -1
                column_iter += 1
    # Finding coefficients
    coeffs = solve(matrix, truth)
    # Transforming list of coefficients into sparse list
    sparse_list, it = [], 0
    for part in range(n + 1):
        for combination in combinations(range(n), part):
            sparse_list.append((''.join(['Z' for i in range(part)]), combination, coeffs[it]))
            it += 1
    # Transforming Sparse list into hamiltonian
    ham = SparsePauliOp.from_sparse_list(sparse_list, max(n, k))
    return ham

def com_to_ham(com: list[int], k: int = -1) -> SparsePauliOp:
    '''
    Function that changes commutative truth table into a hamiltonian
    It solves coefficients in polynomial time
    Because of binomial coefficients in some cases value is accurate only to some decimal point
    '''

    from numpy.linalg import solve
    n = len(com) - 1
    matrix = zeros((n + 1, n + 1))
    hn = int((n+1)/2)
    for ri in range(hn + 1):
        for ci in range(n + 1):
            # Now it's time for black magic, It works, but strugles with big numbers (result is not always accurate because of decimal point)
            matrix[ri][ci] = sum([((-1)**i) * ((2)**(ri - i)) * comb(ri, i) * comb(n - ri + i, ci) for i in range(max(0, ci - n + ri), ri + 1)])
    # Now it's just slightly different to copy half of odd and even sizes
    if n % 2 == 0:
        for r in range(1, n + 1 - hn):
            for ci in range(n + 1):
                matrix[hn + r][ci] = matrix[hn - r][ci] if ci % 2 == 0 else -1 * matrix[hn - r][ci]
    else:
        for r in range(n + 1 - hn):
            for ci in range(n + 1):
                matrix[hn + r][ci] = matrix[hn - r - 1][ci] if ci % 2 == 0 else -1 * matrix[hn - r - 1][ci]
    coeffs = solve(matrix, com)

    # Now comes the slow part
    sparse_list = []
    #return coeffs
    for l, coeff in enumerate(coeffs):
        for combination in combinations(range(n), l):
            sparse_list.append((''.join(['Z' for _ in range(l)]), combination, coeff))
    ham = SparsePauliOp.from_sparse_list(sparse_list, max(n, k))
    return ham

def get_output(Ham: SparsePauliOp) -> dict:
    truth = Ham_to_truth(Ham, dict)
    min_value = min(truth.values())
    res = []
    for i in truth:
        if truth[i] == min_value: res.append(i)
    return res