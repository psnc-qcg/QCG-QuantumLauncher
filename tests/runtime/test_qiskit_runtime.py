from templates import QuantumLauncher
from qiskit_routines import QAOA, QiskitBackend, FALQON
from problems import EC, JSSP, MaxCut, QATM
TESTING_DIR = 'testing'


def test_ec():
    """ Testing function for Exact Cover """
    pr = EC('exact')
    pr.set_instance(instance_name='toy', instance=None)
    qaoa = QAOA(p=3)
    backend = QiskitBackend('local_simulator')
    launcher = QuantumLauncher(pr, qaoa, backend, path=TESTING_DIR)

    inform = launcher.process(save_pickle=True, save_txt=True)
    assert inform is not None


def test_qatm():
    """ Testing function for QATM """
    pr = QATM('exact', instance_name='RCP_3.txt', instance_path='data/qatm/')
    qaoa = QAOA(p=3)
    backend = QiskitBackend('local_simulator')
    launcher = QuantumLauncher(pr, qaoa, backend, path=TESTING_DIR)

    inform = launcher.process(save_pickle=True)
    assert inform is not None


def test_jssp():
    """ Testing function for Job Shop Shedueling Problem """
    pr = JSSP(3, 'exact', instance_name='toy', optimization_problem=True)
    qaoa = QAOA(p=3)
    backend = QiskitBackend('local_simulator')
    launcher = QuantumLauncher(pr, qaoa, backend, path=TESTING_DIR)

    inform = launcher.process(save_pickle=True)
    assert inform is not None


def test_maxcut():
    """ Testing function for Max Cut """
    pr = MaxCut(instance_name='default')
    qaoa = QAOA()
    backend = QiskitBackend('local_simulator')
    launcher = QuantumLauncher(pr, qaoa, backend, path=TESTING_DIR)

    inform = launcher.process(save_pickle=True)
    assert inform is not None


def test_falqon():
    """ Testing function for Falqon, using Exact Cover """
    return 'Not implemented yet'
    pr = EC('exact', instance_name='toy')
    falqon = FALQON()
    backend = QiskitBackend('local_simulator')
    launcher = QuantumLauncher(pr, falqon, backend, path=TESTING_DIR)

    inform = launcher.process(save_to_file=True)
    assert inform is not None
