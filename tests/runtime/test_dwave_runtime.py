from quantum_launcher import QuantumLauncher
from quantum_launcher.base import Result
from quantum_launcher.routines.dwave_routines import DwaveSolver, SimulatedAnnealingBackend
from quantum_launcher.problems import EC, JSSP, MaxCut, QATM, Raw
from pyqubo import Spin
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
    qubits = [Spin(f"x{i}") for i in range(2)]
    H = 0
    H += 3 * qubits[0]
    H += 1 * qubits[1]
    H += -5 * qubits[0] * qubits[1]
    bqm = H.compile().to_bqm()
    pr = Raw(bqm)
    solver = DwaveSolver(1)
    backend = SimulatedAnnealingBackend()
    launcher = QuantumLauncher(pr, solver, backend, path=TESTING_DIR)

    inform = launcher._run()
    assert isinstance(inform, Result)
    bitstring = inform.best_bitstring
    assert bitstring in ['00', '01', '10', '11']
