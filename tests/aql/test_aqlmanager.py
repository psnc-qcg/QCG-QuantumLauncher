from aql import AQLManager
from problems import MaxCut, EC
from dwave_routines import DwaveSolver, SimulatedAnnealingBackend


def test_runtime():
    with AQLManager('test') as launcher:
        launcher.add(backend=SimulatedAnnealingBackend(),
                     algorithm=DwaveSolver(1), problem=EC('exact', instance_name='micro'))
        launcher.add_algorithm(DwaveSolver(2))
        result = launcher.result

    assert len(result) == 2


def test_runtime_2():
    with AQLManager('test') as launcher:
        launcher.add(backend=SimulatedAnnealingBackend(),
                     algorithm=DwaveSolver(1), problem=EC('exact', instance_name='micro'))
        launcher.add_algorithm(DwaveSolver(2), times=2)
        launcher.add_problem(MaxCut(instance_name='default'), times=3)
        result = launcher.result

    assert len(result) == (2+1) * (3+1)
