''' Example of how Quantum Launcher works'''
from problems import JSSP
from qiskit_routines.algorithms import FALQON
from qiskit_routines.backend import QiskitBackend
from templates import QuantumLauncher


def main():
    """ main """
    pr = JSSP(3, 'exact', instance_name='toy', optimization_problem=True)
    alg = FALQON(delta_t=0.03, beta_0=0, n=2)
    backend = QiskitBackend('local_simulator')
    launcher = QuantumLauncher(pr, alg, backend)
    print(launcher.process(save_pickle=True))


if __name__ == '__main__':
    main()
