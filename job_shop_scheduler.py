from __future__ import print_function

from bisect import bisect_right

from qat.core import Observable, Term

import hampy


def get_jss_hamiltonian_qiskit(job_dict, max_time, onehot):
    scheduler = JobShopScheduler(job_dict, max_time, onehot)
    return scheduler.get_hamiltonian_qiskit()

def get_jss_hamiltonian_atos(job_dict, max_time, onehot):
    scheduler = JobShopScheduler(job_dict, max_time, onehot)
    return scheduler.get_hamiltonian_atos()

def get_label(task, time):
    """Creates a standardized name for variables in the constraint satisfaction problem,
    JobShopScheduler.csp.
    """
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
    """A wrapper to an array. Used for passing the key of a custom object to the bisect function.
    Note: bisect function does not let you choose an arbitrary key, hence this class was created.
    """

    def __init__(self, array, key_function):
        self.array = array  # An iterable
        self.key_function = key_function  # Function for grabbing the key of a given item

    def __len__(self):
        return len(self.array)

    def __getitem__(self, index):
        item = self.array[index]
        key = self.key_function(item)
        return key


class JobShopScheduler:
    def __init__(self, job_dict, max_time=None, onehot='exact'):
        self.tasks = []
        self.last_task_indices = []
        self.max_time = max_time
        self.H_qiskit = 0
        self.H_atos = None
        self.H_pos_by_label = dict()
        self.H_label_by_pos = dict()
        self.absurd_times = set()
        self.onehot = onehot

        self._process_data(job_dict)

    def _process_data(self, jobs):
        tasks = []
        last_task_indices = [-1]  # -1 for zero-indexing
        total_time = 0  # total time of all jobs

        for job_name, job_tasks in jobs.items():
            last_task_indices.append(last_task_indices[-1] + len(job_tasks))

            for i, (machine, time_span) in enumerate(job_tasks):
                tasks.append(Task(job_name, i, machine, time_span))
                total_time += time_span

        # Update values
        self.tasks = tasks
        self.last_task_indices = last_task_indices[1:]

        if self.max_time is None:
            self.max_time = total_time

    def _add_one_start_constraint_qiskit(self):
        for task in self.tasks:
            task_times = {get_label(task, t) for t in range(self.max_time)}
            sieved_tasks = set()
            for label in task_times:
                if label in self.absurd_times:
                    continue
                else:
                    sieved_tasks.add(self.H_pos_by_label[label])
            if self.onehot == 'exact':
                self.H_qiskit += hampy.Ham_not(hampy.H_one_in_n(sieved_tasks, self.n))
            elif self.onehot == 'quadratic':
                self.H_qiskit += hampy.quadratic_onehot(sieved_tasks, self.n)

    def _add_precedence_constraint_qiskit(self):
        for current_task, next_task in zip(self.tasks, self.tasks[1:]):
            if current_task.job != next_task.job:
                continue
            for t in range(self.max_time):
                current_label = get_label(current_task, t)
                if current_label in self.absurd_times:
                    continue
                var1 = self.H_pos_by_label[current_label]
                for tt in range(min(t + current_task.duration, self.max_time)):
                    next_label = get_label(next_task, tt)
                    if next_label in self.absurd_times:
                        continue
                    var2 = self.H_pos_by_label[next_label]
                    self.H_qiskit += hampy.H_x(var1, self.n).compose(hampy.H_x(var2, self.n))

    def _add_share_machine_constraint_qiskit(self):
        """self.csp gets the constraint: At most one task per machine per time unit
        """
        sorted_tasks = sorted(self.tasks, key=lambda x: x.machine)
        # Key wrapper for bisect function
        wrapped_tasks = KeyList(sorted_tasks, lambda x: x.machine)

        head = 0
        while head < len(sorted_tasks):

            # Find tasks that share a machine
            tail = bisect_right(wrapped_tasks, sorted_tasks[head].machine)
            same_machine_tasks = sorted_tasks[head:tail]

            # Update
            head = tail

            # No need to build coupling for a single task
            if len(same_machine_tasks) < 2:
                continue

            # Apply constraint between all tasks for each unit of time
            for task in same_machine_tasks:
                for other_task in same_machine_tasks:
                    if task.job == other_task.job and task.position == other_task.position:
                        continue

                    for t in range(self.max_time):
                        current_label = get_label(task, t)
                        if current_label in self.absurd_times:
                            continue

                        var1 = self.H_pos_by_label[current_label]

                        for tt in range(t, min(t + task.duration, self.max_time)):
                            this_label = get_label(other_task, tt)
                            if this_label in self.absurd_times:
                                continue
                            var2 = self.H_pos_by_label[this_label]

                            self.H_qiskit += hampy.H_x(var1, self.n).compose(hampy.H_x(var2, self.n))

    def _add_one_start_constraint_atos(self):
        self.H_atos = Observable(self.n)
        for task in self.tasks:
            task_times = {get_label(task, t) for t in range(self.max_time)}
            sieved_tasks = set()
            for label in task_times:
                if label in self.absurd_times:
                    continue
                else:
                    sieved_tasks.add(self.H_pos_by_label[label])
            if self.onehot == 'exact':
                ham = None
                for elem1 in sieved_tasks:
                    obs1 = Observable(self.n, pauli_terms=[Term(0.5, "I", [0]), Term(-0.5, "Z", [elem1])])
                    c = sieved_tasks.copy()
                    c.remove(elem1)
                    for elem2 in c: 
                        obs1 *= Observable(self.n, pauli_terms=[Term(0.5, "I", [elem2]), Term(0.5, "Z", [elem2])])
                    ham = obs1 if ham is None else ham + obs1
                obs3 = Observable(self.n, pauli_terms=[Term(1, "I", [0])])
                self.H_atos += obs3 - ham
            elif self.onehot == 'quadratic':
                ham = None
                for elem in sieved_tasks:
                    if ham is None:
                        ham = Observable(len(self.instance), pauli_terms=[Term(0.5, "I", [0]), Term(-0.5, "Z", [elem])])
                    else:
                        ham += Observable(len(self.instance), pauli_terms=[Term(0.5, "I", [0]), Term(-0.5, "Z", [elem])])
                ham = Observable(len(self.instance), pauli_terms=[Term(1, "I", [0])]) - ham
                self.H_atos += ham


    def _add_precedence_constraint_atos(self):
        for current_task, next_task in zip(self.tasks, self.tasks[1:]):
            if current_task.job != next_task.job:
                continue
            for t in range(self.max_time):
                current_label = get_label(current_task, t)
                if current_label in self.absurd_times:
                    continue
                var1 = self.H_pos_by_label[current_label]
                for tt in range(min(t + current_task.duration, self.max_time)):
                    next_label = get_label(next_task, tt)
                    if next_label in self.absurd_times:
                        continue
                    var2 = self.H_pos_by_label[next_label]
                    # self.H_atos += hampy.H_x(var1, self.n).compose(hampy.H_x(var2, self.n))
                    var11 = Observable(self.n, pauli_terms=[Term(0.5, "I", [0]), Term(-0.5, "Z", [var1])])
                    var22 = Observable(self.n, pauli_terms=[Term(0.5, "I", [0]), Term(-0.5, "Z", [var2])])
                    self.H_atos += var11 * var22

    def _add_share_machine_constraint_atos(self):
        """self.csp gets the constraint: At most one task per machine per time unit
        """
        sorted_tasks = sorted(self.tasks, key=lambda x: x.machine)
        # Key wrapper for bisect function
        wrapped_tasks = KeyList(sorted_tasks, lambda x: x.machine)

        head = 0
        while head < len(sorted_tasks):

            # Find tasks that share a machine
            tail = bisect_right(wrapped_tasks, sorted_tasks[head].machine)
            same_machine_tasks = sorted_tasks[head:tail]

            # Update
            head = tail

            # No need to build coupling for a single task
            if len(same_machine_tasks) < 2:
                continue

            # Apply constraint between all tasks for each unit of time
            for task in same_machine_tasks:
                for other_task in same_machine_tasks:
                    if task.job == other_task.job and task.position == other_task.position:
                        continue

                    for t in range(self.max_time):
                        current_label = get_label(task, t)
                        if current_label in self.absurd_times:
                            continue

                        var1 = self.H_pos_by_label[current_label]

                        for tt in range(t, min(t + task.duration, self.max_time)):
                            this_label = get_label(other_task, tt)
                            if this_label in self.absurd_times:
                                continue
                            var2 = self.H_pos_by_label[this_label]

                            var11 = Observable(self.n, pauli_terms=[Term(0.5, "I", [0]), Term(-0.5, "Z", [var1])])
                            var22 = Observable(self.n, pauli_terms=[Term(0.5, "I", [0]), Term(-0.5, "Z", [var2])])
                            self.H_atos += var11 * var22
    def _remove_absurd_times(self):
        # Times that are too early for task
        predecessor_time = 0
        current_job = self.tasks[0].job
        for task in self.tasks:
            # Check if task is in current_job
            if task.job != current_job:
                predecessor_time = 0
                current_job = task.job

            for t in range(predecessor_time):
                label = get_label(task, t)
                self.absurd_times.add(label)

            predecessor_time += task.duration

        # Times that are too late for task
        # Note: we are going through the task list backwards in order to compute
        # the successor time
        # start with -1 so that we get (total task time - 1)
        successor_time = -1
        current_job = self.tasks[-1].job
        for task in self.tasks[::-1]:
            # Check if task is in current_job
            if task.job != current_job:
                successor_time = -1
                current_job = task.job

            successor_time += task.duration
            for t in range(successor_time):
                # -1 for zero-indexed time
                label = get_label(task, (self.max_time - 1) - t)
                self.absurd_times.add(label)

    def _build_variable_dict(self):
        for task in self.tasks:
            task_times = {get_label(task, t) for t in range(self.max_time)}
            for label in task_times:
                if label in self.absurd_times:
                    continue
                else:
                    self.H_pos_by_label[label] = len(self.H_pos_by_label)
                    self.H_label_by_pos[len(self.H_label_by_pos)] = label
        self.n = len(self.H_pos_by_label)

    def get_hamiltonian_qiskit(self):
        self._remove_absurd_times()
        self._build_variable_dict()
        self._add_one_start_constraint_qiskit()
        self._add_precedence_constraint_qiskit()
        self._add_share_machine_constraint_qiskit()
        # Get BQM
        # bqm = dwavebinarycsp.stitch(self.csp, **stitch_kwargs)

        # Edit BQM to encourage the shortest schedule
        # Overview of this added penalty:
        # - Want any-optimal-schedule-penalty < any-non-optimal-schedule-penalty
        # - Suppose there are N tasks that need to be scheduled and N > 0
        # - Suppose the the optimal end time for this schedule is t_N
        # - Then the worst optimal schedule would be if ALL the tasks ended at time t_N. (Since
        #   the optimal schedule is only dependent on when the LAST task is run, it is irrelevant
        #   when the first N-1 tasks end.) Note that by "worst" optimal schedule, I am merely
        #   referring to the most heavily penalized optimal schedule.
        #
        # Show math satisfies any-optimal-schedule-penalty < any-non-optimal-schedule-penalty:
        # - Penalty scheme. Each task is given the penalty: base^(task-end-time). The penalty
        #   of the entire schedule is the sum of penalties of these chosen tasks.
        # - Chose the base of my geometric series to be N+1. This simplifies the math and it will
        #   become apparent why it's handy later on.
        #
        # - Comparing the SUM of penalties between any optimal schedule (on left) with that of the
        #   WORST optimal schedule (on right). As shown below, in this penalty scheme, any optimal
        #   schedule penalty <= the worst optimal schedule.
        #     sum_i (N+1)^t_i <= N * (N+1)^t_N, where t_i the time when the task i ends  [eq 1]
        #
        # - Now let's show that all optimal schedule penalties < any non-optimal schedule penalty.
        #   We can prove this by applying eq 1 and simply proving that the worst optimal schedule
        #   penalty (below, on left) is always less than any non-optimal schedule penalty.
        #     N * (N+1)^t_N < (N+1)^(t_N + 1)
        #                               Note: t_N + 1 is the smallest end time for a non-optimal
        #                                     schedule. Hence, if t_N' is the end time of the last
        #                                     task of a non-optimal schedule, t_N + 1 <= t_N'
        #                   <= (N+1)^t_N'
        #                   < sum^(N-1) (N+1)^t_i' + (N+1)^t_N'
        #                   = sum^N (N+1)^t_i'
        #                               Note: sum^N (N+1)^t' is the sum of penalties for a
        #                                     non-optimal schedule
        #
        # - Therefore, with this penalty scheme, all optimal solution penalties < any non-optimal
        #   solution penalties

        # Get BQM
        decision_hamiltonian = self.H_qiskit.simplify().copy()

        base = len(self.last_task_indices) + 1  # Base for exponent
        # Get our pruned (remove_absurd_times) variable list so we don't undo pruning
        # pruned_variables = list(bqm.variables)

        for i in self.last_task_indices:
            task = self.tasks[i]

            for t in range(self.max_time):
                end_time = t + task.duration

                # Check task's end time; do not add in absurd times
                if end_time > self.max_time:
                    continue

                # Add bias to variable
                bias = 2 * base ** (end_time - self.max_time)
                # bias = base**(end_time - 5)
                # bias = base ** (end_time)
                label = get_label(task, t)
                if label in self.absurd_times:
                    continue

                var = self.H_pos_by_label[label]
                self.H_qiskit += hampy.H_x(var, self.n)
        # self.H += h / (base * len(self.last_task_indices))

        # Get BQM
        optimization_hamiltonian = self.H_qiskit.simplify().copy()
        return decision_hamiltonian, optimization_hamiltonian, self.H_pos_by_label.copy(), self.H_label_by_pos.copy()
    
    def get_hamiltonian_atos(self):
        self._remove_absurd_times()
        self._build_variable_dict()
        self._add_one_start_constraint_atos()
        self._add_precedence_constraint_atos()
        self._add_share_machine_constraint_atos()
        # Get BQM
        # bqm = dwavebinarycsp.stitch(self.csp, **stitch_kwargs)

        # Edit BQM to encourage the shortest schedule
        # Overview of this added penalty:
        # - Want any-optimal-schedule-penalty < any-non-optimal-schedule-penalty
        # - Suppose there are N tasks that need to be scheduled and N > 0
        # - Suppose the the optimal end time for this schedule is t_N
        # - Then the worst optimal schedule would be if ALL the tasks ended at time t_N. (Since
        #   the optimal schedule is only dependent on when the LAST task is run, it is irrelevant
        #   when the first N-1 tasks end.) Note that by "worst" optimal schedule, I am merely
        #   referring to the most heavily penalized optimal schedule.
        #
        # Show math satisfies any-optimal-schedule-penalty < any-non-optimal-schedule-penalty:
        # - Penalty scheme. Each task is given the penalty: base^(task-end-time). The penalty
        #   of the entire schedule is the sum of penalties of these chosen tasks.
        # - Chose the base of my geometric series to be N+1. This simplifies the math and it will
        #   become apparent why it's handy later on.
        #
        # - Comparing the SUM of penalties between any optimal schedule (on left) with that of the
        #   WORST optimal schedule (on right). As shown below, in this penalty scheme, any optimal
        #   schedule penalty <= the worst optimal schedule.
        #     sum_i (N+1)^t_i <= N * (N+1)^t_N, where t_i the time when the task i ends  [eq 1]
        #
        # - Now let's show that all optimal schedule penalties < any non-optimal schedule penalty.
        #   We can prove this by applying eq 1 and simply proving that the worst optimal schedule
        #   penalty (below, on left) is always less than any non-optimal schedule penalty.
        #     N * (N+1)^t_N < (N+1)^(t_N + 1)
        #                               Note: t_N + 1 is the smallest end time for a non-optimal
        #                                     schedule. Hence, if t_N' is the end time of the last
        #                                     task of a non-optimal schedule, t_N + 1 <= t_N'
        #                   <= (N+1)^t_N'
        #                   < sum^(N-1) (N+1)^t_i' + (N+1)^t_N'
        #                   = sum^N (N+1)^t_i'
        #                               Note: sum^N (N+1)^t' is the sum of penalties for a
        #                                     non-optimal schedule
        #
        # - Therefore, with this penalty scheme, all optimal solution penalties < any non-optimal
        #   solution penalties

        # Get BQM
        decision_hamiltonian = self.H_atos.copy()

        base = len(self.last_task_indices) + 1  # Base for exponent
        # Get our pruned (remove_absurd_times) variable list so we don't undo pruning
        # pruned_variables = list(bqm.variables)

        for i in self.last_task_indices:
            task = self.tasks[i]

            for t in range(self.max_time):
                end_time = t + task.duration

                # Check task's end time; do not add in absurd times
                if end_time > self.max_time:
                    continue

                # Add bias to variable
                bias = 2 * base ** (end_time - self.max_time)
                # bias = base**(end_time - 5)
                # bias = base ** (end_time)
                label = get_label(task, t)
                if label in self.absurd_times:
                    continue

                var = self.H_pos_by_label[label]
                self.H_atos += Observable(self.n, pauli_terms=[Term(0.5, "I", [0]), Term(-0.5, "Z", [var])])

        # self.H += h / (base * len(self.last_task_indices))

        # Get BQM
        optimization_hamiltonian = self.H_atos.copy()
        return decision_hamiltonian, optimization_hamiltonian, self.H_pos_by_label.copy(), self.H_label_by_pos.copy()