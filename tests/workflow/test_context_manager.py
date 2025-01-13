from quantum_launcher.workflow import WorkflowManager

def task1():
    return 10

def task2(result1):
    return result1 * 3

def test_simple_linear():
    with WorkflowManager() as wm:
        data = wm.task(task1)
        result = wm.task(task2, data)
    wm.run()
    assert result.result == 30
