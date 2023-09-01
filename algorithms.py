''' file with algorithms subclasses '''

import numpy as np
from qiskit.circuit import ParameterVector
from qiskit.circuit.library import PauliEvolutionGate
from qiskit.opflow import H
from qiskit.providers.fake_provider import FakeSherbrooke
from qiskit.quantum_info import SparsePauliOp
from qiskit_aer.noise import NoiseModel
from qiskit_algorithms import QAOA

from templates import Algorithm, Backend


def commutator(op_a: SparsePauliOp, op_b: SparsePauliOp) -> SparsePauliOp:
    ''' Commutator '''
    return op_a @ op_b - op_b @ op_a


'''fake_backend = FakeSherbrooke()
noise_model = NoiseModel.from_backend(fake_backend)
options = Options()
options.simulator = {
    "noise_model": noise_model,
    "coupling_map": fake_backend.coupling_map,
    "seed_simulator": 42
}
options.resilience_level = 1
options.optimization_level = 1'''


class QAOA2(Algorithm):
    ''' Algorithm class with QAOA '''

    def __init__(self, p: int = 1, aux=None):
        self.name = 'qaoa'
        self.path_name = f'{self.name}-{p}'
        self.aux = aux
        self.p: int = p

    def run(self, hamiltonian: SparsePauliOp, backend:Backend) -> dict:
        ''' Runs the QAOA algorithm '''
        energies = []

        def qaoa_callback(evaluation_count, params, mean, std):
            energies.append(mean)

        sampler = backend.get_sampler()
        optimizer = backend.get_optimizer()

        qaoa = QAOA(sampler, optimizer, reps=self.p, callback=qaoa_callback)
        qaoa_result = qaoa.compute_minimum_eigenvalue(hamiltonian, self.aux)
        result = {'qaoa_res': qaoa_result,
                  'energy': qaoa_result.eigenvalue,
                  'depth': qaoa.ansatz.depth(),
                  'energies': energies}
        return result


class FALQON(Algorithm):
    ''' Algorithm class with FALQON '''

    def __init__(self, driver_h=None, delta_t=0, beta_0=0, n=1):

        self.name = 'falqon'
        self.path_name = f'{self.name}-{n}-{delta_t}-{beta_0}'
        self.driver_h = driver_h
        self.delta_t = delta_t
        self.beta_0 = beta_0
        self.n = n
        self.cost_h = None
        self.n_qubits: int = 0

    def run(self, hamiltonian: SparsePauliOp, backend:Backend):
        ''' run falqon '''
        # TODO implement aux operator
        self.cost_h = hamiltonian
        self.n_qubits = hamiltonian.num_qubits
        if self.driver_h is None:
            self.driver_h = SparsePauliOp.from_sparse_list(
                [("X", [i], 1) for i in range(self.n_qubits)], num_qubits=self.n_qubits)

        betas = [self.beta_0]
        energies = []
        circuit_depths = []

        estimator = backend.get_estimator()
        sampler = backend.get_sampler()

        best_sample, last_sample = self.falqon_subroutine(estimator,
                                                    sampler, energies, betas, circuit_depths)

        result = {'betas': betas,
                  'energies': energies,
                  'circuit_depths': circuit_depths,
                  'best_sample': best_sample,
                  'last_sample': last_sample,
                  'n': self.n,
                  'delta_t': self.delta_t,
                  'beta_0': self.beta_0,
                  'energy': min(energies)}

        return result

    def build_ansatz(self, betas):
        ''' building ansatz circuit '''
        circ = (H ^ self.cost_h.num_qubits).to_circuit()
        params = ParameterVector("beta", length=len(betas))
        for param in params:
            circ.append(PauliEvolutionGate(self.cost_h, time=self.delta_t), circ.qubits)
            circ.append(PauliEvolutionGate(self.driver_h, time=self.delta_t * param), circ.qubits)
        return circ

    def falqon_subroutine(self, estimator,
                          sampler, energies, betas, circuit_depths):
        ''' subroutine for falqon '''
        for i in range(self.n):
            betas, energy, depth = self.run_falqon(betas, estimator)
            print(i, energy)
            energies.append(energy)
            circuit_depths.append(depth)
        argmin = np.argmin(np.asarray(energies))
        best_sample = self.sample_at(betas[:argmin], sampler)
        last_sample = self.sample_at(betas, sampler)
        return best_sample, last_sample

    def run_falqon(self, betas, estimator):
        ''' Method to run FALQON algorithm '''
        ansatz = self.build_ansatz(betas)
        comm_h = complex(0, 1) * commutator(self.driver_h, self.cost_h)
        beta = -1 * estimator.run(ansatz, comm_h, betas).result().values[0]
        betas.append(beta)

        ansatz = self.build_ansatz(betas)
        energy = estimator.run(ansatz, self.cost_h, betas).result().values[0]

        return betas, energy, ansatz.depth()

    def sample_at(self, betas, sampler):
        ''' Not sure yet '''
        ansatz = self.build_ansatz(betas)
        ansatz.measure_all()
        res = sampler.run(ansatz, betas).result()
        return res
