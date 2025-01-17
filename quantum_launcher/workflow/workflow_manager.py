import concurrent.futures
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple
from quantum_launcher.base import Algorithm


class Task:
    def __init__(self, func: Callable, args: Tuple[Any] = None, kwargs: Dict[str, Any] = None, num_output: int = 1):
        if args is None:
            args = tuple()
        if kwargs is None:
            kwargs = {}
        self.func = func
        self.dependencies: List[Task] = [arg for arg in args if isinstance(arg, Task)]
        self.dependencies.extend([value for value in kwargs.values() if isinstance(value, Task)])
        self.args = args
        self.kwargs = kwargs
        self.done = False
        self.result = None
        self.num_output = num_output
        self.subtasks: List[SubTask] = []

    def run(self):
        binded_args = [arg.result if isinstance(arg, Task) else arg for arg in self.args]
        binded_kwargs = {key: (value.result if isinstance(value, Task) else value) for key, value in self.kwargs.items()}
        self.result = self.func(*binded_args, **binded_kwargs)
        self.done = True

    def is_ready(self):
        return all(map(lambda x: x.done, self.dependencies))

    def __iter__(self):
        for i in range(self.num_output):
            yield SubTask(self, i)


class SubTask(Task):
    def __init__(self, task: Task, index: int):
        self.task = task
        self.index = index

    @property
    def result(self):
        return self.task.result[self.index]

    @property
    def done(self):
        return self.task.done


class Workflow(Algorithm):
    _algorithm_format = 'none'

    def __init__(self, tasks: List[Task], input_task: Task, output_task: Task, input_format: str = 'none'):
        self.tasks = tasks
        self.input_task = input_task
        self.output_task = output_task
        self._algorithm_format = input_format

    def run(self, problem, backend, formatter):
        input_result = formatter(problem)
        self.input_task.result = input_result
        with concurrent.futures.ThreadPoolExecutor() as executor:
            _execute_workflow(self.tasks, executor)
        return self.output_task.result


class WorkflowManager:
    def __init__(self, manager: Literal['ql', 'prefect', 'airflow'] = 'ql'):
        self.tasks: List[Task] = []
        self.manager = manager
        self.input_task: Optional[Task] = None
        self.input_task_format: str = 'none'
        self.output_task: Optional[Task] = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def task(self, func, args: Tuple = None, kwargs: Dict = None, num_output=None) -> Task:
        args = args or tuple()
        kwargs = kwargs or dict()
        new_task = Task(func, args, kwargs, num_output=num_output)
        self.tasks.append(new_task)
        return new_task

    def __call__(self, input_value=None, /):
        if self.input_task:
            self.input_task.result = input_value
        with concurrent.futures.ThreadPoolExecutor() as executor:
            _execute_workflow(self.tasks, executor)
        if self.output_task:
            return self.output_task.result

    def print_dag(self):
        for task in self.tasks:
            dep_names = [dep.func.__name__ for dep in task.dependencies]
            print(f"{task.func.__name__} -> {dep_names}")

    def input(self, format: str = 'none'):
        self.input_task = Task(func=None)
        self.input_task.done = True
        self.input_task_format = format
        return self.input_task

    def output(self, task: Task):
        self.output_task = task

    def to_workflow(self) -> Workflow:
        return Workflow(self.tasks, self.input_task, self.output_task, input_format=self.input_task_format)


def _execute_workflow(tasks: List[Task], executor: concurrent.futures.Executor, max_iterations: Optional[bool] = None):
    remaining_tasks = set(tasks)
    max_iterations, iteration = max_iterations or len(remaining_tasks), 0
    for _ in range(max_iterations):
        ready_tasks = list(filter(Task.is_ready, remaining_tasks))

        if len(ready_tasks) < 1:
            if remaining_tasks:
                raise RuntimeError("Cycle or error in tasks.")
            return

        futures = {executor.submit(task.run): task for task in ready_tasks}
        for future in concurrent.futures.as_completed(futures):
            if future.exception():
                raise future.exception()

        for t in ready_tasks:
            remaining_tasks.remove(t)

        if iteration > max_iterations:
            raise RuntimeError("Processing take too much iterations")
        iteration += 1
