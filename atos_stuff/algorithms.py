""" file with orca algorithms subclasses """

from qat.plugins import ScipyMinimizePlugin
from qat.qpus import get_default_qpu
from qat.vsolve.ansatz import AnsatzFactory

from templates import Problem, Algorithm
from .atos_templates import AtosStuff
from .backend import AtosBackend


class QAOA2(Algorithm, AtosStuff):
    """ Algorithm class with QAOA """

    def __init__(self, p: int = 1, aux=None):
        super().__init__()
        self.name = 'qaoa'
        self.aux = aux
        self.p: int = p
        self.parameters = ['p']

    def _get_path(self) -> str:
        return f'{self.name}@{self.p}'

    def run(self, problem: Problem, backend: AtosBackend) -> dict:

        """ Runs the QAOA algorithm """
        observable = problem.get_atos_hamiltonian()

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
