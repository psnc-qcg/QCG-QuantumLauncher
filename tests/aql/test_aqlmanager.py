from quantum_launcher.launcher.aql import AQLManager
from quantum_launcher.problems import MaxCut, EC
from quantum_launcher.routines.dwave_routines import DwaveSolver, SimulatedAnnealingBackend
from quantum_launcher.routines.qiskit_routines import QAOA, QiskitBackend
from quantum_launcher.routines.orca_routines import BBS, OrcaBackend


def test_runtime():
    with AQLManager('test') as launcher:
        launcher.add(backend=SimulatedAnnealingBackend(),
                     algorithm=DwaveSolver(1), problem=EC('exact', instance_name='micro'))
        launcher.add_algorithm(DwaveSolver(2))
        result = launcher.result

    assert len(result) == 2


def test_runtime_dwave():
    with AQLManager('test') as launcher:
        launcher.add(backend=SimulatedAnnealingBackend(),
                     algorithm=DwaveSolver(1), problem=EC('exact', instance_name='micro'))
        launcher.add_algorithm(DwaveSolver(2), times=2)
        launcher.add_problem(MaxCut(instance_name='default'), times=3)
        result = launcher.result
        result_bitstring = launcher.result_bitstring

    assert len(result) == (2+1) * (3+1)
    assert len(result_bitstring) == (2+1) * (3+1)
    for x in result:
        assert x is not None
    for x in result_bitstring:
        assert isinstance(x, str)
        assert len(x) == 2


def test_runtime_qiskit():
    with AQLManager('test') as launcher:
        launcher.add(backend=QiskitBackend('local_simulator'),
                     algorithm=QAOA(2), problem=EC('exact', instance_name='micro'))
        launcher.add_problem(MaxCut(instance_name='default'), times=3)
        result = launcher.result
        result_bitstring = launcher.result_bitstring

    assert len(result) == (3+1)
    assert len(result_bitstring) == (3+1)
    for x in result:
        assert x is not None
    for x in result_bitstring:
        assert isinstance(x, str)
        assert len(x) == 6 or len(x) == 2


def test_runtime_orca():
    # TODO Fix this test, it is not working as expected, it is not ending
    return
    with AQLManager('test') as launcher:
        launcher.add(backend=OrcaBackend('local'),
                     algorithm=BBS(), problem=MaxCut(instance_name='default'))
        launcher.add_problem(MaxCut(instance_name='default'), times=1)
        result = launcher.result
        result_bitstring = launcher.result_bitstring

    assert len(result) == (3+1)
    assert len(result_bitstring) == (3+1)
    for x in result:
        assert x is not None
    for x in result_bitstring:
        assert isinstance(x, str)
        assert len(x) == 10 or len(x) == 2
