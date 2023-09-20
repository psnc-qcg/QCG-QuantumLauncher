''' Example of how Quantum Launcher works'''

from problems import MaxCut
from qiskit_stuff.algorithms import QAOA2
from qiskit_stuff.backend import QiskitBackend
from qiskit_stuff.launcher import QiskitLauncher  # , from_pickle

# pr = QATM('exact', instance_name='RCP_3.txt', instance_path='data/qatm/')
# pr = JSSP(3, 'exact', instance_name='toy', optimization_problem=True)
pr = MaxCut(instance_name='default')
qaoa = QAOA2(p=3)
# qaoa = FALQON(delta_t=2, beta_0=2, n=2)
backend = QiskitBackend('local_simulator')
dir_ = 'test_data'
launcher = QiskitLauncher(pr, qaoa, backend)
launcher.set_dir(dir_)
inform = launcher.process('', save_to_file=True)
print(inform)
# print(from_pickle(launcher.res_path)) # This is the same but from pickle
# print(from_pickle("test_data/toy-3-decision-exact-local_simulator-falqon-10-0.03-0-4.596928704106529.pkl"))
