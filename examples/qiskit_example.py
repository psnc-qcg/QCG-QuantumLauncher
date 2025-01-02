''' Example of how Quantum Launcher works'''
from quantum_launcher import *
from quantum_launcher.routines.qiskit_routines import QiskitBackend, QAOA

def main():
    """ main """
    pr = problems.JSSP(3, 'exact', instance_name='toy',
                          optimization_problem=True)
    alg = QAOA()
    backend = QiskitBackend('local_simulator')
    launcher = QuantumLauncher(pr, alg, backend)
    print(launcher.process(save_json=True))


if __name__ == '__main__':
    main()
