''' Example of how Quantum Launcher works'''
from templates import QuantumLauncher
from problems import JSSP
from qiskit_stuff.algorithms import FALQON
from qiskit_stuff.backend import QiskitBackend


def main():
    """ main """
    pr = JSSP(3, 'exact', instance_name='toy', optimization_problem=True)
    alg = FALQON(delta_t=0.03, beta_0=0, n=10)
    backend = QiskitBackend('local_simulator')
    launcher = QuantumLauncher(pr, alg, backend)
    print(launcher.run())


if __name__ == '__main__':
    main()
