''' file with orca algorithms subclasses '''

from qat.plugins import ScipyMinimizePlugin
from qat.qpus import get_default_qpu
from qat.vsolve.ansatz import AnsatzFactory

from atos_stuff.backend import AtosBackend
from templates import Problem, Algorithm


class QAOA2(Algorithm):
    ''' Algorithm class with QAOA '''

    def __init__(self, p: int = 1, aux=None):
        self.name = 'qaoa'
        self.path_name = f'{self.name}@{p}'
        self.aux = aux
        self.p: int = p
        self.parameters = ['p']

    def run(self, problem: Problem, backend: AtosBackend) -> dict:
        
        ''' Runs the QAOA algorithm '''
        observable = self.get_problem_data(problem)
        circuit = AnsatzFactory.qaoa_circuit(observable, self.p, strategy='default')
        qpu = get_default_qpu()
        stack = ScipyMinimizePlugin(method="COBYLA",
                                    tol=1e-5, 
                                    options={"maxiter": 200}) | qpu
                                    
        job = circuit.to_job(observable=observable)
        result = qpu.submit(job)
        sjob = job(**eval(result.meta_data["parameter_map"]))
        sjob = sjob.circuit.to_job(nbshots=1024)
        sresult = qpu.submit(sjob)
        
        return sresult

    def check_problem(self, problem: Problem) -> bool:
        ''' Check if the problem implements get_hamiltonian method'''
        return callable(getattr(problem, 'get_atos_hamiltonian', False))

    def get_problem_data(self, problem: Problem):
        if self.check_problem(problem):
            return problem.get_atos_hamiltonian()
        else:
            raise NotImplementedError('The problem does not have atos hemiltonian getter implemented')
