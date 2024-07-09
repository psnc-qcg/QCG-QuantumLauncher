from __future__ import print_function

from bisect import bisect_right

# from pyqubo import Binary
from .Binary import Binary

from .scheduler import JobShopScheduler, KeyList, get_label


def get_jss_bqm(job_dict, max_time, disable_till=None, disable_since=None, disabled_variables=None, lagrange_one_hot=3,
                lagrange_precedence=1, lagrange_share=2):
    if disable_till is None:
        disable_till = {}
    if disable_since is None:
        disable_since = {}
    if disabled_variables is None:
        disabled_variables = []

    scheduler = DWaveScheduler(job_dict, max_time)
    return scheduler.get_bqm(disable_till, disable_since, disabled_variables,
                             lagrange_one_hot,
                             lagrange_precedence,
                             lagrange_share)


class DWaveScheduler(JobShopScheduler):

    def __init__(self, job_dict, max_time=None):
        super().__init__(job_dict, max_time)

    def _add_one_start_constraint(self, lagrange_one_hot=1):
        """self.csp gets the constraint: A task can start once and only once
        """
        for task in self.tasks:
            task_times = {get_label(task, t) for t in range(self.max_time)}
            H_term = 0
            for label in task_times:
                if label in self.absurd_times:
                    continue
                if label not in self.H_vars:
                    var = Binary(label)
                    self.H_vars[label] = var
                else:
                    var = self.H_vars[label]
                H_term += var
            self.H += lagrange_one_hot * ((1 - H_term) ** 2)

    def _add_precedence_constraint(self, lagrange_precedence=1):
        """self.csp gets the constraint: Task must follow a particular order.
         Note: assumes self.tasks are sorted by jobs and then by position
        """
        for current_task, next_task in zip(self.tasks, self.tasks[1:]):
            if current_task.job != next_task.job:
                continue

            # Forming constraints with the relevant times of the next task
            for t in range(self.max_time):
                current_label = get_label(current_task, t)
                if current_label in self.absurd_times:
                    continue

                if current_label not in self.H_vars:
                    var1 = Binary(current_label)
                    self.H_vars[current_label] = var1
                else:
                    var1 = self.H_vars[current_label]

                for tt in range(min(t + current_task.duration, self.max_time)):

                    next_label = get_label(next_task, tt)
                    if next_label in self.absurd_times:
                        continue
                    if next_label not in self.H_vars:
                        var2 = Binary(next_label)
                        self.H_vars[next_label] = var2
                    else:
                        var2 = self.H_vars[next_label]

                    self.H += lagrange_precedence * var1 * var2

    def _add_share_machine_constraint(self, lagrange_share=1):
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

                        if current_label not in self.H_vars:
                            var1 = Binary(current_label)
                            self.H_vars[current_label] = var1
                        else:
                            var1 = self.H_vars[current_label]

                        for tt in range(t, min(t + task.duration, self.max_time)):
                            this_label = get_label(other_task, tt)
                            if this_label in self.absurd_times:
                                continue
                            if this_label not in self.H_vars:
                                var2 = Binary(this_label)
                                self.H_vars[this_label] = var2
                            else:
                                var2 = self.H_vars[this_label]

                            self.H += lagrange_share * var1 * var2

    def get_bqm(self, disable_till, disable_since, disabled_variables,
                lagrange_one_hot, lagrange_precedence, lagrange_share):
        """Returns a BQM to the Job Shop Scheduling problem.  """

        # Apply constraints to self.csp
        self._remove_absurd_times(
            disable_till, disable_since, disabled_variables)
        self._add_one_start_constraint(lagrange_one_hot)
        self._add_precedence_constraint(lagrange_precedence)
        self._add_share_machine_constraint(lagrange_share)
        # Get BQM
        # bqm = dwaveBinarycsp.stitch(self.csp, **stitch_kwargs)

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
                label = get_label(task, t)
                if label in self.absurd_times:
                    continue
                if label not in self.H_vars:
                    var = Binary(label)
                    self.H_vars[label] = var
                else:
                    var = self.H_vars[label]
                self.H += var * bias

        # Get BQM
        self.model = self.H.compile()
        bqm = self.model.to_bqm()
        return bqm
