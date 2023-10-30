""" Basic problems for Orca """
import numpy as np

from jssp.pyqubo_scheduler import get_jss_bqm
from problems import MaxCut, EC, JSSP
from .orca_templates import OrcaStuff


class MaxCutOrca(MaxCut, OrcaStuff):
    def get_qubo_fn(self, Q):
        def qubo_fn(bin_vec):
            return np.dot(bin_vec, np.dot(Q, bin_vec))

        return qubo_fn

    def get_orca_qubo(self):
        """ Returns Qubo function """
        Q = np.zeros((6, 6))
        for (i, j) in self.instance.edges:
            Q[i, i] += -1
            Q[j, j] += -1
            Q[i, j] += 1
            Q[j, i] += 1

        return self.get_qubo_fn, Q


class ECOrca(EC, OrcaStuff):
    gamma = 1
    delta = 0.05
    def qubo_fn_fact(self, Q):
        def qubo_fn(bin_vec):
            return np.dot(bin_vec, np.dot(Q, bin_vec)) + self.gamma * (self.num_elements - np.sum(np.array(self.len_routes) * np.array(bin_vec)))**2 - self.delta * np.sum(bin_vec)
        return qubo_fn

    def Jrr(self, route1, route2):
        s = len(set(route1).intersection(set(route2)))
        return s / 2

    def hr(self, route1, routes):
        i_sum = 0
        for r in routes:
            i_sum += len(set(r).intersection(set(route1)))
        s = i_sum - len(route1) * 2
        return s / 2

    def calculate_jrr_hr(self):
        Jrr_dict = dict()
        indices = np.triu_indices(len(self.instance), 1)
        for i1, i2 in zip(indices[0], indices[1]):
            Jrr_dict[(i1, i2)] = self.Jrr(self.instance[i1], self.instance[i2])

        hr_dict = dict()
        for i in range(len(self.instance)):
            hr_dict[i] = self.hr(self.instance[i], self.instance)

        return Jrr_dict, hr_dict

    def calculate_lengths_tab(self):
        tab = []
        for route in self.instance:
            tab.append(len(route))
        return tab

    def calculate_num_elements(self):
        d = dict()
        for route in self.instance:
            for el in route:
                d[el] = 1
        return len(d)

    def calculate_instance_size(self):
        # Calculate instance size for training
        return len(self.instance)

    def get_orca_qubo(self):
        self.num_elements = self.calculate_num_elements()
        self.len_routes = self.calculate_lengths_tab()
        Q = np.zeros((len(self.instance), len(self.instance)))
        self.Jrr_dict, self.hr_dict = self.calculate_jrr_hr()
        for i in self.Jrr_dict:
            # print(i)
            Q[i[0]][i[1]] = self.Jrr_dict[i]
            Q[i[1]][i[0]] = Q[i[0]][i[1]]

        for i in self.hr_dict:
            Q[i][i] = -self.hr_dict[i]

        return self.qubo_fn_fact, Q
