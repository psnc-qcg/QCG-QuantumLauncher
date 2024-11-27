'''
#### Main file with generators of hamiltonians (H) and operators on hamiltonians (Ham)
python 3.10.4
qiskit 0.43.3
'''
from itertools import combinations
from qiskit.quantum_info import SparsePauliOp

def H_func(func):
    def inner1(*args, **kwargs):
        hamiltonian:SparsePauliOp = func(*args, **kwargs)
        return hamiltonian.simplify()

    return inner1

def Ham_func(func):
    def inner2(*args, **kwargs):
        hamiltonian:SparsePauliOp = func(*args, **kwargs)
        return hamiltonian.simplify()
    return inner2


def int_to_ham(Hs: tuple, size: int = -1) -> SparsePauliOp:
    if size == -1:
        for H in Hs:
            if type(H) == SparsePauliOp:
                size = H.num_qubits
                break
            else: size = max(size, H + 1)
    Hs = list(Hs)

    for _, i in enumerate(Hs):
        if isinstance(Hs[i], int):
            Hs[i] = H_x(Hs[i], size)
    return Hs

@H_func
def H_x(k: int = 0, size: int = -1) -> SparsePauliOp:
    '''
    Hamiltonian function of "f(x) = x" operator for 1 value
    Currently works only on 1 Qubit

    ### Parameters
    k : int
        Index of qubit that we want to negate
    size : int (if non-specified it takes the smallest possible value)
        Size of gate
    
    ### Errors
    if n <= max(s):
        QiskitError: The number of qubits (n) is smaller than a required index k.
    '''
    if isinstance(k, list):
        k = k[0] # Changing type to single value
    if size == -1:
        size = k + 1 # Auto adjusting size if not specified

    sparse_list = [(('I', [0], 1/2)), (('Z', [k], -1/2))] # Adding both elements to list
    sp = SparsePauliOp.from_sparse_list(sparse_list, size)
    # Transformation list into SparsePauliOp object
    return sp

@H_func
def H_not(k: int, size: int = -1) -> SparsePauliOp:
    '''
    Hamiltonian function of not operator for 1 value
    Currently works only on 1 Qubit

    ### Parameters
    k : int
        Index of qubit that we want to negate
    size : int (if non-specified it takes the smallest possible value)
        Size of gate
    
    ### Errors
    if n <= max(s):
        QiskitError: The number of qubits (n) is smaller than a required index k.
    '''
    # Changing type to single value
    if type(k) == list: k = k[0]
    # Auto adjusting size if not specified
    if size == -1: size = k + 1

    sparse_list = [(('I', [k], 1/2)), (('Z', [k], 1/2))]
    sp = SparsePauliOp.from_sparse_list(sparse_list, size)
    return sp

@H_func
def H_imp(s: list, size: int = -1) -> SparsePauliOp:

    '''Hamiltonian function of operator implication (⇒) 
    Currently works only on 2 Qubit

    ### Parameters
    s : list
        List of Qubits that will be taken to operation
    size : int (if non-specified it takes the smallest possible value)
        Size of gate
    
    ### Errors
      if some of qubits have the same value:
           QiskitError: 'Input indices are duplicated.'''
    if type(s) != list: s = list(s) # Changing type into a list
    if size == -1: size = max(s) + 1 # Auto adjusting size if not specified
    sparse_list = []
    sparse_list.append((('I', [0], 3/4))) # Adding all elements to sparse list
    sparse_list.append((('Z', [s[0]], 1/4)))
    sparse_list.append((('Z', [s[1]], -1/4)))
    sparse_list.append((('ZZ', s, 1/4)))

    sp = SparsePauliOp.from_sparse_list(sparse_list, size)
    # Transformation list into SparsePauliOp object

    return sp

@H_func
def H_lin3(s: list, size: int = -1) -> SparsePauliOp:
    '''
    Hamiltonian function of operator lin3
    Currently works only on 3 Qubit

    ### Parameters
    s : list
        List of Qubits that will be taken to operation
    size : int (if non-specified it takes the smallest possible value)
        Size of gate
    
    ### Errors
      if some of qubits have the same value:
           QiskitError: 'Input indices are duplicated.
    '''
    if type(s) != list: s = list(s) # Changing type into a list
    if size == -1: size = max(s) + 1 # Auto adjusting size if not specified

    sparse_list = []
    sparse_list.append((('I', [0], 3/8))) # Adding all elements to sparse list
    
    for i in s:
        sparse_list.append((('Z', [i], 1/8)))
    l = [] # this list is just for not adding useless elements to a sparse list
    for i in s:
        l.append(i)
        for j in s:
            if j not in l:    
                sparse_list.append((('ZZ', [i, j], -1/8)))
    sparse_list.append((('ZZZ', s, -3/8)))

    return SparsePauliOp.from_sparse_list(sparse_list, size) # Transformation list into SparsePauliOp object

@H_func
def H_maj(s: list, size: int = -1) -> SparsePauliOp:

    '''Hamiltonian function of operator MAJ
    Currently works only on 3 Qubit

    ### Parameters
    s : list
        List of Qubits that will be taken to operation
    size : int (if non-specified it takes the smallest possible value)
        Size of gate
    
    ### Errors
      if some of qubits have the same value:
           QiskitError: 'Input indices are duplicated.'''
    if type(s) != list: s = list(s) # Changing type into a list
    if size == -1: size = max(s) + 1 # Auto adjusting size if not specified
    sparse_list = [] 
    sparse_list.append((('I', [0], 1/2))) # Adding all elements to sparse list
    for i in s: 
        sparse_list.append((('Z', [i], -1/4)))
    sparse_list.append((('ZZZ', s, 1/4)))
    
    return SparsePauliOp.from_sparse_list(sparse_list, size) # Transformation list into SparsePauliOp object

@H_func
def H_and(s: list, size: int = -1) -> SparsePauliOp:
    '''
    Function create and reduces hamiltonian based on logical AND

    ### Parameters
    s : list
        List of Qubits that will be taken to operation
    size : int (if non-specified it takes the smallest possible value)
        Size of gate
    
    ### Errors
    if n <= max(s):
        QiskitError: The number of qubits (n) is smaller than a required index max(s).
    '''
    if type(s) != list: s = list(s) # Changing type into a list
    # Auto adjusting size if not specified
    if size == -1: size = max(s) + 1

    product_ = None
    for i in s:
        sparse_list = []
        sparse_list.append((('I', [i], 1)))
        sparse_list.append((('Z', [i], -1)))
        sp = SparsePauliOp.from_sparse_list(sparse_list, size)
        if product_ is None:
            product_ = sp
        else:
            product_ = product_.compose(sp)
    product_ *= 1 / (2 ** len(s))
    return product_

@H_func
def H_nand(s: list, size: int = -1) -> SparsePauliOp:
    '''
    Function create and reduces hamiltonian based on logical NAND

    ### Parameters
    s : list
        List of Qubits that will be taken to operation
    size : int (if non-specified it takes the smallest possible value)
        Size of gate
    
    ### Errors
    if n <= max(s):
        QiskitError: The number of qubits (n) is smaller than a required index max(s).
    '''
    if type(s) != list: s = list(s) # Changing type into a list
    if size == -1: size = max(s) + 1 # Auto adjusting size if not specified

    product_ = None
    for i in s:
        sparse_list = []
        sparse_list.append((('I', [i], 1)))
        sparse_list.append((('Z', [i], -1)))
        sp = SparsePauliOp.from_sparse_list(sparse_list, size)
        if product_ is None:
            product_ = sp
        else:
            product_ = product_.compose(sp)
    product_ *= 1 / (2 ** len(s))
    I = SparsePauliOp.from_sparse_list([(('I', [0], 1))], size)

    return I - product_

@H_func
def H_or(s: list, size: int = -1) -> SparsePauliOp:
    '''
    Function create and reduces hamiltonian based on logical OR

    ### Parameters
    s : list
        List of Qubits that will be taken to operation
    size : int (if non-specified it takes the smallest possible value)
        Size of Hamiltonian
    
    ### Errors
    if n <= max(s):
        QiskitError: The number of qubits (n) is smaller than a required index max(s).
    '''
    if type(s) != list: s = list(s) # Changing type into a list
    if size == -1:
        size = max(s) + 1 # Auto adjusting size if not specified

    product_ = None
    for i in s:
        sparse_list = []
        sparse_list.append((('I', [0], 1)))
        sparse_list.append((('Z', [i], 1)))

        sp = SparsePauliOp.from_sparse_list(sparse_list, size)

        if product_ is None:
            product_ = sp
        else:
            product_ = product_.compose(sp)

    product_ *= 1 / (2 ** len(s))
    # Now we have to make product = I - product
    sparse_list = [(('I', [0], 1))]
    return SparsePauliOp.from_sparse_list(sparse_list, size) - product_

@H_func
def H_nor(s: list, size: int = -1) -> SparsePauliOp:
    '''
    Function create and reduces hamiltonian based on logical NOR

    ### Parameters
    s : list
        List of Qubits that will be taken to operation
    size : int (if non-specified it takes the smallest possible value)
        Size of Hamiltonian
    
    ### Errors
    if n <= max(s):
        QiskitError: The number of qubits (n) is smaller than a required index max(s).
    '''
    if type(s) != list: s = list(s) # Changing type into a list
    if size == -1:
        size = max(s) + 1 # Auto adjusting size if not specified

    product_ = None
    for i in s:
        sparse_list = []
        sparse_list.append((('I', [0], 1)))
        sparse_list.append((('Z', [i], 1)))

        sp = SparsePauliOp.from_sparse_list(sparse_list, size)

        if product_ is None:
            product_ = sp
        else:
            product_ = product_.compose(sp)
        
    product_ *= 1 / (2 ** len(s))
    # Now we have to make product = I - product
    return product_

@H_func
def H_xor(s: list, size: int = -1) -> SparsePauliOp:
    '''
    Function create and reduces hamiltonian based on logical XOR

    ### Parameters
    s : list
        List of Qubits that will be taken to operation
    size : int (if non-specified it takes the smallest possible value)
        Size of gate
    
    ### Errors
    if n <= max(s):
        QiskitError: The number of qubits (n) is smaller than a required index max(s).
    '''
    if type(s) != list: s = list(s) # Changing type into a list
    if size == -1: size = max(s) + 1 # Auto adjusting size if not specified

    z = ''.join(['Z' for _ in range(len(s))])
    z = SparsePauliOp.from_sparse_list([(z, s, 1/2)], size)
    k = SparsePauliOp.from_sparse_list([(('I', [size - 1], 1/2))], size)
    return k - z  

@H_func
def H_nae(s: list, size: int = -1) -> SparsePauliOp:
    '''
    Function create and reduces hamiltonian based logical NAE (not all equal)

    ### Parameters
    s : list
        List of Qubits that will be taken to operation
    size : int (if non-specified it takes the smallest possible value)
        Size of gate
    
    ### Errors
    if size <= max(s):
        QiskitError: The number of qubits (n) is smaller than a required index max(s).
    '''
    s = list(dict.fromkeys(s)) # Removing duplicates
    if size == -1: size = max(s) + 1 # Auto adjusting size

    k, z, ls = 2, 'ZZ', len(s) # Creating variables
    sparse_list = []
    while k <= ls: # While we can make even sums, we do it
        for i in list(combinations(s, k)): # Iterating through all Combinations
            sparse_list.append(((z, i, 1)))
        k += 2 # Only even combinations matter
        z += 'ZZ' # Less elegant, but faster

    sp = SparsePauliOp.from_sparse_list(sparse_list, size) # Sparsing this int
    num = 2**(ls-1) # 2^(ls-1)
    Isp = SparsePauliOp.from_sparse_list([('I', [0], (num-1))], size) # Creating 1 to substruct
    return (Isp - sp)/num

@H_func
def H_mod(s: list, size: int = -1) -> SparsePauliOp:
    '''
    Function create and reduces hamiltonian based logical mod (every one is equal, non of them are)

    ### Parameters
    s : list
        List of Qubits that will be taken to operation
    size : int (if non-specified it takes the smallest possible value)
        Size of gate
    
    ### Errors
    if size <= max(s):
        QiskitError: The number of qubits (n) is smaller than a required index max(s).
    '''
    s = list(dict.fromkeys(s)) # Removing duplicates
    if size == -1: size = max(s) + 1 # Auto adjusting size
    k, z, ls = 2, 'ZZ', len(s) # Creating variables
    sparse_list = []
    while k <= ls: # While we can make even sums, we do it
        for i in list(combinations(s, k)): # Iterating through all Combinations
            sparse_list.append(((z, i, 1)))
        k += 2 # Only even combinations matter
        z += 'ZZ' # Less elegant, but faster

    sp = SparsePauliOp.from_sparse_list(sparse_list, size) # Sparsing this int
    num = 2**(ls-1) # 2^(ls-1)
    Isp = SparsePauliOp.from_sparse_list([('I', [0], 1)], size) # Creating 1 to add
    return (Isp + sp)/num

@H_func
def H_one_in_n(s: list, size: int = -1) -> SparsePauliOp:
    '''
    Function create and reduces hamiltonian based logical (one in n) 
    Which returns True if exactly one element is True

    ### Parameters
    s : list
        List of Qubits that will be taken to operation
    size : int (if non-specified it takes the smallest possible value)
        Size of gate
    
    ### Errors
    if size <= max(s):
        QiskitError: The number of qubits (n) is smaller than a required index max(s).
    '''
    if type(s) != list: s = list(s) # Changing type into a list
    if size == -1: size = max(s) + 1 # Auto adjusting size
    onehot = None
    for i in s:
        c = H_x(i, size)
        k = s.copy()
        k.remove(i)
        for j in k:
            c = c.compose(H_not(j, size))

        onehot = c if onehot is None else onehot + c

    return onehot

@Ham_func
def Ham_not(H: SparsePauliOp) -> SparsePauliOp:
    '''
    Returns negated Hamiltonian (not H)
    Hamiltonian functions that return 0 rather than 1 and 1 rather than 0
    
    ### Parameters
    H : SparsePauliOp
        Hamiltonian function that we want to negate
    
    '''
    n = H.num_qubits
    sparse_list = []
    sparse_list.append((('I', [0], 1)))
    sp = SparsePauliOp.from_sparse_list(sparse_list, n)
    return sp - H

@Ham_func
def Ham_and(Hs: list[SparsePauliOp|int], size: int = -1) -> SparsePauliOp:
    '''
    And operators for hamiltonians

    It's equal to H1 and H2 (where H1, H2 are hamiltonians)

    example: Ham_and(H1, H2, H3) = H1 and H2 and H3

    where H1, H2, H3 are Hamiltonians (PauliSumOp)

    where H1, H2, H3 are Hamiltonians (SparsePauliOp)

    ### Arguments
    - Hs - list of Hamiltonians or integers (single qubits), which are variables of and operator
    - size - integer, no need to specify, unless you work only on qubits
    '''
    # Changing single Qubits to Hamiltonians
    for H in Hs:
        if type(H) == int:
            Hs = int_to_ham(Hs, size)
            break
    # Multiplying
    prod = None
    for H in Hs:
        prod = H if prod is None else prod.compose(H)
    return prod

@Ham_func
def Ham_xor(Hs: list[SparsePauliOp|int], size: int = -1) -> SparsePauliOp:
    '''
    Xor opeartor for hamiltonians

    It's equal to H1 xor H2 (where H1 and H2 are hamiltonians)
    
    example: Ham_xor(H1, H2, H3) = H1 xor H2 xor H3

    where H1, H2, H3 are Hamiltonians (SparsePauliOp)

    ### Arguments
    - Hs - list of Hamiltonians or integers (single qubits), which are variables of xor operator
    - size - integer, no need to specify, unless you work only on qubits
    '''
    # Dealing with single qubits
    for H in Hs:
        if type(H) == int:
            Hs = int_to_ham(Hs, size)
            break

    res = None
    for H in Hs:
        if res is None: 
            res = H
        else:
            res += H - (2*res.compose(H))


    return res

@Ham_func
def Ham_imp(H1: SparsePauliOp|list, H2: SparsePauliOp) -> SparsePauliOp:
    '''
    Implication operator for hamiltonians

    example: Ham_imp(H1, H2) = H1 -> H2
    
    where H1, H2 are Hamiltonians

    ### Arguments:
    - H1 - first hamiltonian / both arguments may be passed as a list
    - H2 - * second hamiltonian

    '''
    # Changing list into arguments
    if isinstance(H1, list):
        H2, H1 = H1[1], H1[0]
    sparse_list = [(('I', [0], 1))]
    I = SparsePauliOp(SparsePauliOp.from_sparse_list(sparse_list, H1.num_qubits))
    return I - H1 + H1.compose(H2)

@Ham_func
def Ham_or(Hs: list[SparsePauliOp|int], size: int = -1) -> SparsePauliOp:
    '''
    Or opeartor for hamiltonians

    It's equal to H1 xor H2 (where H1 and H2 are hamiltonians)
    
    example: Ham_or(H1, H2, H3) = H1 or H2 or H3

    where H1, H2, H3 are Hamiltonians (SparsePauliOp)

    ### Arguments
    - Hs - list of Hamiltonians or integers (single qubits), which are variables of and operator
    - size - integer, no need to specify, unless you work only on qubits
    '''
    # Changing single qubits to Hamiltonians
    for H in Hs:
        if type(H) == int:
            Hs = int_to_ham(Hs, size)
            break

    n = len(Hs)
    prod = None
    for i in range(1, n + 1):
        for j in combinations(range(n), i):
            sec_prod = None
            for k in j:
                sec_prod = Hs[k] if sec_prod is None else sec_prod.compose(Hs[k])
            prod = sec_prod if prod is None else prod + ((-1) ** (i + 1)) * sec_prod
    return prod

@Ham_func
def Ham_scalar_sum(H1: SparsePauliOp, H2: SparsePauliOp, a: float = 1, b: float = 1) -> SparsePauliOp:
    '''
    scalar sum of hamiltonians

    after using this operation hamiltonian is no longer boolean

    maybe it should be moved to onehot
    '''
    return (a * H1) + (b * H2)

@Ham_func
def Ham_maj(H1: SparsePauliOp|list, H2: SparsePauliOp = H_x(), H3: SparsePauliOp = H_x()) -> SparsePauliOp:
    '''
    Majority operator for 3 hamiltonians

    it returns True if majority of Hamiltonians are satisfied

    it returns False otherwise

    ### Arguments
    - H1 - first Hamiltonian / list with 3 Hamiltonians
    - H2 - * second Hamiltonian
    - H3 - * thierd Hamiltonian
    '''
    # Changing type if args passed in list
    if isinstance(H1, list):
        H3, H2, H1 = H1[2], H1[1], H1[0]
    return (H1.compose(H2) + H1.compose(H3) + H2.compose(H3) - (2 * H1.compose(H2).compose(H3)))
