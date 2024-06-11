from templates import QuantumLauncher
from orca_routines import BBS, OrcaBackend
from problems import EC, JSSP, MaxCut, QATM
TESTING_DIR = 'testing'


def test_ec():
    """ Testing function for Exact Cover """
    pr = EC('exact', instance_name='toy')
    bbs = BBS()
    backend = OrcaBackend('local_simulator')
    launcher = QuantumLauncher(pr, bbs, backend, path=TESTING_DIR)

    inform = launcher._run()
    assert inform is not None


def test_jssp():
    """ Testing function for Job Shop Shedueling Problem """
    pr = JSSP(3, 'exact', instance_name='toy', optimization_problem=True)
    bbs = BBS()
    backend = OrcaBackend('local_simulator')
    launcher = QuantumLauncher(pr, bbs, backend, path=TESTING_DIR)

    inform = launcher._run()
    assert inform is not None


def test_maxcut():
    """ Testing function for Max Cut """
    pr = MaxCut(instance_name='default')
    bbs = BBS()
    backend = OrcaBackend('local_simulator')
    launcher = QuantumLauncher(pr, bbs, backend, path=TESTING_DIR)

    inform = launcher._run()
    assert inform is not None
