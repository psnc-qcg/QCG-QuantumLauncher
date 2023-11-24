""" File for testing all qiskit problems """
try:
    from problems import EC, JSSP, MaxCut, QATM
    from templates import QuantumLauncher
    from qiskit_stuff import *
except Exception as ex:
    print('\033[91mImport Error\033[0m')
    print(ex)

TESTING_DIR = 'testing'


def test_ec():
    """ Testing function for Exact Cover """
    try:
        pr = EC('exact')
        pr.set_instance(instance_name='toy', instance=None)
        qaoa = QAOA2(p=3, alternating_ansatz=True)
        backend = QiskitBackend('local_simulator')
        launcher = QuantumLauncher(pr, qaoa, backend, path=TESTING_DIR)

        inform = launcher.process(save_pickle=True, save_txt=True)
        if inform is None:
            raise ValueError('The Output is empty')
        print('\033[92mExact Cover finished properly\033[0m')
    except Exception as ex:
        print('\033[91mSomething with EC problem/QAOA went wrong\033[0m')
        print(ex)


def test_jssp():
    """ Testing function for Job Shop Shedueling Problem """
    try:
        pr = JSSP(3, 'exact', instance_name='toy', optimization_problem=True)
        qaoa = QAOA2(p=3)
        backend = QiskitBackend('local_simulator')
        launcher = QuantumLauncher(pr, qaoa, backend, path=TESTING_DIR)

        inform = launcher.process(save_pickle=True)
        if inform is None:
            raise ValueError('The Output is empty')
        print('\033[92mJSSP finished properly\033[0m')
    except Exception as ex:
        print('\033[91mSomething with JSSP problem/QAOA went wrong\033[0m')
        print(ex)


def test_maxcut():
    """ Testing function for Max Cut """
    try:
        pr = MaxCut()
        pr.set_instance(instance_name='default')
        qaoa = QAOA2(p=3)
        backend = QiskitBackend('local_simulator')
        launcher = QuantumLauncher(pr, qaoa, backend, path=TESTING_DIR)

        inform = launcher.process(save_pickle=True)
        if inform is None:
            raise ValueError('The Output is empty')
        print('\033[92mMaxCut finished properly\033[0m')
    except Exception as ex:
        print('\033[91mSomething with MaxCut problem/QAOA went wrong\033[0m')
        print(ex)


def test_qatm():
    """ Testing function for QATM """
    try:
        pr = QATM('exact', instance_name='RCP_3.txt')
        pr.read_instance(instance_name='RCP_3.txt', instance_path='data/qatm/')
    except Exception as ex:
        print('\033[91mSomething with QATM problem (most likely lack of data file)\033[0m')
        print(ex)
    try:
        qaoa = QAOA2(p=3)
        backend = QiskitBackend('local_simulator')
        launcher = QuantumLauncher(pr, qaoa, backend, path=TESTING_DIR)

        inform = launcher.process(save_pickle=True)
        if inform is None:
            raise ValueError('The Output is empty')
        print('\033[92mQATM finished properly\033[0m')
    except Exception as ex:
        print('\033[91mSomething with QATM problem/QAOA went wrong\033[0m')
        print(ex)


def test_falqon():
    """ Testing function for Falqon, using Exact Cover """
    try:
        pr = EC('exact', instance_name='toy')
        falqon = FALQON()
        backend = QiskitBackend('local_simulator')
        launcher = QuantumLauncher(pr, falqon, backend, path=TESTING_DIR)

        inform = launcher.process(save_to_file=True)
        if inform is None:
            raise ValueError('The Output is empty')
        print('\033[92mFALQON finished properly\033[0m')
    except Exception as ex:
        print('\033[91mSomething with Falqon went wrong\033[0m')
        print(ex)


def main():
    """ Main """
    test_ec()
    test_jssp()
    test_maxcut()
    test_qatm()
    test_falqon()
    print(f'\033[94mAll Data saved to {TESTING_DIR} folder\033[0m')


if __name__ == '__main__':
    main()
