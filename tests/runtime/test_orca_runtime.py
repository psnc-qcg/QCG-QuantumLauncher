from quantum_launcher import QuantumLauncher
from quantum_launcher.routines.orca_routines import BBS, OrcaBackend
from quantum_launcher.problems import EC, JSSP, MaxCut, QATM, Raw
import numpy as np
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


def test_raw():
    """ Testing function for Raw """
    qubo = None, np.array([[10, 1], [0, -10]])
    pr = Raw(qubo)
    bbs = BBS()
    backend = OrcaBackend('local_simulator')
    launcher = QuantumLauncher(pr, bbs, backend, path=TESTING_DIR)

    inform = launcher._run()
    assert inform is not None

    bitstring = bbs.get_bitstring(inform)
    assert bitstring in ['00', '01', '10', '11']
