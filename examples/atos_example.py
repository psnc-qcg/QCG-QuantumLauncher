''' Quantum Launcher for Atos '''
import atos_routines
from problems import EC
from base import QuantumLauncher


def main():
    ''' main '''
    pr = EC('exact', instance_name='toy')
    alg = atos_routines.QAOA()
    backend = atos_routines.AtosBackend('local')
    launcher = QuantumLauncher(pr, alg, backend)
    print(launcher._run())


if __name__ == '__main__':
    main()
