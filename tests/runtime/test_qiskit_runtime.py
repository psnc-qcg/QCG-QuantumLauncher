from quantum_launcher import QuantumLauncher
from quantum_launcher.base import Result
from quantum_launcher.routines.qiskit_routines import QAOA, QiskitBackend, FALQON
from quantum_launcher.problems import EC, JSSP, MaxCut, QATM, Raw
from qiskit.quantum_info import SparsePauliOp
TESTING_DIR = 'testing'


def test_ec():
    """ Testing function for Exact Cover """
    pr = EC('exact', instance_name='micro')
    qaoa = QAOA(p=3)
    backend = QiskitBackend('local_simulator')
    launcher = QuantumLauncher(pr, qaoa, backend, path=TESTING_DIR)

    # inform = launcher.process(save_pickle=True, save_txt=True)
    inform = launcher.run()
    assert isinstance(inform, Result)


def test_qatm():
    """ Testing function for QATM """
    pr = QATM('exact', instance_name='RCP_3.txt', instance_path='data/qatm/')
    qaoa = QAOA(p=3)
    backend = QiskitBackend('local_simulator')
    launcher = QuantumLauncher(pr, qaoa, backend, path=TESTING_DIR)

    # inform = launcher.process(save_pickle=True)
    inform = launcher.run()
    assert isinstance(inform, Result)


def test_jssp():
    """ Testing function for Job Shop Shedueling Problem """
    pr = JSSP(3, 'exact', instance_name='toy', optimization_problem=True)
    qaoa = QAOA(p=3)
    backend = QiskitBackend('local_simulator')
    launcher = QuantumLauncher(pr, qaoa, backend, path=TESTING_DIR)

    # inform = launcher.process(save_pickle=True)
    inform = launcher.run()
    assert isinstance(inform, Result)


def test_maxcut():
    """ Testing function for Max Cut """
    pr = MaxCut(instance_name='default')
    qaoa = QAOA()
    backend = QiskitBackend('local_simulator')
    launcher = QuantumLauncher(pr, qaoa, backend, path=TESTING_DIR)

    # inform = launcher.process(save_pickle=True)
    inform = launcher.run()
    assert isinstance(inform, Result)


# def test_falqon():
#     """ Testing function for Falqon, using Exact Cover """
#     pr = EC('exact', instance_name='toy')
#     falqon = FALQON()
#     backend = QiskitBackend('local_simulator')
#     launcher = QuantumLauncher(pr, falqon, backend, path=TESTING_DIR)

#     inform = launcher.process(save_to_file=True)
#     assert inform is not None


def test_raw():
    """ Testing function for Raw """
    hamiltonian = SparsePauliOp.from_list(
        [("ZZ", -1), ("ZI", 2), ("IZ", 2), ("II", -1)])
    pr = Raw(hamiltonian)
    qaoa = QAOA()
    backend = QiskitBackend('local_simulator')
    launcher = QuantumLauncher(pr, qaoa, backend, path=TESTING_DIR)

    inform = launcher.run()
    assert inform is not None
    bitstring = inform.best_bitstring
    assert bitstring in ['00', '01', '10', '11']
