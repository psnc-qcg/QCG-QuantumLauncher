from quantum_launcher.launcher.profiling_launcher import ProfilingLauncher
from quantum_launcher import problems
from quantum_launcher.routines.dwave_routines import SimulatedAnnealingBackend, DwaveSolver

alg = DwaveSolver()
backend = SimulatedAnnealingBackend()
pr = problems.MaxCut(instance_name='default')
launcher = ProfilingLauncher(pr, alg, backend)
res = launcher.run()
# You should see at the console many informations about number of calls of each function, time and etc.
# Great tool if writing your own function to check if classical part is well optimized
print(res)
