''' Quantum Launcher for Atos '''
import atos_stuff
from problems import EC
from templates import QuantumLauncher


def main():
    ''' main '''
    pr = EC('exact', instance_name='toy')
    alg = atos_stuff.QAOA2()
    backend = atos_stuff.AtosBackend('local')
    launcher = QuantumLauncher(pr, alg, backend)
    print(launcher._run())


if __name__ == '__main__':
    main()
