""" file with orca algorithms subclasses """

from qat.plugins import ScipyMinimizePlugin
from qat.qpus import get_default_qpu
from qat.vsolve.ansatz import AnsatzFactory

from atos_stuff.backend import AtosBackend
from templates import Problem, Algorithm


class QAOA2(Algorithm):
    """ Algorithm class with QAOA """

    def __init__(self, p: int = 1, aux=None):
        self.name = 'qaoa'
        self.aux = aux
        self.p: int = p
        self.parameters = ['p']
        self._set_path()

    def _set_path(self) -> None:
        self.path = f'{self.name}@{self.p}'

    def run(self, problem: Problem, backend: AtosBackend) -> dict:

        """ Runs the QAOA algorithm """
        observable = self.get_problem_data(problem)

        circuit = AnsatzFactory.qaoa_circuit(observable, self.p, strategy='default')

        job = circuit.to_job(observable=observable)
        qpu = get_default_qpu()
        stack = ScipyMinimizePlugin(method="COBYLA",
                                    tol=1e-5,
                                    options={"maxiter": 200}) | qpu
        optimization_result = stack.submit(job)
        sjob = job(**eval(optimization_result.meta_data["parameter_map"]))
        sjob = sjob.circuit.to_job(nbshots=1024)
        sample_result = stack.submit(sjob)
        
        dict_results = {"optimization_result": optimization_result, "sample_result": sample_result}

        return dict_results

    def check_problem(self, problem: Problem) -> bool:
        """ Check if the problem implements get_hamiltonian method"""
        return callable(getattr(problem, 'get_atos_hamiltonian', False))

    def get_problem_data(self, problem: Problem):
        if self.check_problem(problem):
            return problem.get_atos_hamiltonian()
        else:
            raise NotImplementedError('The problem does not have atos hamiltonian getter implemented')