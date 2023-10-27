''' Quantum Launcher for Atos '''
from templates import QuantumLauncher
import atos_stuff
from problems import EC


def main():
    ''' main '''
    pr = EC('exact', instance_name='toy')
    alg = atos_stuff.QAOA2()
    backend = atos_stuff.AtosBackend('local')
    launcher = QuantumLauncher(pr, alg, backend)
    print(launcher.run())


if __name__ == '__main__':
    main()
