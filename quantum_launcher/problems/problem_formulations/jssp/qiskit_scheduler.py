from __future__ import print_function

from bisect import bisect_right

import quantum_launcher.hampy as hampy

from .scheduler import JobShopScheduler, KeyList, get_label


def get_jss_hamiltonian(job_dict, max_time, onehot):
    scheduler = QiskitScheduler(job_dict, max_time, onehot)
    return scheduler.get_hamiltonian()


class QiskitScheduler(JobShopScheduler):

    def __init__(self, job_dict, max_time=None, onehot='exact'):
        super().__init__(job_dict, max_time)
        self.H_pos_by_label = dict()
        self.H_label_by_pos = dict()
        self.onehot = onehot

    def _add_one_start_constraint(self, lagrange_one_hot=1):
        for task in self.tasks:
            task_times = {get_label(task, t) for t in range(self.max_time)}
            onehot_tasks = set()
            for label in task_times:
                if label in self.absurd_times:
                    continue
                else:
                    onehot_tasks.add(self.H_pos_by_label[label])
            if self.onehot == 'exact':
                self.H += hampy.Ham_not(hampy.H_one_in_n(onehot_tasks, self.n))
            elif self.onehot == 'quadratic':
                self.H += hampy.quadratic_onehot(onehot_tasks, self.n)

    def _add_precedence_constraint(self, lagrange_precedence=1):
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
                    self.H += hampy.H_x(var1,
                                        self.n).compose(hampy.H_x(var2, self.n))

    def _add_share_machine_constraint(self, lagrange_share=1):
        sorted_tasks = sorted(self.tasks, key=lambda x: x.machine)
        wrapped_tasks = KeyList(sorted_tasks, lambda x: x.machine)

        head = 0
        while head < len(sorted_tasks):

            tail = bisect_right(wrapped_tasks, sorted_tasks[head].machine)
            same_machine_tasks = sorted_tasks[head:tail]

            head = tail

            if len(same_machine_tasks) < 2:
                continue

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

                            self.H += hampy.H_x(var1,
                                                self.n).compose(hampy.H_x(var2, self.n))

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

    def get_hamiltonian(self):
        self._remove_absurd_times({}, {}, [])
        self._build_variable_dict()
        self._add_one_start_constraint()
        self._add_precedence_constraint()
        self._add_share_machine_constraint()
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
        decision_hamiltonian = self.H.simplify().copy()

        base = len(self.last_task_indices) + 1  # Base for exponent
        # Get our pruned (remove_absurd_times) variable list so we don't undo pruning
        # pruned_variables = list(bqm.variables)

        h = 0

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
                self.H += hampy.H_x(var, self.n)
        # self.H += h / (base * len(self.last_task_indices))

        # Get BQM
        optimization_hamiltonian = self.H.simplify().copy()
        return decision_hamiltonian, optimization_hamiltonian, self.H_pos_by_label.copy(), self.H_label_by_pos.copy()
