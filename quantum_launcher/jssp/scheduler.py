def get_label(task, time):
    return f"{task.job}_{task.position},{time}"


class Task:
    def __init__(self, job, position, machine, duration):
        self.job = job
        self.position = position
        self.machine = machine
        self.duration = duration

    def __repr__(self):
        return ("{{job: {job}, position: {position}, machine: {machine}, duration:"
                " {duration}}}").format(**vars(self))


class KeyList:

    def __init__(self, array, key_function):
        self.array = array
        self.key_function = key_function

    def __len__(self):
        return len(self.array)

    def __getitem__(self, index):
        item = self.array[index]
        key = self.key_function(item)
        return key


class JobShopScheduler:
    def __init__(self, job_dict, max_time=None):
        self.tasks = []
        self.last_task_indices = []
        self.max_time = max_time
        self.H = 0
        self.H_vars = {}
        self.absurd_times = set()
        self._process_data(job_dict)

    def _process_data(self, jobs):
        tasks = []
        last_task_indices = [-1]
        total_time = 0

        for job_name, job_tasks in jobs.items():
            last_task_indices.append(last_task_indices[-1] + len(job_tasks))

            for i, (machine, time_span) in enumerate(job_tasks):
                tasks.append(Task(job_name, i, machine, time_span))
                total_time += time_span

        self.tasks = tasks
        self.last_task_indices = last_task_indices[1:]

        if self.max_time is None:
            self.max_time = total_time

    def _remove_absurd_times(self, disable_till: dict, disable_since, disabled_variables):
        predecessor_time = 0
        current_job = self.tasks[0].job
        for task in self.tasks:
            if task.job != current_job:
                predecessor_time = 0
                current_job = task.job

            for t in range(predecessor_time):
                label = get_label(task, t)
                self.absurd_times.add(label)

            predecessor_time += task.duration

        successor_time = -1
        current_job = self.tasks[-1].job
        for task in self.tasks[::-1]:
            if task.job != current_job:
                successor_time = -1
                current_job = task.job

            successor_time += task.duration
            for t in range(successor_time):
                label = get_label(task, (self.max_time - 1) - t)
                self.absurd_times.add(label)

        for task in self.tasks:
            if task.machine in disable_till.keys():
                for i in range(disable_till[task.machine]):
                    label = get_label(task, i)
                    self.absurd_times.add(label)
            elif task.machine in disable_since.keys():
                for i in range(disable_since[task.machine], self.max_time):
                    label = get_label(task, i)
                    self.absurd_times.add(label)

        for label in disabled_variables:
            self.absurd_times.add(label)
