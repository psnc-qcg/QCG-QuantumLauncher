from templates import QuantumLauncher
from dwave_routines import DwaveSolver, SimulatedAnnealingBackend
from problems import EC, JSSP, MaxCut, QATM, Raw
import numpy as np
TESTING_DIR = 'testing'


def test_ec():
    """ Testing function for Exact Cover """
    pr = EC('quadratic', instance_name='toy')
    solver = DwaveSolver(1)
    backend = SimulatedAnnealingBackend()
    launcher = QuantumLauncher(pr, solver, backend, path=TESTING_DIR)

    inform = launcher._run()
    assert inform is not None


def test_jssp():
    """ Testing function for Job Shop Shedueling Problem """
    pr = JSSP(3, 'quadratic', instance_name='toy', optimization_problem=True)
    solver = DwaveSolver(1)
    backend = SimulatedAnnealingBackend()
    launcher = QuantumLauncher(pr, solver, backend, path=TESTING_DIR)

    inform = launcher._run()
    assert inform is not None


def test_maxcut():
    """ Testing function for Max Cut """
    pr = MaxCut(instance_name='default')
    solver = DwaveSolver(1)
    backend = SimulatedAnnealingBackend()
    launcher = QuantumLauncher(pr, solver, backend, path=TESTING_DIR)

    inform = launcher._run()
    assert inform is not None


def test_qatm():
    """ Testing function for Max Cut """
    pr = QATM('exact', instance_name='RCP_3.txt', instance_path='data/qatm/')
    solver = DwaveSolver(1)
    backend = SimulatedAnnealingBackend()
    launcher = QuantumLauncher(pr, solver, backend, path=TESTING_DIR)

    inform = launcher._run()
    assert inform is not None


def test_raw():
    """ Testing function for Raw """
    qubo = np.array([[10, 1], [0, -10]]), 0
    pr = Raw(qubo)
    solver = DwaveSolver(1)
    backend = SimulatedAnnealingBackend()
    launcher = QuantumLauncher(pr, solver, backend, path=TESTING_DIR)

    inform = launcher._run()
    assert inform is not None
    bitstring = solver.get_bitstring(inform)
    assert bitstring in ['00', '01', '10', '11']
