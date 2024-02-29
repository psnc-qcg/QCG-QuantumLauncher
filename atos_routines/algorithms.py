""" file with orca algorithms subclasses """

from qat.plugins import ScipyMinimizePlugin
from qat.qpus import get_default_qpu, CLinalg
from qat.vsolve.ansatz import AnsatzFactory

from templates import Problem, Algorithm
from .atos_templates import AtosRoutine
from .backend import AtosBackend


class QAOA(Algorithm, AtosRoutine):
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
        sjob = sjob.circuit.to_job(nbshots=4096)
        sample_result = CLinalg().submit(sjob)


        from qiskit_algorithms.minimum_eigensolvers.diagonal_estimator import _evaluate_sparsepauli
        cheating = {
            sample.state.state: (sample.probability, _evaluate_sparsepauli(sample.state.state, problem.get_qiskit_hamiltonian()))
            for sample in sample_result.raw_data
        }

        dict_results = {"optimization_result": optimization_result, "sample_result": sample_result,
                        "cheating": cheating}

        return dict_results
