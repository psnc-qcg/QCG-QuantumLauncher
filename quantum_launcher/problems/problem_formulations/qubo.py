""" Basic problems for Orca """
import numpy as np
from qiskit_optimization.converters import QuadraticProgramToQubo
from qiskit_optimization.translators import from_ising
from typing import Tuple
from quantum_launcher.problems.problem_formulations.jssp.pyqubo_scheduler import get_jss_bqm
from quantum_launcher.problems.problem_initialization.maxcut import MaxCut
from quantum_launcher.problems.problem_initialization.ec import EC
from quantum_launcher.problems.problem_initialization.jssp import JSSP
from quantum_launcher.problems.problem_initialization.qatm import QATM
from quantum_launcher.problems.problem_initialization.raw import Raw

from quantum_launcher.base import formatter, adapter


@adapter('qubo', 'qubo_fn')
def get_qubo_fn(qubo):
    # TODO check
    def qubo_fn(bin_vec):
        return np.dot(bin_vec, np.dot(qubo, bin_vec))
    return qubo_fn


@adapter('hamiltonian', 'qubo')
def get_orca_qubo(self):
    hamiltonian = self.get_qiskit_hamiltonian()
    qp = from_ising(hamiltonian)
    conv = QuadraticProgramToQubo()
    qubo = conv.convert(qp).objective
    return None, qubo.quadratic.to_array()


@formatter(MaxCut, 'qubo')
def get_orca_qubo(problem: MaxCut):
    """ Returns Qubo function """
    Q = np.zeros((6, 6))
    for (i, j) in problem.instance.edges:
        Q[i, i] += -1
        Q[j, j] += -1
        Q[i, j] += 1
        Q[j, i] += 1

    return Q, 0


class ECOrca:
    gamma = 1
    delta = 0.05

    def Jrr(self, route1, route2):
        s = len(set(route1).intersection(set(route2)))
        return s / 2

    def hr(self, route1, routes):
        i_sum = 0
        for r in routes:
            i_sum += len(set(r).intersection(set(route1)))
        s = i_sum - len(route1) * 2
        return s / 2

    def calculate_jrr_hr(self, problem: EC):
        Jrr_dict = dict()
        indices = np.triu_indices(len(problem.instance), 1)
        for i1, i2 in zip(indices[0], indices[1]):
            Jrr_dict[(i1, i2)] = self.Jrr(
                problem.instance[i1], problem.instance[i2])

        hr_dict = dict()
        for i in range(len(problem.instance)):
            hr_dict[i] = self.hr(problem.instance[i], problem.instance)

        return Jrr_dict, hr_dict

    def calculate_lengths_tab(self, problem: EC):
        tab = []
        for route in problem.instance:
            tab.append(len(route))
        return tab

    def calculate_num_elements(self, problem: EC):
        d = dict()
        for route in problem.instance:
            for el in route:
                d[el] = 1
        return len(d)

    def calculate_instance_size(self, problem: EC):
        # Calculate instance size for training
        return len(problem.instance)


@formatter(EC, 'qubo')
class EC_QUBO(ECOrca):
    def __call__(self, problem: EC):
        self.num_elements = self.calculate_num_elements(problem)
        self.len_routes = self.calculate_lengths_tab(problem)
        Q = np.zeros((len(problem.instance), len(problem.instance)))
        self.Jrr_dict, self.hr_dict = self.calculate_jrr_hr(problem)
        for i in self.Jrr_dict:
            Q[i[0]][i[1]] = self.Jrr_dict[i]
            Q[i[1]][i[0]] = Q[i[0]][i[1]]

        for i in self.hr_dict:
            Q[i][i] = -self.hr_dict[i]

        return Q, 0


@formatter(EC, 'qubo_fn')
class EC_FN(ECOrca):
    # TODO fix and check
    def __call__(self, Q):
        def qubo_fn(bin_vec):
            return np.dot(bin_vec, np.dot(Q, bin_vec)) + self.gamma * (self.num_elements - np.sum(np.array(self.len_routes) * np.array(bin_vec)))**2 - self.delta * np.sum(bin_vec)
        return qubo_fn


class JSSPOrca:
    gamma = 1
    lagrange_one_hot = 1
    lagrange_precedence = 2
    lagrange_share = 5

    def _fix_get_jss_bqm(self, instance, max_time, config,
                         lagrange_one_hot=0,
                         lagrange_precedence=0,
                         lagrange_share=0) -> Tuple[dict, list, None]:
        pre_result = get_jss_bqm(instance, max_time, config,
                                 lagrange_one_hot=lagrange_one_hot,
                                 lagrange_precedence=lagrange_precedence,
                                 lagrange_share=lagrange_share)
        result = (pre_result.spin.linear, pre_result.spin.quadratic,
                  pre_result.spin.offset)  # I need to change it into dict somehow
        return result, list(result[0].keys()), None

    def calculate_instance_size(self, problem: JSSP):
        # Calculate instance size for training
        _, variables, _ = self._fix_get_jss_bqm(problem.instance, problem.max_time, self.config,
                                                lagrange_one_hot=self.lagrange_one_hot,
                                                lagrange_precedence=self.lagrange_precedence,
                                                lagrange_share=self.lagrange_share)
        return len(variables)

    def get_len_all_jobs(self, problem: JSSP):
        result = 0
        for job in problem.instance.values():
            result += len(job)
        return result

    def one_hot_to_jobs(self, binary_vector, problem: JSSP):
        actually_its_qubo, variables, model = self._fix_get_jss_bqm(problem.instance, problem.max_time, self.config,
                                                                    lagrange_one_hot=self.lagrange_one_hot,
                                                                    lagrange_precedence=self.lagrange_precedence,
                                                                    lagrange_share=self.lagrange_share)
        result = [variables[i]
                  for i in range(len(variables)) if binary_vector[i] == 1]
        return result

    def _set_config(self):
        self.config = {}
        self.config['parameters'] = {}
        self.config['parameters']['job_shop_scheduler'] = {}
        self.config['parameters']['job_shop_scheduler']['problem_version'] = "optimization"


@formatter(JSSP, 'qubo')
class JSSP_QUBO(JSSPOrca):
    def __call__(self, problem: JSSP):
        # Define the matrix Q used for QUBO
        self.config = {}
        self.instance_size = self.calculate_instance_size(problem)
        self._set_config()
        actually_its_qubo, variables, model = self._fix_get_jss_bqm(problem.instance, problem.max_time, self.config,
                                                                    lagrange_one_hot=self.lagrange_one_hot,
                                                                    lagrange_precedence=self.lagrange_precedence,
                                                                    lagrange_share=self.lagrange_share)
        reverse_dict_map = {v: i for i, v in enumerate(variables)}

        Q = np.zeros((self.instance_size, self.instance_size))

        for (label_i, label_j), value in actually_its_qubo[1].items():
            i = reverse_dict_map[label_i]
            j = reverse_dict_map[label_j]
            Q[i, j] += value
            Q[j, i] = Q[i, j]

        for label_i, value in actually_its_qubo[0].items():
            i = reverse_dict_map[label_i]
            Q[i, i] += value
        return Q / max(np.max(Q), -np.min(Q)), 0


@formatter(JSSP, 'qubo_fn')
class JSSP_FN(JSSPOrca):
    def qubo_fn_fact(self, Q):
        # TODO fix and check
        def qubo_fn(bin_vec):
            return np.dot(bin_vec, np.dot(Q, bin_vec)) + self.gamma * (np.sum(bin_vec) - self.get_len_all_jobs()) ** 2
        return qubo_fn


@formatter(Raw, 'qubo')
def get_orca_qubo(problem: Raw):
    return problem.instance
