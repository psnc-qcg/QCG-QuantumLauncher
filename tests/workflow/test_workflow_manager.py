from quantum_launcher import QuantumLauncher
from quantum_launcher.workflow import WorkflowManager
from quantum_launcher.problems import Raw, MaxCut
from quantum_launcher.routines import orca_routines
from quantum_launcher.base import Algorithm


def task1():
    return 10


def task2(result1):
    return result1 * 3


def check_if_qubo(qubo):
    import numpy as np
    assert isinstance(qubo[0], np.ndarray)


def test_task_addition():
    with WorkflowManager() as wm:
        data = wm.task(task1)
        result = wm.task(task2, data)
    wm()
    assert result.result == 30


def test_running():
    with WorkflowManager() as wm:
        data = wm.input()
        result = wm.task(task2, data)
        wm.output(result)

    assert wm(4) == 12


def test_workflow():
    with WorkflowManager() as wm:
        data = wm.input(format='qubo')
        result = wm.task(task2, data)
        wm.output(result)

    workflow = wm.to_workflow()
    assert isinstance(workflow, Algorithm)
    launcher = QuantumLauncher(20, workflow)
    result = launcher.run()
    assert result == 60


def test_workflow_format():
    with WorkflowManager() as wm:
        data = wm.input(format='qubo')
        result = wm.task(check_if_qubo, data)
        wm.output(result)

    workflow = wm.to_workflow()
    assert workflow._algorithm_format == 'qubo'
    launcher = QuantumLauncher(MaxCut(instance_name='default'), workflow)
    result = launcher.run()
