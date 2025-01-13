import concurrent.futures
from typing import Any, Callable, Dict, List, Optional, Set, Tuple


class Task:
    def __init__(self, func: Callable, args: Tuple[Any], kwargs: Dict[str, Any], num_output: int = 1):
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


class WorkflowManager:
    def __init__(self):
        self.tasks: List[Task] = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def task(self, func, *args, num_output=None, **kwargs) -> Task:
        new_task = Task(func, args, kwargs, num_output=num_output)
        self.tasks.append(new_task)
        return new_task

    def print_dag(self):
        for task in self.tasks:
            dep_names = [dep.func.__name__ for dep in task.dependencies]
            print(f"{task.func.__name__} -> {dep_names}")

    def run(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            self._process_tasks(set(self.tasks), executor)

    def _process_tasks(self, remaining_tasks: Set[Task], executor: concurrent.futures.Executor, max_iterations: Optional[bool] = None):
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
